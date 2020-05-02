#!/usr/bin/env python3

import os
import configparser
import logging


# TUTTE le chiavi del dizionario quì sotto DEVONO essere scritte in minuscolo, altrimenti falliscono i controlli più avanti
# (sì, lo so che potrei mettere un .lower(), ma anche no >:()
DEFAULT_CONFIG = {"BOT": {"databasefilepath": "socialFeedgram.sqlite3"},
                  "API": {"telegramkey": "",
                          "youtubev3key": ""}
                  }

# module_logger = logging.getLogger('telegram_bot.config')

# Structure Config
# [BOT]
# databasefilepath
# [API]
# telegramkey": ""
# "youtubev3key": ""


class Config:
    # Private:
    #   logger
    #   file_config
    #   state
    #   cofigurazione_dict
    # Public:
    #   dictionary
    #   status

    def __init__(self, fileConfig):

        self.__logger = logging.getLogger('telegram_bot.Config')
        self.__logger.info('Creating an instance of Config')

        self.__logger.info("################### CONFIGURATION LOADING #########################")

        self.__file_config = fileConfig
        self.__state = 1

        self.__logger.info("Controllo se esiste già il file di configurazione %s ...", fileConfig)
        if os.path.exists(self.__file_config):
            self.__logger.info("Il file %s esiste.", fileConfig)
            self.load_config()
        else:
            self.__logger.info("################### CONFIGURATION CREATION #########################")
            self.__cofigurazione_dict = DEFAULT_CONFIG
            self.save_config()
            self.load_config()

        self.__logger.info("################### CONFIGURATION COMPLETE #########################")

    def load_config(self):
        self.__logger.info("################### CONFIGURATION CONFIGURAZIONE #########################")
        configurazione = configparser.ConfigParser()
        try:
            configurazione.read(self.__file_config)
        except configparser.DuplicateOptionError:
            self.__logger.warning("Delle chiavi sono duplicate")
            self.__state = -2
            return
        except configparser.DuplicateSectionError:
            self.__logger.warning("Delle sezioni sono duplicate")
            self.__state = -3
            return
        # Converto l'oggetto configurazione in un dizionario
        self.__cofigurazione_dict = self.__as_dict(configurazione)
        self.__logger.info("Configurazione caricata.")
        if self.__check_config:
            self.__logger.info("Controllo conclusosi con successo.")
            # self._state = -4
            # return -4

    def save_config(self):
        self.__logger.info("################### SALVATAGGIO CONFIGURAZIONE #########################")
        self.__write_config(self.__file_config, self.__cofigurazione_dict)

    @property
    def dictionary(self):
        return self.__cofigurazione_dict

    @property
    def status(self):
        return self.__state

    # private function

    def __write_config(self, file_config, config):
        try:
            with open(file_config, 'w') as file_config_obj:
                configurazione = configparser.ConfigParser()
                for sezione in config:
                    configurazione[sezione] = config[sezione]

                configurazione.write(file_config_obj)
                self.__logger.info("File config impostato con sucesso")
        except OSError:
            self.__logger.warning(
                "Qualcosa è andato storto. Impossibile creare il file di configurazione.")
            raise

    @property
    def __check_config(self):
        self.__logger.info("################### CONTROLLO CONFIGURAZIONE#########################")
        self.__logger.info("Controllo che ci siano esattamente tutte le sezioni...")
        if not set(self.__cofigurazione_dict.keys()) == set(DEFAULT_CONFIG.keys()):
            self.__logger.warning("NON ci sono ESATTAMENTE tutte le sezioni.")
            self.__state = -5
            return False
        self.__logger.info("Ci sono tutte le sezioni.")

        self.__logger.info("Controllo che in ogni sezione ci siano esattamente tutte le chiavi...")

        for key, _ in DEFAULT_CONFIG.items():
            if not set(self.__cofigurazione_dict[key].keys()) == set(DEFAULT_CONFIG[key].keys()):
                self.__logger.warning("Nella sezione %s NON ci sono ESATTAMENTE tutte le chiavi!", str(key))
                self.__logger.warning("Miss the key(s): %s ", ''.join(list(set(self.__cofigurazione_dict[key].keys()) - set(DEFAULT_CONFIG[key].keys()))))
                self.__state = -6
                return False
            else:
                for key_section, value_section in self.__cofigurazione_dict[key].items():
                    if not str(value_section):
                        self.__logger.warning("Nella sezione %s l'opzione %s è VUOTA!", str(key), str(key_section))
                        self.__state = -7
                        return False

        self.__logger.info("Ci sono tutte le chiavi in ogni sezione.")

        self.__logger.info("Controllo che tutte le opzioni abbiano valori accettabli...")
        # In realtà bisognerebbe controllare se il path del database sia valido, ma vbb, lo farò un'altra volta
        # TODO: Implementare controllo per la validità del path del database
        self.__logger.info("Tutte le opzioni hanno valori accettabili.")

        return True

    @classmethod
    def __as_dict(cls, dicts):
        sections_dict = {}

        # get all defaults
        # defaults = dicts.defaults()
        # if defaults:
        #     temp_dict = {}
        #     for key in defaults.iterkeys():
        #         temp_dict[key] = defaults[key]
        #     sections_dict['default'] = temp_dict

        # get sections and iterate over each
        sections = dicts.sections()

        for section in sections:
            options = dicts.options(section)
            temp_dict = {}
            for option in options:
                temp_dict[option] = dicts.get(section, option)

            sections_dict[section] = temp_dict

        return sections_dict