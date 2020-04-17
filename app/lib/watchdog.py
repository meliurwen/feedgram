#!/usr/bin/env python3
import threading
import queue
import logging
# Libs
from app.lib.process_input import Processinput
from app.lib.database import MyDatabase
from app.lib.telegram import Telegram

CODA = queue.Queue()
CODA_TEMP = queue.Queue()


class Watchdog(threading.Thread):

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

        # Inizializazione dei social da fare solo ne caso del news_retreiver e del telegram_user_interface
        if self.mode == "telegram_user_interface" or self.mode == "news_retreiver":
            self.__db = MyDatabase(self.__conf_dict["BOT"]["databasefilepath"])

        if self.mode == "telegram_user_interface" or self.mode == "sender":
            self.__tel_interface = Telegram(self.__conf_dict["API"]["telegramkey"])  # <- cambiare config_dict

        if self.mode == "telegram_user_interface":
            self.__process_input = Processinput(self.__db)  # da dare in input i social

    def run(self):
        global CODA
        global CODA_TEMP

        if self.mode == "telegram_user_interface":
            last_update_id = None
            while self.still_run:
                updates = self.__tel_interface.get_updates(last_update_id)
                if len(updates["result"]) > 0:
                    last_update_id = self.__tel_interface.get_last_update_id(updates) + 1
                    CODA_TEMP.put(self.__process_input.process(updates))

        if self.mode == "elaborazione_code":
            self.__logger.info("Ciao sono elaborazione_code")
            delivering_list = []
            message_list = []
            # TODO: dare un'occhiata alla logica di questa roba qua sotto, c'è qualquadra che non cosa... :/
            while self.still_run:
                if CODA_TEMP.empty() and len(delivering_list) == 0:  # Se la coda è vuota aspetto che non diventi più vuota per aggiungere i messaggi in ddelivering_list
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
