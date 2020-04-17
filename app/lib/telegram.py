#!/usr/bin/env python3
import time
import json
import logging
from urllib.parse import quote_plus
from app.lib.utils import get_url


class Telegram:

    # Inizializzo le veriabili che servono per calibrare l'invio dei messaggi in modo che stiano dentro
    # i rate limits di Telegram (https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this).
    # Secondo la documentazione i valori da dare alle variabili sottostanti per rispettare i rate limits sono:
    # ONE_SECOND_TIME=1, SIXTY_SECONDS_TIME=60, MESSAGES_PER_SECOND=30, MESSAGES_PER_MINUTE_TO_SAME_CHAT=20
    ONE_SECOND_TIME = 1
    SIXTY_SECONDS_TIME = 60
    MESSAGES_PER_SECOND = 30
    MESSAGES_PER_MINUTE_TO_SAME_CHAT = 20

    # Imposta la url di Telegram col token (fa abbastanza schifo come metodo, fa funziona)
    def __init__(self, token):
        self.__logger = logging.getLogger('telegram_bot.Send_Recive')
        self.__logger.info('Creating an instance for telegram comunication')
        self.__tl_url = "https://api.telegram.org/bot{}/".format(token)

    # TODO: Mettere nel config il timeout in modo che possa esse impostato manualmente dall'utente
    def get_updates(self, offset=None):
        url = self.__tl_url + "getUpdates?timeout=60"
        if offset:
            url += "&offset={}".format(offset)
        return self.__get_json_from_url(url)

    def send_message(self, message):
        url = self.__tl_url
        if message["type"] == "sendMessage":
            if ("chat_id" in message) and ("text" in message):  # if is sendMessage, the dict MUST contain chat_id and text, otherwise is invalid and the mssage will not be sent
                url = url + "sendMessage?text={}&chat_id={}".format(self.__cut_and_encode_text(message["text"]), message["chat_id"])
                if "markdown" in message:
                    if (message["markdown"] == "HTML") or (message["markdown"] == "markdown"):
                        url = url + "&parse_mode={}".format(message["markdown"])
                if "reply_markup" in message:
                    url = url + "&reply_markup={}".format(quote_plus(json.dumps(message["reply_markup"])))
                # TODO: Finire di aggiungere le funzionalità della modalità sendMessage
            else:
                self.__logger.warning("Si sta cercando di mandare una URL sendMessage NON formattata correttamente!")
                self.__logger.warning(message)
        elif message["type"] == "answerCallbackQuery":
            if "callback_query_id" in message:
                url = url + "answerCallbackQuery?callback_query_id={}".format(message["callback_query_id"])
                if "text" in message:  # TODO: Make a 200 characters delimeter (see Telegram's APIs)
                    url = url + "&text={}".format(quote_plus(message["text"]))
                if "show_alert" in message:  # Forse mettere un controllo tipo isbool()? Boh...
                    url = url + "&show_alert={}".format(str(message["show_alert"]))
            else:
                self.__logger.warning("Si sta cercando di mandare una URL answerCallbackQuery NON formattata correttamente!")
                self.__logger.warning(message)
            # TODO: Finire di aggiungere le funzionalità della modalità answerCallbackQuery
        elif message["type"] == "editMessageText":
            if "text" in message:  # if ("text" in message) and ((("chat_id" in message) and ("message_id" in message)) or ("inline_message_id" in message)):
                if "inline_message_id" in message:
                    url = url + "editMessageText?text={}&inline_message_id={}".format(self.__cut_and_encode_text(message["text"]), message["inline_message_id"])
                else:
                    if ("chat_id" in message) and ("message_id" in message):
                        url = url + "editMessageText?text={}&chat_id={}&message_id={}".format(self.__cut_and_encode_text(message["text"]), message["chat_id"], message["message_id"])
                    else:
                        self.__logger.warning("Si sta cercando di mandare una URL editMessageText NON formattata correttamente!")
                if "markdown" in message:
                    url = url + "&parse_mode={}".format(message["markdown"])
                if "disable_web_page_preview" in message:  # Forse mettere un controllo tipo isbool()? Boh...
                    url = url + "&disable_web_page_preview={}".format(str(message["disable_web_page_preview"]))
                if "reply_markup" in message:
                    url = url + "&reply_markup={}".format(quote_plus(json.dumps(message["reply_markup"])))
            else:
                self.__logger.warning("Si sta cercando di mandare una URL editMessageText NON formattata correttamente!")
                self.__logger.warning(message)
            # TODO: Finire di aggiungere le funzionalità della modalità answerCallbackQuery
        else:
            self.__logger.warning("Si sta cercando di mandare una URL non valida o si sta cercando di usare una funzionalità ancora non supportata!")

        get_url(url)

    @classmethod
    def get_last_update_id(cls, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    # TODO: Introdurre il supporto per le answerCallbackQuery e più in generale a tutte le funzioni che NON prevedono il parametro chat_id
    # al momento, per renderle comaptibili glielo inserisco lo stesso, ma è una soluzione abbastanza triste.
    # Tutto quello che so di ufficiale riguardo i rate limits è quì: https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this
    # Se fossero un po' più precisi nelle specifiche mi farebbero un gran favore. >:(
    # def send_messages(self, coda, condizione):
    def send_messages(self, coda):

        last_one_second = {}
        last_sixty_seconds = {}
        buffer = []
        # Il buffer è una lista perchè necessario garantire una sorta di FIFO, nel senso che il primo messaggio inserito deve anche
        # tendenzialmente essere il primo ad uscire. Si dice "tendenzialmente" perché ci sono da rispettare anche altri vincoli.
        # La presenza di questi altri vincoli non intacca la garanzia che l'ordine di messaggi inviati per la stessa chat verrà rispettato.
        # I vincoli di cui si parla sono i rate limits imposti dalle API di Telegram (https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this).

        last_element_buffer_sent = False

        # ERROR manca condizione di uscita dal while
        # while True:

        # Controlla ad intervalli regolari se la lista non è vuota ed ad intervalli regolari relativamente lunghi "pulisce" i dizionari last_one_second e last_sixty_seconds
        h_tmp = 0
        while coda.empty():
            # print("Aspetto...")
            if h_tmp >= self.MESSAGES_PER_SECOND or h_tmp == 0:  # h_tmp==0 dovrebbe esserci solo la prima volta che si entra nel while
                tempo = time.time()
                last_sixty_seconds = self.__clean_sixty(last_sixty_seconds, tempo)
                last_one_second = self.__clean_one(last_one_second, tempo)
                # print("SIXTY")
                # print(len(last_sixty_seconds))
                # print("ONE")
                # print(len(last_one_second))
                h_tmp = 0
            h_tmp += 1
            # with condizione:
            #     condizione.wait(0.5)
            time.sleep(0.5)

        contatore_messaggi_inviati = 0

        tempo = time.time()
        timeout = tempo + self.ONE_SECOND_TIME
        flag_messaggi_ancora_da_inviare = True

        # Lo so che è brutto vedere il contatore j partire da 1, ma fidati, va bene così ;)
        j = 0
        i = 1
        while flag_messaggi_ancora_da_inviare:
            tempo = time.time()
            if tempo > timeout:
                j += 1
                # print("Ho sforato di: "+str(tempo-timeout))
                i = 1
                timeout = time.time() + self.ONE_SECOND_TIME

            k = 0
            flag_buffer = True
            last_element_buffer_sent = False

            # Controlla nel buffer se c'è un messaggio che si può inviare, e se c'è lo invia ed esce dal ciclo.
            buffer_length = len(buffer)
            while (k < buffer_length) and flag_buffer:
                # print(buffer)
                utente = buffer[k]["chat_id"]
                if utente in last_one_second:
                    if last_one_second[utente] > (tempo - self.ONE_SECOND_TIME):
                        is_more_one_sec_ago = False
                    else:
                        is_more_one_sec_ago = True
                else:
                    is_more_one_sec_ago = True
                if is_more_one_sec_ago:
                    if utente not in last_sixty_seconds:
                        last_sixty_seconds[utente] = []
                        last_sixty_seconds[utente].append(tempo)
                        self.send_message(buffer[k])
                        # print("Sending_buffer: "+str(buffer[k]))
                        last_element_buffer_sent = True
                        contatore_messaggi_inviati += 1
                        last_one_second[utente] = tempo
                        del buffer[k]
                        flag_buffer = False
                    else:
                        length_messages_sent_in_sixty = len(last_sixty_seconds[utente])
                        if length_messages_sent_in_sixty < self.MESSAGES_PER_MINUTE_TO_SAME_CHAT:
                            self.send_message(buffer[k])
                            # print("Sending_buffer: "+str(buffer[k]))
                            last_element_buffer_sent = True
                            contatore_messaggi_inviati += 1
                            last_sixty_seconds[utente].append(tempo)
                            last_one_second[utente] = tempo
                            del buffer[k]
                            flag_buffer = False
                        else:
                            contatore_messaggi_ultimo_minuto = 0
                            tmp = []
                            for delivery_time in last_sixty_seconds[utente]:
                                if delivery_time > (tempo - self.SIXTY_SECONDS_TIME):
                                    contatore_messaggi_ultimo_minuto += 1
                                    tmp.append(delivery_time)
                            if contatore_messaggi_ultimo_minuto < self.MESSAGES_PER_MINUTE_TO_SAME_CHAT:
                                self.send_message(buffer[k])
                                # print("Sending_buffer: "+str(buffer[k]))
                                last_element_buffer_sent = True
                                contatore_messaggi_inviati += 1
                                tmp.append(tempo)
                                last_sixty_seconds[utente] = tmp
                                last_one_second[utente] = tempo
                                del buffer[k]
                                flag_buffer = False
                k += 1

            # Teoricamente flag_coda=True solo o quando il buffer è vuoto o quando è stato fatto scorrete tutto senza che sia stato spedito il messaggio
            # Questo serve per capire se è necessario inviare un messaggio proveniente dalla coda o meno
            # N.B. Si ricorda che in un solo ciclo può essere inviato al più UN SOLO messaggio proveniente O dal buffer O dalla coda, O da nessuno dei due.
            flag_coda = bool(buffer_length == k and (not last_element_buffer_sent))

            # "Scorre" la coda (estraendo i dati dalla coda con un .get()) se c'è un messaggio che si può inviare, e se c'è lo invia ed esce dal ciclo.
            # I messaggi che controlla e che non si possono al momento inviare li sposta nel buffer.
            k = 0
            while (not coda.empty()) and flag_coda:
                messaggio = coda.get()
                # print(messaggio)
                utente = messaggio["chat_id"]
                if utente in last_one_second:
                    if last_one_second[utente] > (tempo - self.ONE_SECOND_TIME):
                        is_more_one_sec_ago = False
                    else:
                        is_more_one_sec_ago = True
                else:
                    is_more_one_sec_ago = True
                if is_more_one_sec_ago:
                    if utente not in last_sixty_seconds:
                        last_sixty_seconds[utente] = []
                        last_sixty_seconds[utente].append(tempo)
                        self.send_message(messaggio)
                        # print("Sending_queue: "+str(messaggio))
                        contatore_messaggi_inviati += 1
                        last_one_second[utente] = tempo
                        flag_coda = False
                    else:
                        length_messages_sent_in_sixty = len(last_sixty_seconds[utente])
                        if length_messages_sent_in_sixty < self.MESSAGES_PER_MINUTE_TO_SAME_CHAT:
                            self.send_message(messaggio)
                            # print("Sending_queue: "+str(messaggio))
                            contatore_messaggi_inviati += 1
                            last_sixty_seconds[utente].append(tempo)
                            last_one_second[utente] = tempo
                            flag_coda = False
                        else:
                            contatore_messaggi_ultimo_minuto = 0
                            tmp = []
                            for delivery_time in last_sixty_seconds[utente]:
                                if delivery_time > (tempo - self.SIXTY_SECONDS_TIME):
                                    contatore_messaggi_ultimo_minuto += 1
                                    tmp.append(delivery_time)
                            if contatore_messaggi_ultimo_minuto < self.MESSAGES_PER_MINUTE_TO_SAME_CHAT:
                                self.send_message(messaggio)
                                # print("Sending_queue: "+str(messaggio))
                                contatore_messaggi_inviati += 1
                                tmp.append(tempo)
                                last_sixty_seconds[utente] = tmp
                                last_one_second[utente] = tempo
                                flag_coda = False
                            else:
                                # print("over20->Buffer: "+str(messaggio))
                                buffer.append(messaggio)
                else:
                    # print("over1->Buffer: "+str(messaggio))
                    buffer.append(messaggio)
                k += 1

            # Decommenta quì sotto se vuoi aggiungere un ritardo forzato nell'invio tra un messaggio e l'altro
            # with condizione:
            #     condizione.wait(0.1)
            # In caso abbia inviato 30 messaggi prima del timeout, fermarsi ed aspettare che scata il timeout
            if not i < self.MESSAGES_PER_SECOND:
                tempo_sleep = timeout - time.time()
                # print("stop")
                # print("Ci ho messo: "+str(one_second_time - tempo_sleep)+"s")
                if tempo_sleep > 0:
                    # with condizione:
                    #     condizione.wait(tempo_sleep)
                    time.sleep(tempo_sleep)
            i += 1

            # Ad intervalli regolari "pulisci" last_one_second e last_sixty_seconds
            # Perchè col tempo tendono ad accumulare dati che non servono più
            if j == 180:
                tempo = time.time()
                last_one_second = self.__clean_one(last_one_second, tempo)
                last_sixty_seconds = self.__clean_sixty(last_sixty_seconds, tempo)
                # print(str(sixty_seconds_time) + " SECONDS")
                # for chiave, valore in last_sixty_seconds.items():
                #     print(str(chiave) + " = " + str(len(valore)))
                j = 0
                # print("ONE SECOND TEMP")
                # print(len(last_one_second))
                # print("BUFFER")
                # print(len(buffer))
                # print("MESSAGGI INVIATI")
                # print(contatore_messaggi_inviati)

            # Se la coda ed il buffer sono vuoti significa che non c'è più nulla da inviare, per cui si esce dal ciclo
            if coda.empty() and (len(buffer) == 0):
                flag_messaggi_ancora_da_inviare = False

    def __get_json_from_url(self, url):
        before_json_exception = False
        while True:
            content = get_url(url)
            try:
                jsn = json.loads(content)
                if before_json_exception:
                    before_json_exception = False
                    self.__logger.info("This time the the content retrived contains json! :D")
                return jsn
            except ValueError:
                before_json_exception = True
                self.__logger.exception("The content of the url is not json, now i print the content... %s ", content)
                time.sleep(1)
                self.__logger.info("Trying to retreive again the content from the url...")

    # If the message is too long, cut it and send it anyway without the parse mode active (in order to prevent the error of bad parsing).
    # Currently Telegram's API support a message of a maximum of 4096 UTF8 characters.
    # https://core.telegram.org/method/messages.sendMessage
    @classmethod
    def __cut_and_encode_text(cls, text):
        if len(text) > 4096:
            text = text[:4096]
        return quote_plus(text)

    def __clean_sixty(self, last_sixty_seconds, tempo):
        last_sixty_seconds_tmp = {}
        for utente, valore in last_sixty_seconds.items():
            tmp_utente = []
            for delivery_time in valore:
                if delivery_time > (tempo - self.SIXTY_SECONDS_TIME):
                    tmp_utente.append(delivery_time)
            if len(tmp_utente) > 0:
                last_sixty_seconds_tmp[utente] = tmp_utente
        last_sixty_seconds = last_sixty_seconds_tmp
        return last_sixty_seconds

    def __clean_one(self, last_one_second, tempo):
        last_one_second_tmp = {}
        for utente, delivery_time in last_one_second.items():
            if delivery_time > (tempo - self.ONE_SECOND_TIME):
                last_one_second_tmp[utente] = delivery_time
        last_one_second = last_one_second_tmp
        return last_one_second
