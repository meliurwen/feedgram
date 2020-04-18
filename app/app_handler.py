#!/usr/bin/env python3
import sys
import threading
import logging
import time
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
    condizione_compiler = threading.Condition()

    thread1 = Watchdog(1, "TelegramUserInterface", "telegram_user_interface", 0, None, config.dictionary, still_run)  # T.U.I. aka Telegram User Interface (I hope to be the first to have invented this **original** name 8-) )
    thread2 = Watchdog(1, "Sender", "sender", 0, condizione_sender, config.dictionary, still_run)
    thread3 = Watchdog(1, "ElaborazioneCode", "elaborazione_code", 0, None, None, still_run)
    thread4 = Watchdog(1, "NewsRetreiver", "news_retreiver", 600, condizione_compiler, config.dictionary, still_run)
    thread5 = Watchdog(1, "NewsCompiler", "news_compiler", 0, condizione_compiler, None, still_run)

    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread4.daemon = True
    thread5.daemon = True

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt Ctrl-C. Exiting...")
            sys.exit(0)
            raise
        # except:
            # report error and proceed
            # logger.info("Salve errore")


if __name__ == "__main__":
    main()
