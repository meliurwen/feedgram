#!/usr/bin/env python3
import threading
import queue
import logging
import time
import json
# Libs
from feedgram.lib.process_input import Processinput
from feedgram.lib.database import MyDatabase
from feedgram.lib.telegram import Telegram
from feedgram.social.instagram import Instagram

CODA = queue.Queue()
CODA_TEMP = queue.Queue()
SUBSCRIPTIONS_DICT = {}
DATAS_SOCIAL = []


class Watchdog(threading.Thread):

    def news_retreiver_subthread(self, social_type, subscriptions, coda_social):
        if social_type == "instagram":
            datas = self.__instagram_interface.get_feed(subscriptions)
        else:
            datas = []
        if datas:
            coda_social.put(datas)

    def __init__(self, thread_id, name, mode, delay, condizione, conf_dict, still_run):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.mode = mode
        self.delay = delay
        self.condizione = condizione
        self.still_run = still_run
        self.__conf_dict = conf_dict

        self.__logger = logging.getLogger("telegram_bot.WD.{}".format(self.name))

        # inizializazione della variabile database solo nei thread necessari
        if self.mode == "telegram_user_interface" or self.mode == "news_retreiver" or self.mode == "news_compiler" or self.mode == "pause_manger":
            self.__db = MyDatabase(self.__conf_dict["BOT"]["databasefilepath"])

        # Inizializazione dei social da fare solo ne caso del news_retreiver e del telegram_user_interface
        if self.mode == "telegram_user_interface" or self.mode == "news_retreiver":
            self.__instagram_interface = Instagram()

        if self.mode == "telegram_user_interface" or self.mode == "sender":
            self.__tel_interface = Telegram(self.__conf_dict["API"]["telegramkey"])  # <- cambiare config_dict

        if self.mode == "telegram_user_interface":
            self.__process_input = Processinput(self.__db, [self.__instagram_interface])  # da dare in input i social

    def run(self):
        global CODA
        global CODA_TEMP
        global SUBSCRIPTIONS_DICT
        global DATAS_SOCIAL

        if self.mode == "telegram_user_interface":
            last_update_id = None
            while self.still_run:
                updates = self.__tel_interface.get_updates(last_update_id)
                if len(updates["result"]) > 0:
                    last_update_id = self.__tel_interface.get_last_update_id(updates) + 1
                    CODA_TEMP.put(self.__process_input.process(updates))

        if self.mode == "elaborazione_code":
            delivering_list = []
            message_list = []
            # TODO: dare un'occhiata alla logica di questa roba qua sotto, c'è qualquadra che non cosa... :/
            while self.still_run:
                if CODA_TEMP.empty() and len(delivering_list) == 0:  # Se la coda è vuota aspetto che non diventi più vuota per aggiungere i messaggi in delivering_list
                    message_list = CODA_TEMP.get()
                    delivering_list = delivering_list + message_list
                    # print("Ho appena ricevuto dei messaggini nuovi da spedirez! ^_^")
                else:
                    if not CODA_TEMP.empty():  # Se mentre la coda non è vuota (ergo, mentre sis ta svuotando) si aggiunge
                        message_list = CODA_TEMP.get()
                        delivering_list = delivering_list + message_list
                        # print("Ho appena ricevuto dei messaggini nuovi da spedire! ^_^")
                    if len(delivering_list) > 0:
                        message = delivering_list.pop(0)
                        CODA.put(message)

        if self.mode == "sender":
            while self.still_run:
                self.__tel_interface.send_messages(CODA)

        if self.mode == "news_compiler":
            while self.still_run:
                with self.condizione:
                    self.condizione.wait()

                # TODO: Migliorare questa parte mettendo un tipo di messaggio a seconda del social
                messages_socials = []
                if SUBSCRIPTIONS_DICT:
                    for data_social in DATAS_SOCIAL:
                        if data_social["social"] in SUBSCRIPTIONS_DICT["subscriptions"]:
                            if data_social["internal_id"] in SUBSCRIPTIONS_DICT["subscriptions"][data_social["social"]]:
                                for user in SUBSCRIPTIONS_DICT["subscriptions"][data_social["social"]][data_social["internal_id"]]:

                                    # Controllo la data di scadenza della sottoscrizione
                                    # Se è scaduta resetto allo stato 0 (di default)
                                    if user['expire'] <= time.time():
                                        user['state'] = 0

                                    message_title = data_social["title"]
                                    if data_social["type"] == "new_post":
                                        text = "<b>[" + data_social["social"].upper() + "]</b>\nUser: <i>" + message_title + "</i>\nLink: " + data_social["post_url"]
                                    elif data_social["type"] == "now_private":
                                        text = "<b>⚠️ALERT⚠️</b>\n<b>[" + data_social["social"].upper() + "]</b>\nThis account now is <b>private</b>, that means that you'll no longer receive updates until its owner decides to change it back to <i>public</i>.\nUser: <i>" + message_title + "</i>\nLink: " + data_social["post_url"]
                                    elif data_social["type"] == "deleted_account":
                                        text = "<b>⚠️ALERT⚠️</b>\n<b>[" + data_social["social"].upper() + "]</b>\nThis account has been <b>deleted</b> and also automatically removed from your <i>Follow List</i>.\nUser: <i>" + message_title + "</i>\nLink: " + data_social["post_url"]
                                    else:
                                        text = "<b>⚠️UNKNOWN MESSAGE⚠️</b>\nPlease report it to the creator of this bot."

                                    # Se l'utente ha impostato lo stato 2 (muted) alla sottoscrizione, allora non riceve nessun messaggio a riguardo
                                    if user['state'] != 2:
                                        message = {'type': 'sendMessage',
                                                   'text': text,
                                                   'chat_id': str(user['user_id']),
                                                   'disable_notification': bool(user['state'] == 1),
                                                   'markdown': 'HTML'}
                                        if user['state'] != 3:
                                            messages_socials.append(message)
                                        else:
                                            self.__db.archive_message(user['user_id'], user["social_id"], data_social["post_date"], message)

                self.__logger.info("Messaggi da inviare: %s ", len(messages_socials))
                if len(messages_socials) > 0:
                    CODA_TEMP.put(messages_socials)
                    self.__logger.info("Messaggi messi in coda di spedizione.")

        if self.mode == "news_retreiver":
            # global condizione_compiler
            while self.still_run:

                self.__db.clean_expired_state()  # TODO: Estremamente poco efficiente e costosa, assolutamente da migliorare
                self.__db.clean_dead_subscriptions()  # Pulisco al tabella "socials" rimuovendo gli account ai quali nessuno è più iscritto
                SUBSCRIPTIONS_DICT = self.__db.create_dict_of_user_ids_and_socials  # Creo un dizionario di tutte le iscrizioni degli utenti

                # Creo un dizionario con tutti gli account a cui gli utenti sono iscritti
                # socials_accounts_dict = {}
                # for social_key in SUBSCRIPTIONS_DICT.keys():
                #    socials_accounts_dict[social_key] = list(SUBSCRIPTIONS_DICT[social_key].keys())
                # ### ##
                # print(SUBSCRIPTIONS_DICT["instagram"])

                if SUBSCRIPTIONS_DICT:  # se il dizionario non è vuoto (la tabella "socials" non è vuota, ergo, almeno un utente è iscritto a qualcosa)

                    # In caso nessuno sia iscritto al social aggiungo un array ed un dizionario vuoti
                    num_subs_threads = {"subscriptions": {"total": 0}, "threads": {"total": 0}}
                    for element in ["instagram"]:  # TODO: Portare fuori questa lista, che indica i servizi che sono abilitati per il retrieving delle informazioni
                        if element not in SUBSCRIPTIONS_DICT["subscriptions"]:
                            SUBSCRIPTIONS_DICT["subscriptions"][element] = {}
                        if element not in SUBSCRIPTIONS_DICT["social_accounts"]:
                            SUBSCRIPTIONS_DICT["social_accounts"][element] = []
                        num_subs_threads["subscriptions"][element] = len(SUBSCRIPTIONS_DICT["social_accounts"][element])
                        num_subs_threads["subscriptions"]["total"] = num_subs_threads["subscriptions"]["total"] + num_subs_threads["subscriptions"][element]
                        num_subs_threads["threads"][element] = 0

                    max_subscriptions_per_thread = 10  # Ricorda, deve essere assolutamente > 0
                    self.__logger.info("Account massimi per thread: %s ", str(max_subscriptions_per_thread))
                    for element in num_subs_threads["threads"]:
                        if element != "total":
                            num_subs_threads["threads"][element] = num_subs_threads["subscriptions"][element] // max_subscriptions_per_thread
                            if num_subs_threads["subscriptions"][element] % max_subscriptions_per_thread:
                                num_subs_threads["threads"][element] += 1
                            num_subs_threads["threads"]["total"] = num_subs_threads["threads"]["total"] + num_subs_threads["threads"][element]
                    self.__logger.info(num_subs_threads)

                    # Crea nuovi thread
                    coda_social = queue.Queue()
                    threads = []
                    thread_id = 0
                    for social_name, value in num_subs_threads["threads"].items():
                        if social_name != "total":
                            head = 0
                            if max_subscriptions_per_thread > num_subs_threads["subscriptions"][social_name]:
                                tail = num_subs_threads["subscriptions"][social_name]
                            else:
                                tail = max_subscriptions_per_thread
                            for _ in range(0, value):

                                thread = threading.Thread(target=Watchdog.news_retreiver_subthread,
                                                          name="{}-{}".format(social_name, thread_id),
                                                          args=(self, social_name, SUBSCRIPTIONS_DICT["social_accounts"][social_name][head:tail], coda_social))
                                thread.start()
                                threads.append(thread)
                                thread_id += 1
                                head = tail
                                tail = tail + max_subscriptions_per_thread
                                if tail > num_subs_threads["subscriptions"][social_name]:
                                    tail = num_subs_threads["subscriptions"][social_name]

                    # Aspetta che tutti i thread finiscano
                    for tred in threads:
                        tred.join()

                    # Unisce i dati ricevuti dai thread
                    DATAS_SOCIAL = []
                    datas_queries = {'update': [], 'delete': []}
                    while not coda_social.empty():
                        messaggio = coda_social.get()
                        DATAS_SOCIAL = DATAS_SOCIAL + messaggio["messages"]
                        datas_queries["update"] = datas_queries["update"] + messaggio["queries"]["update"]
                        datas_queries["delete"] = datas_queries["delete"] + messaggio["queries"]["delete"]

                    # Ordina i messaggi in ordine cronologico
                    if len(DATAS_SOCIAL) > 1:
                        DATAS_SOCIAL = sorted(DATAS_SOCIAL, key=lambda k: k['post_date'], reverse=False)

                    # Credo che sarebbe meglio spostare questo coso qua sotto dopo la riga: print("Controllerò di nuovo tra 10 minuti.") o nel thread "News_compiler"
                    # Investigare a riguardo
                    self.__db.process_messages_queries(datas_queries)

                self.condizione.acquire()
                self.condizione.notify_all()
                self.condizione.release()
                self.__logger.info("Controllerò di nuovo tra %s minuti.", self.delay // 60)

                with self.condizione:
                    self.condizione.wait(self.delay)

        if self.mode == "pause_manger":
            while self.still_run:
                messages = self.__db.detect_stop_pause_or_expired
                # for mess in message:
                # mess[0] -> message_id
                # mess[1] -> user_id
                # mess[2] -> social_id
                # mess[3] -> update_date
                # mess[4] -> message
                # mess[5] -> status
                # mess[6] -> expire_date

                messages_list = []  # lista dei messaggi che dovranno essere inviati
                trash_list = []  # lista che conterrà gli id dei messaggi da rimuovere
                if messages:
                    self.__logger.info("Ho trovato %s messaggi archivati da gestire", len(messages))
                    for mess in messages:
                        # Per ogni messaggio andremo ad analizzare lo stato.
                        # In ogni caso i messaggi selezionati dovranno essere rimossi dal database.
                        trash_list.append(mess[0])  # aggungo il messaggio nella lista di quelli da rimuovere

                        # Se lo stato è 2 (stop) non verrà inviato nessun messaggio
                        if mess[5] != 2:
                            # se lo stato è:
                            # 0 (normale) -> cambio di stato in 0
                            # 1 (mute) -> cambio di stato in 1
                            # 3 (pausa) -> l'expire_date è scaduto
                            # inviamo normalmente il messaggio

                            temp = json.loads(mess[4])  # oggettizzo il json

                            if mess[5] == 1:
                                # stato di mute, il messaggio dovrà essere inviato silenziosamente
                                temp['disable_notification'] = True

                            messages_list.append(temp)  # append del messaggio alla lista

                self.__db.remove_messages(trash_list)

                self.__logger.info("Messaggi da inviare: %s ", len(messages_list))
                if len(messages_list) > 0:
                    CODA_TEMP.put(messages_list)
                    self.__logger.info("Messaggi messi in coda di spedizione.")

                time.sleep(self.delay)
