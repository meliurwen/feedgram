#!/usr/bin/env python3
import sys
import threading
import logging
# lib
from app.lib.config import Config
from app.lib.database import MyDatabase
from app.lib.watchdog import Watchdog


FILE_CONFIG = "config.ini"


def setup_loger():
    # create logger with 'spam_application'
    logger = logging.getLogger('telegram_bot')
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    # fh = logging.FileHandler('spam.log')
    # fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    cha = logging.StreamHandler()
    cha.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

    # fh.setFormatter(formatter)
    cha.setFormatter(formatter)
    # add the handlers to the logger
    # logger.addHandler(fh)
    logger.addHandler(cha)
    return logger


FILE_CONFIG = "config.ini"


def main():
    # Inizializzo il logger per la stampa dei messaggi
    logger = setup_loger()

    logger.info("Benvenuto nel programma")

    # Instanzio l'ogetto contentente la configurazione
    config = Config(FILE_CONFIG)

    # Verifico che lo stato dell'oggetto sia coretto altrimenti chiudo il programma
    if config.status <= 0:
        logger.error("Arresto del programma...")
        sys.exit(0)

    # Instanzio l'ogetto del database data la configurazione caricata
    database = MyDatabase(config.dictionary["BOT"]["databasefilepath"])

    # Verifico che lo stato del database sia valido altrimenti chiudo il programma
    if database.status <= 0:
        logger.error("Arresto del programma...")
        sys.exit(0)

    still_run = True
    condizione_sender = threading.Condition()

    thread1 = Watchdog(1, "TelegramUserInterface", "telegram_user_interface", 0, None, config.dictionary, still_run)  # T.U.I. aka Telegram User Interface (I hope to be the first to have invented this **original** name 8-) )
    thread2 = Watchdog(1, "Sender", "sender", 0, condizione_sender, config.dictionary, still_run)
    thread3 = Watchdog(1, "ElaborazioneCode", "elaborazione_code", 0, None, None, still_run)

    thread1.start()
    thread2.start()
    thread3.start()


if __name__ == "__main__":
    main()
