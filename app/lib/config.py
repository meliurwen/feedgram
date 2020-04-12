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


class Config:
    # [BOT]
    # databasefilepath
    # [API]
    # telegramkey": ""
    # "youtubev3key": ""

    def __init__(self, fileConfig):

        self.logger = logging.getLogger('telegram_bot.Config')
        self.logger.info('Creating an instance of Config')

        self.logger.info("################### CONFIGURATION LOADING #########################")

        self._file_config = fileConfig
        self._state = 1

        self.logger.info("Controllo se esiste già il file di configurazione %s ...", fileConfig)
        if os.path.exists(self._file_config):
            self.logger.info("Il file %s esiste.", fileConfig)
            self.load_config()
        else:
            self.logger.info("################### CONFIGURATION CREATION #########################")
            self.__cofigurazione_dict = DEFAULT_CONFIG
            self._save_config()
            self.load_config()

        self.logger.info("################### CONFIGURATION COMPLETE #########################")

    def load_config(self):
        self.logger.info("################### CONFIGURATION CONFIGURAZIONE #########################")
        configurazione = configparser.ConfigParser()
        try:
            configurazione.read(self._file_config)
        except configparser.DuplicateOptionError:
            self.logger.warning("Delle chiavi sono duplicate")
            self._state = -2
            # return -2
        except configparser.DuplicateSectionError:
            self.logger.warning("Delle sezioni sono duplicate")
            self._state = -3
            # return -3
        # Converto l'oggetto configurazione in un dizionario
        self.__cofigurazione_dict = self._as_dict(configurazione)
        self.logger.info("Configurazione caricata.")
        if self._check_config:
            self.logger.info("Controllo conclusosi con successo.")
            # self._state = -4
            # return -4

    def _save_config(self):
        self.logger.info("################### SALVATAGGIO CONFIGURAZIONE #########################")
        self._write_config(self._file_config, self.__cofigurazione_dict)

    @property
    def dictionary(self):
        return self.__cofigurazione_dict

    @property
    def status(self):
        return self._state

    # private function

    def _write_config(self, file_config, config):
        try:
            with open(file_config, 'w') as file_config_obj:
                configurazione = configparser.ConfigParser()
                for sezione in config:
                    configurazione[sezione] = config[sezione]

                configurazione.write(file_config_obj)
                self.logger.info("File config impostato con sucesso")
        except OSError:
            self.logger.warning(
                "Qualcosa è andato storto. Impossibile creare il file di configurazione.")

    @property
    def _check_config(self):
        self.logger.info("################### CONTROLLO CONFIGURAZIONE#########################")
        self.logger.info("Controllo che ci siano esattamente tutte le sezioni...")
        if not set(self.__cofigurazione_dict.keys()) == set(DEFAULT_CONFIG.keys()):
            self.logger.warning("NON ci sono ESATTAMENTE tutte le sezioni.")
            self._state = -5
            return False
        self.logger.info("Ci sono tutte le sezioni.")

        self.logger.info("Controllo che in ogni sezione ci siano esattamente tutte le chiavi...")

        for key, _ in DEFAULT_CONFIG.items():
            if not set(self.__cofigurazione_dict[key].keys()) == set(DEFAULT_CONFIG[key].keys()):
                self.logger.warning("Nella sezione %s NON ci sono ESATTAMENTE tutte le chiavi!", str(key))
                self.logger.warning("Miss the key(s): %s ", ''.join(list(set(self.__cofigurazione_dict[key].keys()) - set(DEFAULT_CONFIG[key].keys()))))
                self._state = -6
            else:
                for key_section, value_section in self.__cofigurazione_dict[key].items():
                    if not str(value_section):
                        self.logger.warning("Nella sezione %s l'opzione %s è VUOTA!", str(key), str(key_section))
                        self._state = -7
            return False

        self.logger.info("Ci sono tutte le chiavi in ogni sezione.")

        self.logger.info("Controllo che tutte le opzioni abbiano valori accettabli...")
        # In realtà bisognerebbe controllare se il path del database sia valido, ma vbb, lo farò un'altra volta
        # TODO: Implementare controllo per la validità del path del database
        self.logger.info("Tutte le opzioni hanno valori accettabili.")

        return True

    @classmethod
    def _as_dict(cls, dicts):
        sections_dict = {}

        # get all defaults
        defaults = dicts.defaults()
        if defaults:
            temp_dict = {}
            for key in defaults.iterkeys():
                temp_dict[key] = defaults[key]

            sections_dict['default'] = temp_dict

        # get sections and iterate over each
        sections = dicts.sections()

        for section in sections:
            options = dicts.options(section)
            temp_dict = {}
            for option in options:
                temp_dict[option] = dicts.get(section, option)

            sections_dict[section] = temp_dict

        return sections_dict
