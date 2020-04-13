import os.path
import sqlite3
import time
import logging


class MyDatabase:

    def __init__(self, dbPath):
        self.__logger = logging.getLogger('telegram_bot.database')
        self.__logger.info('Creating an instance of database')

        self.__logger.info("################### INIZIALIZAZIONE CONFIGURAZIONE #########################")

        self.__tables = ['admins', 'users', 'registrations', 'socials']
        self.__dbpath = dbPath
        self.__state = 1

        if self.__db_exist:
            if not self.__tables_exist:
                self.__logger.warning("Database presente ma mancano delle tabelle.")
                self.__state = -1
            else:
                self.__logger.info("Tutte le tabelle sono presenti.")
        else:
            self.__logger.info("Creo il file SQLITE3 e le tabelle...")
            self.__db_creation()

    @property
    def status(self):
        return self.__state

    @property
    def __db_exist(self):

        self.__logger.info("Versione modulo: %s", sqlite3.version)
        self.__logger.info("Versione libreria SQLite: %s", sqlite3.sqlite_version)
        self.__logger.info("Nome database SQLite: %s", self.__dbpath)

        self.__logger.info("Controllo se esiste già un file chiamato %s ...", self.__dbpath)
        if os.path.isfile(self.__dbpath):
            self.__logger.info("Il file ESISTE")
            return True
        else:
            self.__logger.info("Il file NON esiste")
            return False

    @property
    def __tables_exist(self):
        for tabella in self.__tables:
            if not self.__table_exist(tabella):
                return False
        return True

    def __table_exist(self, table):
        self.__logger.debug("Controllo se esiste la tabella %s ...", table)
        counter, _ = self.__query(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?;", table)
        if counter[0] == 0:
            print("Tabella " + str(table) + " assente!")
            return False
        else:
            return True

    def __db_creation(self):
        self.__logger.info("Creo il file SQLITE3 e le tabelle...")
        self.__query("CREATE TABLE `admins` (`user_id` INTEGER NOT NULL, `is_creator` INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(`user_id`));")
        self.__query("CREATE TABLE `users` (`user_id` INTEGER NOT NULL, `username` TEXT, `chat_id` INTEGER NOT NULL, `notifications` INTEGER NOT NULL DEFAULT 1, `max_registrations` INTEGER NOT NULL DEFAULT 10, `subscription_time` INTEGER NOT NULL, PRIMARY KEY(`user_id`));")
        self.__query("CREATE TABLE `registrations` (`user_id` INTEGER NOT NULL, `social_id` INTEGER NOT NULL, PRIMARY KEY(`user_id`,`social_id`), FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(`social_id`) REFERENCES `socials`(`social_id`) ON DELETE CASCADE ON UPDATE CASCADE);")
        self.__query("CREATE TABLE `socials` (`social_id` INTEGER NOT NULL, `social` TEXT NOT NULL, `username` TEXT NOT NULL, `title` TEXT NOT NULL, `internal_id` TEXT NOT NULL, `retreive_time` INTEGER NOT NULL, `status` TEXT NOT NULL DEFAULT 'public', PRIMARY KEY(`social_id`));")
        self.__logger.info("Database e tabelle create con successo")

    def __query(self, query, *args, foreign=False, fetch=1):

        con = None
        data = None
        rowcount = 0

        self.__logger.debug('Executing %s with args %s with foreign_keys=%s.', query, args, foreign)
        try:
            con = sqlite3.connect(self.__dbpath)
            cur = con.cursor()
            if foreign:
                cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(query, tuple(args))

            if fetch > 1:
                data = cur.fetchmany(fetch)
            elif fetch == 0:
                data = cur.fetchall()
            else:
                data = cur.fetchone()

            rowcount = cur.rowcount

            if not data:
                con.commit()
        except sqlite3.Error as err:
            self.__logger.error("Database error: %s", err)
        except Exception as err:
            self.__logger.error("Exception in _query: %s", err)
        finally:
            if con:
                con.close()
        return data, rowcount
