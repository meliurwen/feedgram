import os.path
import sqlite3
import logging
import time


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
        except sqlite3.Warning as err:
            self.__logger.error("Exception in query: %s", err)
        finally:
            if con:
                con.close()
        return data, rowcount

    def check_utente(self, user_id):
        query = ("SELECT 1 FROM users WHERE user_id = ?;")
        res, _ = self.__query(query, user_id)
        return bool(res)

    def unsubscribe_user(self, user_id):
        self.__query("DELETE FROM users WHERE user_id = ?;",
                     user_id, foreign=True)

    def subscribe_user(self, user_id, username, chat_id, notifications, max_registrations):
        self.__query("INSERT INTO users (user_id, username, chat_id, notifications, max_registrations, subscription_time) VALUES (?, ?, ?, ?, ?, ?);",
                     user_id, username, chat_id, notifications, max_registrations, int(time.time()))

    def check_number_subscribtions(self, user_id):
        res, _ = self.__query(
            "SELECT users.user_id, (SELECT count(user_id) AS registrations FROM registrations WHERE user_id = ?) AS actual_registrations, users.max_registrations FROM users where users.user_id = ?;", user_id, user_id)
        value = res
        value = {
            "user_id": value[0], "actual_registrations": value[1], "max_registrations": value[2]}
        return value

    def get_first_social_id_from_internal_user_social_and_if_present_subscribe(self, user_id, sub, exists):
        tmp_list = []

        if sub["internal_id"]:
            tmp_list, _ = self.__query(
                "SELECT social_id, username, title, status FROM socials WHERE social = ? AND internal_id = ?;", sub["social"], sub["internal_id"])
        elif sub["username"]:
            tmp_list, _ = self.__query(
                "SELECT social_id, internal_id, title, status FROM socials WHERE social = ? AND username = ?;", sub["social"], sub["username"])
        else:
            sub["subStatus"] = "internalId_or_username_not_present"
            return sub  # Errore, internal_id od username non presenti

        if tmp_list:
            # if tmp_list is not none
            # Ottengo il social_id ed i restanti dati mancanti
            sub["social_id"] = tmp_list[0]
            if not exists:
                sub["status"] = tmp_list[3]
                sub["title"] = tmp_list[2]
                if sub["internal_id"]:
                    sub["username"] = tmp_list[1]
                elif sub["username"]:
                    sub["internal_id"] = tmp_list[1]
                else:
                    return -1  # Errore, è praticamente impossibile arrivare in questo else
            else:
                pass
        else:
            # if tmp_list is none
            # La ricerca ha dato riscontro negativo, non si trova nel database
            if exists:
                self.__query("INSERT INTO socials (social, username, title, internal_id, retreive_time) VALUES (?, ?, ?, ?, ?);",
                             sub["social"], sub["username"], sub["title"], sub["internal_id"], int(time.time()))
                res, _ = self.__query(
                    "SELECT social_id FROM socials WHERE social = ? AND internal_id = ?;", sub["social"], sub["internal_id"])
                sub["social_id"] = res[0]

                self.__query(
                    "INSERT INTO registrations (user_id, social_id) VALUES (?, ?);", user_id, sub["social_id"])
                sub["subStatus"] = "CreatedSocialAccAndSubscribed"
                return sub
            else:
                sub["subStatus"] = "notInDatabase"
                return sub

        # Se si è arrivati a questo punto significa che è presente nel database, ora bisogna controllare se l'utente è iscritto
        res, _ = self.__query(
            "SELECT 1 FROM registrations WHERE user_id = ? AND social_id = ?;", user_id, sub["social_id"])
        # None se non c'è la relazione quindi devi sottoscrivere
        if res:
            # utente già inscritto
            sub["subStatus"] = "AlreadySubscribed"
        else:
            # utente non inscritto
            # Utente non ancora iscritto, ora procedo ad iscriverlo
            sub["subStatus"] = "JustSubscribed"
            self.__query(
                "INSERT INTO registrations (user_id, social_id) VALUES (?, ?);", user_id, sub["social_id"])

        return sub

    @property
    def create_dict_of_user_ids_and_socials(self):
        res, _ = self.__query("SELECT registrations.user_id, socials.social, socials.internal_id, socials.username, socials.title, socials.retreive_time, socials.status FROM registrations, socials WHERE registrations.social_id = socials.social_id;", fetch=0)
        socials_accounts_dict = {"social_accounts": {}, "subscriptions": {}}
        if res:
            for row in res:
                if row[1] not in socials_accounts_dict["subscriptions"]:
                    socials_accounts_dict["subscriptions"][row[1]] = {}
                    socials_accounts_dict["social_accounts"][row[1]] = []
                if row[2] not in socials_accounts_dict["subscriptions"][row[1]]:
                    socials_accounts_dict["subscriptions"][row[1]][row[2]] = []
                    account_temp = {}
                    account_temp["internal_id"] = str(row[2])
                    account_temp["username"] = str(row[3])
                    account_temp["title"] = str(row[4])
                    account_temp["retreive_time"] = str(row[5])
                    account_temp["status"] = str(row[6])
                    socials_accounts_dict["social_accounts"][row[1]].append(account_temp)
                socials_accounts_dict["subscriptions"][row[1]][row[2]].append(str(row[0]))
        return socials_accounts_dict

    def clean_dead_subscriptions(self):
        _, rowcount = self.__query(
            "DELETE FROM socials WHERE social_id IN (SELECT social_id FROM socials WHERE social_id NOT IN (SELECT social_id FROM registrations));")
        self.__logger.info(
            "Account senza iscrizioni rimossi: %s ", rowcount)

    def process_messages_queries(self, messages_queries):
        for query in messages_queries["update"]:
            if query["type"] == "retreive_time":
                self.__query("UPDATE socials SET retreive_time = ? WHERE social = ? AND internal_id = ?;",
                             query["retreive_time"], query["social"], query["internal_id"], foreign=True)
            elif query["type"] == "status":
                self.__query("UPDATE socials SET status = ? WHERE social = ? AND internal_id = ?;",
                             query["status"], query["social"], query["internal_id"], foreign=True)
        for query in messages_queries["delete"]:
            if query["type"] == "socialAccount":
                self.__query("DELETE FROM registrations WHERE registrations.social_id = (SELECT socials.social_id FROM socials WHERE socials.social = ? AND socials.internal_id = ?);",
                             query["social"], query["internal_id"], foreign=True)
                self.__query("DELETE FROM socials WHERE socials.social = ? AND socials.internal_id = ?;",
                             query["social"], query["internal_id"], foreign=True)
