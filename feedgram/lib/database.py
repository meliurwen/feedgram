import os.path
import sqlite3
import logging
import time
import json


class MyDatabase:

    def __init__(self, dbPath):
        self.__logger = logging.getLogger('telegram_bot.database')
        self.__logger.info('Class instance for communication with a SQLite3 database initiated.')

        self.__tables = ['admins', 'users', 'registrations', 'socials', 'messages', 'jail']
        self.__dbpath = dbPath
        self.__state = 1
        self.__max_role_lvl = 1

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

        self.__logger.info("Module version: %s", sqlite3.version)
        self.__logger.info("Library version: %s", sqlite3.sqlite_version)
        self.__logger.info("Database name: %s", self.__dbpath)

        self.__logger.info("Checking if already a file named '%s' exists...", self.__dbpath)
        is_file = os.path.isfile(self.__dbpath)
        if is_file:
            self.__logger.info("The file exists.")
        else:
            self.__logger.info("The file does not exist.")
        return is_file

    @property
    def __tables_exist(self):
        for tabella in self.__tables:
            if not self.__table_exist(tabella):
                return False
        return True

    def __table_exist(self, table):
        self.__logger.debug("Checking if the table '%s' exists...", table)
        counter, _ = self.__query(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?;", table)
        is_tab = bool(counter[0])
        if not is_tab:
            self.__logger.error("Tabella %s assente!", table)
        return is_tab

    def __db_creation(self):
        self.__logger.info("Creating the SQLite3 file and tables...")
        self.__query("CREATE TABLE `admins` (`user_id` INTEGER NOT NULL, `role` INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(`user_id`));")
        self.__query("CREATE TABLE `users` (`user_id` INTEGER NOT NULL, `username` TEXT, `chat_id` INTEGER NOT NULL, `max_registrations` INTEGER NOT NULL DEFAULT 10, `subscription_time` INTEGER NOT NULL, PRIMARY KEY(`user_id`));")
        self.__query("CREATE TABLE `registrations` (`user_id` INTEGER NOT NULL, `social_id` INTEGER NOT NULL, `status` INTEGER NOT NULL DEFAULT 0, `expire_date` INTEGER NOT NULL DEFAULT -1, `category` TEXT NOT NULL DEFAULT 'default', PRIMARY KEY(`user_id`,`social_id`), FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY(`social_id`) REFERENCES `socials`(`social_id`) ON DELETE CASCADE ON UPDATE CASCADE);")
        self.__query("CREATE TABLE `socials` (`social_id` INTEGER NOT NULL, `social` TEXT NOT NULL, `username` TEXT NOT NULL, `title` TEXT NOT NULL, `internal_id` TEXT NOT NULL, `retreive_time` INTEGER NOT NULL, `status` TEXT NOT NULL DEFAULT 'public', PRIMARY KEY(`social_id`));")
        self.__query("CREATE TABLE `messages` ( `message_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,`user_id` INTEGER NOT NULL, `social_id` INTEGER NOT NULL, `update_date` INTEGER NOT NULL, `message` TEXT NOT NULL, FOREIGN KEY(`user_id`,`social_id`) REFERENCES `registrations`(`user_id`,`social_id`) ON DELETE CASCADE ON UPDATE CASCADE );")
        self.__query("CREATE TABLE `jail` (`user_id` INTEGER NOT NULL, `expire_time` INTEGER NOT NULL, PRIMARY KEY(`user_id`));")
        self.__logger.info("Database and tables created successfully.")

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
        _, rows = self.__query("DELETE FROM users WHERE user_id = ?;",
                               user_id, foreign=True)
        return bool(rows)

    def subscribe_user(self, user_id, username, chat_id, max_registrations):
        self.__query("INSERT INTO users (user_id, username, chat_id, max_registrations, subscription_time) VALUES (?, ?, ?, ?, ?);",
                     user_id, username, chat_id, max_registrations, int(time.time()))

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
        res, _ = self.__query("SELECT registrations.user_id, socials.social, socials.internal_id, socials.username, socials.title, socials.retreive_time, socials.status, registrations.status, registrations.expire_date, socials.social_id FROM registrations, socials WHERE registrations.social_id = socials.social_id;", fetch=0)
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
                socials_accounts_dict["subscriptions"][row[1]][row[2]].append({'user_id': row[0], 'social_id': row[9], 'state': row[7], 'expire': row[8]})
        return socials_accounts_dict

    def user_subscriptions(self, user_id, by_category=False):
        if by_category:
            res, _ = self.__query("SELECT socials.social, socials.title, socials.internal_id, registrations.status, registrations.expire_date , registrations.category "
                                  "FROM registrations, socials "
                                  "WHERE  registrations.user_id = ? AND  registrations.social_id = socials.social_id "
                                  "ORDER BY registrations.category, socials.social;", user_id, fetch=0)
        else:
            res, _ = self.__query("SELECT socials.social, socials.title, socials.internal_id, registrations.status, registrations.expire_date "
                                  "FROM registrations, socials "
                                  "WHERE  registrations.user_id = ? AND "
                                  "registrations.social_id = socials.social_id ORDER BY socials.social;", user_id, fetch=0)
        return res

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

    def unfollow_social_account(self, user_id, social, internal_id):
        _, rowcount = self.__query("DELETE FROM registrations \
            WHERE registrations.user_id = ? AND \
            registrations.social_id = (\
                SELECT socials.social_id FROM socials WHERE socials.social = ? AND socials.internal_id = ?);", user_id, social, internal_id, foreign=True)

        # If deletes something return True
        return bool(rowcount)

    def check_if_subscribed(self, user_id, social, username=None, internal_id=None):

        # Check if there's enough data
        if not (username or internal_id):
            return None, None

        # Check if user_id is subscribed to the SN profile issued
        if internal_id:
            res, _ = self.__query(
                "SELECT t_soc.internal_id "
                "FROM ( SELECT socials.internal_id, socials.social_id FROM socials "
                "WHERE socials.social = ? AND socials.internal_id = ?  ) t_soc "
                "INNER JOIN ( "
                "SELECT registrations.social_id  FROM registrations "
                "WHERE registrations.user_id = ?) t_reg "
                "ON t_soc.social_id = t_reg.social_id;", social, internal_id, user_id)

        else:
            res, _ = self.__query(
                "SELECT t_soc.internal_id "
                "FROM ( SELECT socials.internal_id, socials.social_id FROM socials "
                "WHERE socials.social = ? AND socials.username = ?  ) t_soc "
                "INNER JOIN ( "
                "SELECT registrations.social_id  FROM registrations "
                "WHERE registrations.user_id = ?) t_reg "
                "ON t_soc.social_id = t_reg.social_id;", social, username, user_id)

        # If exists return True with the internal_id
        if res:
            is_sub, internal_id = True, res[0]
        else:
            is_sub, internal_id = False, None
        return is_sub, internal_id

    def set_state_of_social_account(self, user_id, social, internal_id, state, exp_date):
        _, rowcount = self.__query("UPDATE registrations "
                                   "SET status = ? , expire_date = ? "
                                   "WHERE registrations.user_id = ? AND "
                                   "registrations.social_id = ("
                                   "SELECT socials.social_id "
                                   "FROM socials WHERE socials.social = ? AND socials.internal_id = ?);", state, exp_date, user_id, social, internal_id)
        return bool(rowcount)

    def archive_message(self, user_id, social_id, post_date, message):
        self.__query("INSERT INTO messages (user_id, social_id, update_date, message) VALUES (?, ?, ?, ?);",
                     user_id, social_id, post_date, json.dumps(message))

    @property
    def get_pause_expired_or_removed_messages(self):
        '''
            Ottengo i messaggi archiviati che hanno la pausa scaduta o non sono più in pausa
            :return: <List> of <List>
        '''
        res, _ = self.__query("SELECT messages.message_id, messages.message, t_reg.status "
                              "FROM messages "
                              "INNER JOIN(SELECT  * "
                              "FROM registrations "
                              "WHERE registrations.status != 3 OR (registrations.status = 3 AND registrations.expire_date < ?)) t_reg "
                              "ON messages.user_id = t_reg.user_id AND messages.social_id = t_reg.social_id "
                              "ORDER BY messages.update_date;",
                              time.time(), fetch=0)
        return res

    def remove_messages(self, messages):
        for mess in messages:
            self.__query("DELETE FROM messages "
                         "WHERE messages.message_id = ?;", mess)

    def set_category_of_social_account(self, user_id, social, internal_id, category):
        _, rowcount = self.__query("UPDATE registrations "
                                   "SET category = ? "
                                   "WHERE registrations.user_id = ? AND "
                                   "registrations.social_id = ("
                                   "SELECT socials.social_id "
                                   "FROM socials WHERE socials.social = ? AND socials.internal_id = ?);", category, user_id, social, internal_id)
        return bool(rowcount)

    def rename_category(self, user_id, category_old, category_new='default'):
        _, rowcount = self.__query("UPDATE registrations "
                                   "SET category = ? "
                                   "WHERE registrations.user_id = ? AND "
                                   "registrations.category = ?;", category_new, user_id, category_old)
        return bool(rowcount)

    def set_state_of_category(self, user_id, category, state, exp_date):
        _, rowcount = self.__query("UPDATE registrations "
                                   "SET status = ? , expire_date = ? "
                                   "WHERE registrations.user_id = ? AND "
                                   "registrations.category = ?;", state, exp_date, user_id, category)
        return bool(rowcount)

    def clean_expired_state(self):
        _, rowcount = self.__query("UPDATE registrations "
                                   "SET status = 0 , expire_date = -1 "
                                   "WHERE registrations.expire_date < ? AND registrations.expire_date != -1;", time.time())

        self.__logger.info("Sottoscrizioni con lo stato scaduto: %s ", rowcount)

    def set_role(self, user_id, role):
        _, rowcount = self.__query("INSERT INTO admins (user_id, role) VALUES (?, ?) "
                                   "ON CONFLICT(user_id) DO UPDATE SET role = ? WHERE role != ?;", user_id, role, role, role, foreign=True)
        return bool(rowcount)

    def list_operators(self):
        op_tuples, _ = self.__query("SELECT admins.user_id, admins.role, users.username "
                                    "FROM admins LEFT JOIN users ON admins.user_id= users.user_id "
                                    "ORDER BY role ASC;", fetch=0)
        return op_tuples

    def has_permissions(self, user_id, role):
        has_perm, _ = self.__query("SELECT COUNT(user_id) FROM admins "
                                   "WHERE user_id = ? AND role <= ?;", user_id, role)
        return bool(has_perm[0])

    def __get_role(self, user_id):
        role, _ = self.__query("SELECT role FROM admins WHERE user_id = ?;", user_id)
        return None if role is None else role[0]

    def __get_user_id(self, username):
        username, _ = self.__query("SELECT user_id FROM users WHERE username = ?;", username)
        return None if username is None else username[0]

    def __is_auth_action(self, user_id, recipient_user_id, role_lvl_action=None):
        is_success = False
        issuer_role, recipient_role = self.__get_role(user_id), self.__get_role(recipient_user_id)
        if role_lvl_action is None:
            role_lvl_action = issuer_role
        if recipient_role is None:
            recipient_role = 999  # Is an arbitrary high number
        if issuer_role is None:
            pass
        elif (issuer_role <= recipient_role) and (role_lvl_action >= issuer_role):
            is_success = True
        return is_success

    def __is_auth_action_uname(self, user_id, recipient_uname_id, is_username=False, role_lvl_action=None):
        is_success = False
        if is_username:
            recipient_uname_id = self.__get_user_id(recipient_uname_id)
        if recipient_uname_id is None:
            pass
        elif self.__is_auth_action(user_id, recipient_uname_id, role_lvl_action):
            is_success = True
        return is_success, recipient_uname_id

    def __rm_role(self, user_id):
        _, rows = self.__query("DELETE FROM admins WHERE user_id = ?;",
                               user_id, foreign=True)
        return bool(rows)

    def __set_follow_limit(self, user_id, max_registrations):
        _, rowcount = self.__query("UPDATE users SET max_registrations = ? "
                                   "WHERE user_id = ? AND max_registrations != ?;",
                                   max_registrations, user_id, max_registrations,
                                   foreign=True)
        return bool(rowcount)

    def __ban_user(self, user_id, d_expire_time):
        _, rowcount = self.__query("INSERT INTO jail (user_id, expire_time) VALUES (?, ?);",
                                   user_id, int(time.time() + d_expire_time))
        return bool(rowcount)

    def __unban_user(self, user_id):
        _, rows = self.__query("DELETE FROM jail WHERE user_id = ?;",
                               user_id)
        return bool(rows)

    def is_banned(self, user_id):
        is_banned, _ = self.__query("SELECT COUNT(user_id) FROM jail "
                                    "WHERE user_id = ?;", user_id)
        return bool(is_banned[0])

    def set_role_auth(self, user_id, recipient_uname_id, role, is_username=False):
        is_success = False
        if role <= self.__max_role_lvl:
            is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username, role)
            is_success = self.set_role(recipient_uname_id, role) if is_success else is_success
        return is_success

    def kick_user_auth(self, user_id, recipient_uname_id, is_username=False):
        is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username)
        if is_success:
            is_success = self.unsubscribe_user(recipient_uname_id)
        return self.unsubscribe_user(recipient_uname_id) if is_success else is_success

    def rm_role_auth(self, user_id, recipient_uname_id, is_username=False):
        is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username)
        return self.__rm_role(recipient_uname_id) if is_success else is_success

    def set_follow_limit_auth(self, user_id, recipient_uname_id, max_registrations, is_username=False):
        is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username)
        return self.__set_follow_limit(recipient_uname_id, max_registrations) if is_success else is_success

    def set_ban_user_auth(self, user_id, recipient_uname_id, is_username=False, d_expire_time=4294967296):
        is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username)
        return self.__ban_user(recipient_uname_id, d_expire_time) if is_success else is_success

    def set_unban_user_auth(self, user_id, recipient_uname_id, is_username=False):
        is_success, recipient_uname_id = self.__is_auth_action_uname(user_id, recipient_uname_id, is_username)
        return self.__unban_user(recipient_uname_id) if is_success else is_success
