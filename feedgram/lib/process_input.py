#!/usr/bin/env python3
import logging
import re
import time


class Processinput:

    def __init__(self, database, social_list, privilege_key):
        self.__logger = logging.getLogger('telegram_bot.process_input')
        self.__db = database
        self.__re_compiler()
        self.__socials = social_list
        self.__privilege_key = privilege_key

    # Big message
    __msm_stop = ("You're no longer subscribed!\n"
                  "We already <i>miss</i> you, please come back soon! 😢\n"
                  "Tip: In order to re-joyn type /start *wink* *wink*")

    __msm_help = ("📖 Help\n\nYou can follow up to <i>10 social accounts</i>.\n"
                  "Socials currently supported:\n"
                  " • <i>Instagram</i>\n"
                  "You can follow only <b>public</b> accounts.\n"
                  "\n"
                  "<b>Receive Feeds:</b>\n"
                  " • /sub <i>social</i> <i>username</i>\n"
                  " • /sub <i>link</i>\n"
                  " • /unsub <i>social</i> <i>username</i>\n"
                  " • /mute <i>social</i> <i>username</i> <i>time</i>\n"
                  " • /halt <i>social</i> <i>username</i> <i>time</i>\n"
                  " • /pause <i>social</i> <i>username</i> <i>time</i>\n"
                  "<b>Bot:</b>\n"
                  " • /stop to stop and unsubscribe from the bot.")

    # inline keyboard
    __ilk_help = {"text": "📖", "callback_data": "help_mode"}

    __ilk_rem = {"text": "🗑", "callback_data": "remove"}
    __ilk_notoff = {"text": "🔕", "callback_data": "mute"}
    __ilk_halt = {"text": "⏹", "callback_data": "halt"}
    __ilk_pause = {"text": "⏯️", "callback_data": "pause"}

    __ilk_rem_c = {"text": "🗑", "callback_data": "cat_remove"}
    __ilk_notoff_c = {"text": "🔕", "callback_data": "cat_mute"}
    __ilk_halt_c = {"text": "⏹", "callback_data": "cat_halt"}
    __ilk_pause_c = {"text": "⏯️", "callback_data": "cat_pause"}

    __ilk_list = {"text": "📋", "callback_data": "list_mode"}
    __ilk_category = {"text": "🏷", "callback_data": "category_mode"}

    def process(self, updates):
        messages = []
        for update in updates["result"]:
            mss_type = None
            if 'message' in update:
                mss_type = "message"
            elif 'callback_query' in update:
                mss_type = "callback_query"

            else:
                # mss_type = "WTF" #trovare un modo per gestire questo caso
                self.__logger.warning("Messaggio ricevuto non coretto %s ", update)
            if mss_type:
                user_id = update[mss_type]["from"]["id"]
                username = None
                chat_id = None
                if "username" in update[mss_type]["from"]:
                    username = update[mss_type]["from"]["username"]
                else:
                    username = ""
                if "chat" in update[mss_type]:  # di solito arrivano quando ci sono i messaggi "normali"
                    chat_id = update[mss_type]["chat"]["id"]
                elif "message" in update[mss_type]:  # di solito arrivando quando ci sono le callback_query
                    chat_id = update[mss_type]["message"]["chat"]["id"]
                else:
                    # chat_id = update[mss_type]["WTF"] #trovare un modo per gestire questo caso
                    self.__logger.warning("Il messaggio ricevuto non contiene in numero della chat %s ", update)
                if chat_id:
                    if self.__db.check_utente(user_id):
                        if 'text' in update[mss_type]:
                            text = update[mss_type]["text"]
                            if text[:1] == "/":
                                if text == "/stop":
                                    self.__db.unsubscribe_user(user_id)
                                    if self.__db.check_utente(user_id):
                                        messages.append(self.__ms_maker(chat_id, "Something bad happened, you're STILL registered!\nTry again later."))
                                    else:
                                        messages.append(self.__ms_maker(chat_id, self.__msm_stop, "HTML"))
                                elif text == "/help":
                                    tets = self.__ms_maker(chat_id, self.__msm_help, "HTML", None, None, {"inline_keyboard": [[self.__ilk_list, self.__ilk_category]]})
                                    messages.append(tets)
                                elif text == "/list":
                                    message, button = self.__list_mss(user_id, 0)
                                    messages.append(self.__ms_maker(chat_id, message, "HTML", None, None, {"inline_keyboard": button}))
                                elif text[:4] == "/sub":
                                    match = re.search(r"^([a-zA-Z]{1,16}) (\S{1,128})$", text[5:])
                                    if match:
                                        msg_subs = self.__iscrizione({"social": match.group(1), "username": match.group(2), "internal_id": None, "social_id": None, "link": None, "data": {}}, user_id)
                                    else:
                                        match = re.search(r"^(http[s]?:\/\/)?([a-zA-Z0-9-_]{2,256}\.\S*)$", text[5:])
                                        if match:
                                            msg_subs = self.__iscrizione({"social": None, "username": None, "internal_id": None, "social_id": None, "link": match.group(2), "data": {}}, user_id)
                                        else:
                                            msg_subs = None
                                    if not msg_subs:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/sub</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/sub &lt;link&gt;</code>\n<i>or</i>\n<code>/sub &lt;social&gt; &lt;username&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))
                                elif text[:6] == "/unsub":
                                    match = re.search(r"^([a-zA-Z]{1,16}) (\S{1,128})$", text[7:])
                                    if match:
                                        unsub_status = self.__unsubscription({"social": match.group(1), "username": match.group(2), "internal_id": None}, user_id)
                                        if unsub_status["ok"]:
                                            msg_subs = "<b>✅🗑 Unsubscribed successfully!</b>\n\nSocial: <i>{}</i>\nUser: <i>{}</i>!".format(match.group(1), match.group(2))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(unsub_status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/unsub</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/unsub &lt;social&gt; &lt;username&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))
                                elif text[:5] == "/mute":
                                    match = re.match(r"(\S+) (\S+) (\d{1,3}d|\d{1,3}h)", text[6:])
                                    if match:
                                        unsub_status = self.__set_sub_state({"social": match.group(1), "username": match.group(2), "internal_id": None}, user_id, 1, match.group(3))
                                        if unsub_status["ok"]:
                                            msg_subs = "<b>✅🔕 Muted successfully!</b>\n\nSocial: <i>{}</i>\nUser: <i>{}</i>!".format(match.group(1), match.group(2))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(unsub_status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/mute</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/mute &lt;social&gt; &lt;username&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/mute &lt;social&gt; &lt;username&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:5] == "/halt":
                                    match = re.match(r"(\S+) (\S+) (\d{1,3}d|\d{1,3}h)", text[6:])
                                    if match:
                                        unsub_status = self.__set_sub_state({"social": match.group(1), "username": match.group(2), "internal_id": None}, user_id, 2, match.group(3))
                                        if unsub_status["ok"]:
                                            msg_subs = "<b>✅⏹ Stopped successfully!</b>\n\nSocial: <i>{}</i>\nUser: <i>{}</i>!".format(match.group(1), match.group(2))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(unsub_status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/halt</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/halt &lt;social&gt; &lt;username&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/halt &lt;social&gt; &lt;username&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:6] == "/pause":
                                    match = re.match(r"(\S+) (\S+) (\d{1,3}d|\d{1,3}h)", text[7:])
                                    if match:
                                        unsub_status = self.__set_sub_state({"social": match.group(1), "username": match.group(2), "internal_id": None}, user_id, 3, match.group(3))
                                        if unsub_status["ok"]:
                                            msg_subs = "<b>✅⏯️ Paused successfully!</b>\n\nSocial: <i>{}</i>\nUser: <i>{}</i>!".format(match.group(1), match.group(2))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(unsub_status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/pause</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/pause &lt;social&gt; &lt;username&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/pause &lt;social&gt; &lt;username&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:6] == "/cmute":
                                    match = re.match(r"(\S+) (\d{1,3}d|\d{1,3}h)", text[7:])
                                    if match:
                                        status = self.__set_cat_state(user_id, match.group(1), 1, match.group(2))
                                        if status["ok"]:
                                            msg_subs = "<b>✅🔕 Muted successfully!</b>\n\nCategory: <i>{}</i>".format(match.group(1))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/cmute</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/cmute &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/cmute &lt;category&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:6] == "/chalt":
                                    match = re.match(r"(\S+) (\d{1,3}d|\d{1,3}h)", text[7:])
                                    if match:
                                        status = self.__set_cat_state(user_id, match.group(1), 2, match.group(2))
                                        if status["ok"]:
                                            msg_subs = "<b>✅⏹ Stopped successfully!</b>\n\nCategory: <i>{}</i>".format(match.group(1))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/chalt</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/chalt &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/chalt &lt;category&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:7] == "/cpause":
                                    match = re.match(r"(\S+) (\d{1,3}d|\d{1,3}h)", text[8:])
                                    if match:
                                        status = self.__set_cat_state(user_id, match.group(1), 3, match.group(2))
                                        if status["ok"]:
                                            msg_subs = "<b>✅⏯️ Paused successfully!</b>\n\nCategory: <i>{}</i>".format(match.group(1))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/cpause</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/cpause &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/cpause &lt;category&gt; &lt;XXXh&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:9] == "/category":
                                    match = re.search(r"^([a-zA-Z]{1,16}) (\S{1,128}) (\S{1,32})$", text[10:])
                                    if match:
                                        status = self.__set_sub_category({"social": match.group(1), "username": match.group(2), "internal_id": None}, user_id, match.group(3))
                                        if status["ok"]:
                                            msg_subs = "<b>✅Successfully moved!</b>\n\nSocial: <i>{}</i>\nUser: <i>{}</i>\nTo category: <i>{}</i>!".format(match.group(1), match.group(2), match.group(3))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>{}</code>".format(status["description"])
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/category</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/category &lt;social&gt; &lt;username&gt; &lt;category&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:7] == "/rename":
                                    match = re.search(r"^(\S{1,32}) (\S{1,32})$", text[8:])
                                    if match:
                                        status = self.__db.rename_category(user_id, match.group(1), match.group(2))
                                        if status:
                                            msg_subs = "<b>✅Successfully renamed!</b>\n\nCategory: <i>{}</i>\nInto: <i>{}</i>".format(match.group(1), match.group(2))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>categoryDontExist</code>"
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/rename</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/rename &lt;category&gt; &lt;category&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text[:7] == "/remove":
                                    match = re.search(r"^(\S{1,32})$", text[8:])
                                    if match:
                                        status = self.__db.rename_category(user_id, match.group(1))
                                        if status:
                                            msg_subs = "<b>✅Successfully removed!</b>\n\nCategory: <i>{}</i>".format(match.group(1))
                                        else:
                                            msg_subs = "<b>⚠️Warning</b>\nError: <code>categoryDontExist</code>"
                                    else:
                                        msg_subs = "<b>⚠️Warning</b>\n<code>/remove</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/remove &lt;category&gt;</code>"
                                    messages.append(self.__ms_maker(chat_id, msg_subs, "HTML"))

                                elif text == "/start":
                                    messages.append(self.__ms_maker(chat_id, "You're alredy registered.\nType /help to learn the commands available!"))

                                elif text[:8] == "/privkey":
                                    match = re.match(r"^\s+([A-Za-z0-9-]+)", text[8:])
                                    if match:
                                        if match.group(1) == self.__privilege_key:
                                            if self.__db.set_role(user_id, 0):
                                                msg = "You have now creator privileges!"
                                            else:
                                                msg = "You already have the role of creator"
                                            messages.append(self.__ms_maker(chat_id, msg))

                                elif text[:7] == "/listop":
                                    if self.__db.has_permissions(user_id, 1):
                                        op_tuples = self.__db.list_operators()
                                        op_list = self.__mk_list_op_json(op_tuples)
                                        op_list = self.__mk_list_op_decorate(op_list)
                                        msg = "{}{}".format("<b>⚖️ Operators list</b>\n\n", self.__mk_list(op_list))
                                        messages.append(self.__ms_maker(chat_id, msg, "HTML"))

                                elif text[:8] == "/setrole":
                                    if self.__db.has_permissions(user_id, 1):
                                        match = re.search(r"^\s+(@[a-zA-Z0-9]{5,32}|\d{5,16})\s+(\d{1,3}|admin|mod)$", text[8:])
                                        if match:
                                            int_oprole = 0 if match[2] == "admin" else 1 if match[2] == "mod" else int(match[2])
                                            str_oprole = self.__replace_all(str(int_oprole), self.ROLES_S)
                                            str_opuser, is_username = (match[1][1:], True) if match[1][:1] == "@" else (match[1], False)
                                            msg = "<b>✅ Successful action</b>\n\nUser {} is now <b>{}</b>!".format(match[1], str_oprole) if self.__db.set_role_auth(user_id, str_opuser, int_oprole, is_username) else "<b>⚠️Warning</b>\n\nAction not performed; the reason could be one or a combination of those:\n • Wrong username/userId issued.\n • Not enough privileges.\n • The action you are trying to perform is not possible!"
                                        else:
                                            msg = "<b>⚠️ Warning</b>\n<code>/setrole</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/setrole &lt;@username&gt; &lt;rolenumber&gt;</code>\n<i>OR:</i>\n<code>/setrole &lt;userId&gt; &lt;rolenumber&gt;</code>"
                                        messages.append(self.__ms_maker(chat_id, msg, "HTML"))

                                elif text[:8] == "/remrole":
                                    if self.__db.has_permissions(user_id, 1):
                                        match = re.search(r"^\s+(@[a-zA-Z0-9]{5,32}|\d{5,16})$", text[8:])
                                        if match:
                                            str_opuser, is_username = (match[1][1:], True) if match[1][:1] == "@" else (match[1], False)
                                            msg = "<b>✅ Successful action</b>\n\nUser {} now has <b>no role</b>!".format(match[1]) if self.__db.rm_role_auth(user_id, str_opuser, is_username) else "<b>⚠️Warning</b>\n\nAction not performed; the reason could be one or a combination of those:\n • Wrong username/userId issued.\n • Not enough privileges.\n • The action you are trying to perform is not possible!"
                                        else:
                                            msg = "<b>⚠️ Warning</b>\n<code>/remrole</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/remrole &lt;@username&gt;</code>\n<i>OR:</i>\n<code>/remrole &lt;userId&gt;</code>"
                                        messages.append(self.__ms_maker(chat_id, msg, "HTML"))

                                elif text[:5] == "/kick":
                                    if self.__db.has_permissions(user_id, 1):
                                        match = re.search(r"^\s+(@[a-zA-Z0-9]{5,32}|\d{5,16})$", text[5:])
                                        if match:
                                            str_opuser, is_username = (match[1][1:], True) if match[1][:1] == "@" else (match[1], False)
                                            msg = "<b>✅ Successful action</b>\n\nUser {} is <b>kicked</b>!".format(match[1]) if self.__db.kick_user_auth(user_id, str_opuser, is_username) else "<b>⚠️Warning</b>\n\nAction not performed; the reason could be one or a combination of those:\n • Wrong username/userId issued.\n • Not enough privileges.\n • The action you are trying to perform is not possible!"
                                        else:
                                            msg = "<b>⚠️ Warning</b>\n<code>/kick</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/kick &lt;@username&gt;</code>\n<i>OR:</i>\n<code>/kick &lt;userId&gt;</code>"
                                        messages.append(self.__ms_maker(chat_id, msg, "HTML"))
                                else:
                                    messages.append(self.__ms_maker(chat_id, "Unrecognized command"))
                        # "chat_id":chat_id non è prevista dalle API di Telegram per answerCallbackQuery, serve solo alla funzione Telegram.send_messages(coda, condizione)
                        # che si basa sul parametro "chat_id" per schedualare i messaggi da inviare
                        # TODO: Togliere i chat_id inutili non appena è stato risolto il problema nel send_messages perché questa è una soluzione triste (ma non troppo)
                        # NOTA: Mi sa che questa "soluzione triste" rimarrà così per sempre, od almeno finchè Telegram non rilascerà specifiche più dettagliate.
                        elif 'callback_query' in update:
                            callback_query_id = update[mss_type]["id"]
                            message_id = update[mss_type]["message"]["message_id"]
                            callback_data = update[mss_type]["data"]

                            if callback_data == "help_mode":
                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Help", False))
                                messages.append(self.__ms_edit(chat_id, message_id, self.__msm_help, "HTML", {"inline_keyboard": [[self.__ilk_list, self.__ilk_category]]}))

                            # Lo spazio con il numero possono non esserci
                            # Es.
                            # list_mode     <- chiamata normale del list mode
                            # list_mode 66  <- chiamata durante lo spostamento di pagina
                            elif bool(re.findall(r"^(list_mode)( \d+)?", callback_data)):
                                match = re.findall(r"^(list_mode) ?(\d+)?", callback_data)[0]
                                if match[1]:
                                    message, button = self.__list_mss(user_id, int(match[1]))
                                else:
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Following list", False))
                                    message, button = self.__list_mss(user_id, 0)
                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # category_mode     <- chiamata normale del list mode
                            # category_mode 66  <- chiamata durante lo spostamento di pagina
                            elif bool(re.findall(r"^(category_mode)( \d+)?", callback_data)):
                                match = re.findall(r"^(category_mode) ?(\d+)?", callback_data)[0]
                                if match[1]:
                                    message, button = self.__category_mss(user_id, int(match[1]))
                                else:
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Category list", False))
                                    message, button = self.__category_mss(user_id, 0)
                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # remove                            <- chiamata normale al remove
                            # remove 66                         <- stò solo scorrendo le pagine
                            # remove 66 <social> <internal_id>  <- stò facendo una rimozzone e sono ad una data pagina
                            # ^(remove)     <- inizia con remove
                            # ( \d+)?       <- Può avere un numero
                            # ( \S+ \S+)?   <- Può esserci una sequenza di due str
                            elif bool(re.findall(r"^(remove)( \d+)?( \S+ \S+)?", callback_data)):
                                # avremo 4 match:
                                # 0: remove
                                # 1: <page_index>
                                # 2: <social>
                                # 3: <internal_id>
                                # Per evitare che nelle group 2 e 3 (\S+) ci sia lo spazio
                                # si è messo fuori dalla parentesi con un ? per
                                # indicare la possibilità che ci sia
                                match = re.findall(r"^(remove)( \d+)? ?(\S+)? ?(\S+)?", callback_data)[0]
                                if match[1]:
                                    # il numero è presente siamo in una pagina
                                    if match[2] and match[3]:
                                        # Se gli elementi 2 e 3 sono presenti siamo nella rimozione di un elemento
                                        # Lo rimuoviamo dal database e mettiamo il messaggio Unfollowed
                                        unsub_status = self.__unsubscription({"social": match[2], "username": None, "internal_id": match[3]}, user_id)
                                        if unsub_status["ok"]:
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, "Unfollowed", False))
                                        else:
                                            alert_msg = "Error: {}".format(unsub_status["description"])
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, alert_msg, True))

                                    # In ogni caso genereremo il messaggio nella pagina
                                    message, button = self.__list_remove_mss(user_id, int(match[1]))

                                else:
                                    # Se il numero non è presente siamo nel caso base della remove a pagina 0
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Be careful, you'll not receive confirmation alert upon removing!", True))
                                    message, button = self.__list_remove_mss(user_id, 0)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # mute
                            # mute <page_index> <day>
                            # mute <page_index> <day> <socail> <internal_id>
                            elif bool(re.findall(r"^(mute)( \d+)?( \d+)?( \S+ \S+)?", callback_data)):
                                # 0: mute
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <social>
                                # 4: <internal_id>

                                match = re.findall(r"^(mute)( \d+)?( \d+)? ?(\S+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3] and match[4]:
                                        # Se gli elementi 3 e 4 sono presenti siamo nella pausa di un elemento

                                        unsub_status = self.__set_sub_state({"social": match[3], "username": None, "internal_id": match[4]}, user_id, 1, "{}d".format(match[2]))

                                        if unsub_status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Muted", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Un-Muted", False))
                                        else:
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, "Alert: {}".format(unsub_status["description"]), True))

                                    # In ogni caso genereremo il messaggio data la pagina e il day indicati
                                    message, button = self.__list_mute_mss(user_id, int(match[1]), int(match[2]))

                                else:
                                    # Se non  abbiamo ne day ne pagina siamo nel caso base
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Muted list", False))
                                    message, button = self.__list_mute_mss(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # halt
                            # halt <page_index> <day>
                            # halt <page_index> <day> <socail> <internal_id>
                            elif bool(re.findall(r"^(halt)( \d+)?( \d+)?( \S+ \S+)?", callback_data)):
                                # 0: halt
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <social>
                                # 4: <internal_id>
                                match = re.findall(r"^(halt)( \d+)?( \d+)? ?(\S+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3] and match[4]:
                                        # Se gli elementi 3 e 4 sono presenti siamo nella pausa di un elemento

                                        unsub_status = self.__set_sub_state({"social": match[3], "username": None, "internal_id": match[4]}, user_id, 2, "{}d".format(match[2]))

                                        if unsub_status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Stopped", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Resetted", False))
                                        else:
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, "Error: {}".format(unsub_status["description"]), True))

                                    # In ogni caso genereremo il messaggio data la pagina e il day indicati
                                    message, button = self.__list_halt_mss(user_id, int(match[1]), int(match[2]))

                                else:
                                    # Se non  abbiamo ne day ne pagina siamo nel caso base
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Stop list", False))
                                    message, button = self.__list_halt_mss(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # pause
                            # pause <page_index> <day>
                            # pause <page_index> <day> <socail> <internal_id>
                            elif bool(re.findall(r"^(pause)( \d+)?( \d+)?( \S+ \S+)?", callback_data)):
                                # 0: pause
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <social>
                                # 4: <internal_id>
                                match = re.findall(r"^(pause)( \d+)?( \d+)? ?(\S+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3] and match[4]:
                                        # Se gli elementi 3 e 4 sono presenti siamo nella pausa di un elemento

                                        unsub_status = self.__set_sub_state({"social": match[3], "username": None, "internal_id": match[4]}, user_id, 3, "{}d".format(match[2]))

                                        if unsub_status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Paused", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Un-Paused", False))
                                        else:
                                            alert_msg = "Alert: {}".format(unsub_status["description"])
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, alert_msg, True))

                                    # In ogni caso genereremo il messaggio data la pagina e il day indicati
                                    message, button = self.__list_pause_mss(user_id, int(match[1]), int(match[2]))

                                else:
                                    # Se non  abbiamo ne day ne pagina siamo nel caso base
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Pause list", False))
                                    message, button = self.__list_pause_mss(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # cat_remove <page_index> <category>
                            elif bool(re.findall(r"^(cat_remove)( \d+)?( \S+)?", callback_data)):
                                # 0: cat_remove
                                # 1: <page_index>
                                # 2: <category>
                                match = re.findall(r"^(cat_remove)( \d+)? ?(\S+)?", callback_data)[0]
                                if match[1]:
                                    # il numero è presente siamo in una pagina
                                    if match[2]:
                                        # Se l'elemento 2 è presente siamo nella rimozione di una categoria
                                        # La rimosssione di una categoria avviene con la rinomina della categoraia attuale in quella di 'default'
                                        self.__db.rename_category(user_id, match[2])
                                        messages.append(self.__callback_maker(chat_id, callback_query_id, "Category removed", False))

                                    # In ogni caso genereremo il messaggio nella pagina
                                    message, button = self.__category_remove(user_id, int(match[1]))

                                else:
                                    # Se il numero non è presente siamo nel caso base della remvoe a pagina 0
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Only the category will be removed, the subscriptions will be moved to 'default' category", True))
                                    message, button = self.__category_remove(user_id, 0)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # cat_mute <page_index> <day> category>
                            elif bool(re.findall(r"^(cat_mute)( \d+)?( \d+)?( \S+)?", callback_data)):
                                # 0: cat_mute
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <category>
                                match = re.findall(r"^(cat_mute)( \d+)?( \d+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3]:
                                        status = self.__set_cat_state(user_id, match[3], 1, "{}d".format(match[2]))
                                        if status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Muted", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Un-Muted", False))
                                        else:
                                            alert_msg = "Alert: {}".format(unsub_status["description"])
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, alert_msg, True))
                                    # In ogni caso genereremo il messaggio nella pagina
                                    message, button = self.__category_mute(user_id, int(match[1]), int(match[2]))
                                else:
                                    # Se il numero non è presente siamo nel caso base della remvoe a pagina 0
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Mute", False))
                                    message, button = self.__category_mute(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # cat_halt <page_index> <day> category>
                            elif bool(re.findall(r"^(cat_halt)( \d+)?( \d+)?( \S+)?", callback_data)):
                                # 0: cat_halt
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <category>
                                match = re.findall(r"^(cat_halt)( \d+)?( \d+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3]:
                                        status = self.__set_cat_state(user_id, match[3], 2, "{}d".format(match[2]))
                                        if status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Stopped", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Un-Stopped", False))
                                        else:
                                            alert_msg = "Alert: {}".format(unsub_status["description"])
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, alert_msg, True))
                                    # In ogni caso genereremo il messaggio nella pagina
                                    message, button = self.__category_halt(user_id, int(match[1]), int(match[2]))
                                else:
                                    # Se il numero non è presente siamo nel caso base della remvoe a pagina 0
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Stop", False))
                                    message, button = self.__category_halt(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                            # cat_halt <page_index> <day> category>
                            elif bool(re.findall(r"^(cat_pause)( \d+)?( \d+)?( \S+)?", callback_data)):
                                # 0: cat_pause
                                # 1: <page_index>
                                # 2: <day>
                                # 3: <category>
                                match = re.findall(r"^(cat_pause)( \d+)?( \d+)? ?(\S+)?", callback_data)[0]
                                if match[1] and match[2]:
                                    # il numero è presente siamo in una pagina
                                    if match[3]:
                                        status = self.__set_cat_state(user_id, match[3], 3, "{}d".format(match[2]))
                                        if status["ok"]:
                                            if int(match[2]) != 0:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Paused", False))
                                            else:
                                                messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Un-Paused", False))
                                        else:
                                            alert_msg = "Alert: {}".format(unsub_status["description"])
                                            messages.append(self.__callback_maker(chat_id, callback_query_id, alert_msg, True))
                                    # In ogni caso genereremo il messaggio nella pagina
                                    message, button = self.__category_pause(user_id, int(match[1]), int(match[2]))
                                else:
                                    # Se il numero non è presente siamo nel caso base della remvoe a pagina 0
                                    messages.append(self.__callback_maker(chat_id, callback_query_id, "Category Pause", False))
                                    message, button = self.__category_pause(user_id, 0, 3)

                                messages.append(self.__ms_edit(chat_id, message_id, message, "HTML", {"inline_keyboard": button}))

                        else:
                            messages.append(self.__ms_maker(chat_id, "[AUTHORIZED] You can send text only!"))
                    else:
                        if 'text' in update[mss_type]:
                            text = update[mss_type]["text"]
                            if text == "/start":
                                self.__db.subscribe_user(user_id, username, chat_id, 10)
                                if self.__db.check_utente(user_id):
                                    messages.append(self.__ms_maker(chat_id, "Congratulations, you're now registered!\nType /help to learn the commands available!"))
                                    tets = self.__ms_maker(chat_id, self.__msm_help, "HTML")
                                    messages.append(tets)
                                else:
                                    messages.append(self.__ms_maker(chat_id, "Something bad happened, you're NOT registered!\nTry again later."))
                            else:
                                messages.append(self.__ms_maker(chat_id, "You're not registered, type /start to subscribe!"))

        return messages

    @classmethod
    def __ms_maker(cls, chatid, text, markdown=None, disable_web_page_preview=None, disable_notification=None, reply_markup=None):
        temp_dict = {}

        temp_dict["type"] = "sendMessage"
        temp_dict["chat_id"] = chatid
        temp_dict["text"] = text

        # markdown <==> parser_mode di telegram
        if markdown:
            temp_dict["markdown"] = markdown

        if isinstance(disable_web_page_preview, bool):
            temp_dict["disable_web_page_preview"] = disable_web_page_preview

        if isinstance(disable_notification, bool):
            temp_dict["disable_notification"] = disable_notification

        if reply_markup:
            temp_dict["reply_markup"] = reply_markup

        return temp_dict

    @classmethod
    def __callback_maker(cls, chatid, queryid, text=None, alert=None):
        temp_dict = {}

        temp_dict["type"] = "answerCallbackQuery"
        temp_dict["chat_id"] = chatid
        temp_dict["callback_query_id"] = queryid
        if text:
            temp_dict["text"] = text

        # markdown <==> parser_mode di telegram
        if alert:
            temp_dict["show_alert"] = alert

        return temp_dict

    @classmethod
    def __ms_edit(cls, chat_id, message_id, text, markdown=None, reply_markup=None):
        temp_dict = {}

        temp_dict["type"] = "editMessageText"
        temp_dict["chat_id"] = chat_id
        temp_dict["message_id"] = message_id
        temp_dict["text"] = text

        # markdown <==> parser_mode di telegram
        if markdown:
            temp_dict["markdown"] = markdown

        if reply_markup:
            temp_dict["reply_markup"] = reply_markup

        return temp_dict

    SUB_X_PAGE = 6
    BUTN_X_ROW = 3
    NUMBER_DICT = {"0": "⓪", "1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦", "8": "⑧", "9": "⑨"}
    STATUS_DICT = {"0": "", "1": "🔕", "2": "⏹", "3": "⏯️"}
    LINE_LIMIT = 24
    ROLES_P = {"0": "Creators", "1": "Moderators"}
    ROLES_S = {"0": "Creator", "1": "Moderator"}

    def __list_mss(self, user_id, index):
        user_subscriptions = self.__db.user_subscriptions(user_id)
        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [0], "👥Follow List\n" + ' ' * 50 + "\nYou are following: \n")

        buttons_list = []
        buttons_list.append(self.__make_navigation_button("list_mode", page_idx, len(user_subscriptions)))
        buttons_list.append([self.__ilk_pause, self.__ilk_notoff, self.__ilk_halt, self.__ilk_rem])
        buttons_list.append([self.__ilk_help])

        return txt_prepend, buttons_list

    def __list_remove_mss(self, user_id, index):
        user_subscriptions = self.__db.user_subscriptions(user_id)
        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [0], "♻️Remove\n" + ' ' * 50 + "\nYou are following: \n", True)

        buttons_list = []
        buttons_list = self.__make_numeric_button('remove {}'.format(page_idx), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("remove", page_idx, len(user_subscriptions)))
        buttons_list.append([self.__ilk_list, self.__ilk_help])

        return txt_prepend, buttons_list

    def __list_mute_mss(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id)
        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [0], "👥Mute List\n" + ' ' * 50 + "\nYou are following: \n", True)

        buttons_list = []
        buttons_list = self.__make_numeric_button('mute {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("mute", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("mute", dtime, page_idx)
        buttons_list.append([self.__ilk_list, self.__ilk_help])

        return txt_prepend, buttons_list

    def __list_halt_mss(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id)
        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [0], "👥Stop List\n" + ' ' * 50 + "\nYou are following: \n", True)

        buttons_list = []
        buttons_list = self.__make_numeric_button('halt {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("halt", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("halt", dtime, page_idx)
        buttons_list.append([self.__ilk_list, self.__ilk_help])

        return txt_prepend, buttons_list

    def __list_pause_mss(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id)
        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [0], "👥Pause List\n" + ' ' * 50 + "\nYou are following: \n", True)

        buttons_list = []
        buttons_list = self.__make_numeric_button('pause {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("pause", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("pause", dtime, page_idx)
        buttons_list.append([self.__ilk_list, self.__ilk_help])

        return txt_prepend, buttons_list

    def __category_mss(self, user_id, index):
        user_subscriptions = self.__db.user_subscriptions(user_id, True)

        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [5, 0], "👥Category List\n" + ' ' * 50 + "\nYou are following: \n", True, True)

        buttons_list = []
        buttons_list.append(self.__make_navigation_button("category_mode", page_idx, len(user_subscriptions)))
        buttons_list.append([self.__ilk_pause_c, self.__ilk_notoff_c, self.__ilk_halt_c, self.__ilk_rem_c])
        buttons_list.append([self.__ilk_help])

        return txt_prepend, buttons_list

    def __category_remove(self, user_id, index):
        user_subscriptions = self.__db.user_subscriptions(user_id, True)

        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [5, 0], "🗑Category List\n" + ' ' * 50 + "\nYou are following: \n", True, True)

        buttons_list = []
        buttons_list = self.__make_numeric_button_category('cat_remove {}'.format(page_idx), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("cat_remove", page_idx, len(user_subscriptions)))
        buttons_list.append([self.__ilk_category, self.__ilk_help])

        return txt_prepend, buttons_list

    def __category_mute(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id, True)

        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [5, 0], "🔕Category List\n" + ' ' * 50 + "\nYou are following: \n", True, True)

        buttons_list = []
        buttons_list = self.__make_numeric_button_category('cat_mute {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("cat_mute", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("cat_mute", dtime, page_idx)
        buttons_list.append([self.__ilk_category, self.__ilk_help])

        return txt_prepend, buttons_list

    def __category_halt(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id, True)

        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [5, 0], "⏹Category List\n" + ' ' * 50 + "\nYou are following: \n", True, True)

        buttons_list = []
        buttons_list = self.__make_numeric_button_category('cat_halt {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("cat_halt", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("cat_halt", dtime, page_idx)
        buttons_list.append([self.__ilk_category, self.__ilk_help])

        return txt_prepend, buttons_list

    def __category_pause(self, user_id, index, dtime):
        user_subscriptions = self.__db.user_subscriptions(user_id, True)

        txt_prepend, page_idx = self.__textmessage(index, user_subscriptions, [5, 0], "⏯️Category List\n" + ' ' * 50 + "\nYou are following: \n", True, True)

        buttons_list = []
        buttons_list = self.__make_numeric_button_category('cat_pause {} {}'.format(page_idx, dtime), user_subscriptions, page_idx, self.SUB_X_PAGE, self.BUTN_X_ROW)
        buttons_list.append(self.__make_navigation_button("cat_pause", page_idx, len(user_subscriptions), dtime))
        buttons_list = buttons_list + self.__make_time_button("cat_pause", dtime, page_idx)
        buttons_list.append([self.__ilk_category, self.__ilk_help])

        return txt_prepend, buttons_list

    @classmethod
    def __make_numeric_button(cls, callbk_data, array, start, lent, row_len):
        i = 1
        result = []
        tmp = []
        for subscri in array[start: start + lent]:
            tmp.append({"text": str(i), "callback_data": "{} {} {}".format(callbk_data, subscri[0], subscri[2])})
            # tmp.append({"text": str(i), "callback_data": "{} {}".format(callbk_data, " ".join([subscri[idx] for idx in index]))})
            if len(tmp) == row_len:
                result.append(tmp)
                tmp = []
            i += 1
        if tmp:
            result.append(tmp)

        return result

    @classmethod
    def __make_numeric_button_category(cls, callbk_data, array, start, lent, row_len):
        i = 1
        result = []
        tmp = []
        keys = []
        for subscri in array[start: start + lent]:
            if subscri[5] not in keys:
                tmp.append({"text": str(i), "callback_data": "{} {}".format(callbk_data, subscri[5])})
                keys.append(subscri[5])
                i += 1
            if len(tmp) == row_len:
                result.append(tmp)
                tmp = []

        if tmp:
            result.append(tmp)

        return result

    def __make_navigation_button(self, command, page, length, dtime=None):
        # remove <page_index>
        # list <page_index>
        # mute <page_index> <time>
        # halt <page_index> <time>
        # pause <page_index> <time>
        page_minus = page - self.SUB_X_PAGE
        page_plus = page + self.SUB_X_PAGE
        if dtime is None:
            dtime = ""
        else:
            dtime = " {}".format(dtime)

        temp_motion_button = []
        if page_minus >= 0:
            temp_motion_button.append({"text": "«", "callback_data": "{} {}{}".format(command, page_minus, dtime)})

        if page_plus < length:
            temp_motion_button.append({"text": "»", "callback_data": "{} {}{}".format(command, page_plus, dtime)})

        return temp_motion_button

    @classmethod
    def __make_time_button(cls, command, day, page):
        temp_button = []
        # prima fila di bottoni per i giorni
        temp_row_button = []
        temp_row_button.append({"text": "{}1 Day".format("✔ " if day == 1 else ""), "callback_data": "{} {} {}".format(command, page, 1)})
        temp_row_button.append({"text": "{}3 Days".format("✔ " if day == 3 else ""), "callback_data": "{} {} {}".format(command, page, 3)})
        temp_button.append(temp_row_button)

        # seconda fila dei bottoni per i giorni
        temp_row_button = []
        temp_row_button.append({"text": "{}7 Days".format("✔ " if day == 7 else ""), "callback_data": "{} {} {}".format(command, page, 7)})
        temp_row_button.append({"text": "{}Reset state".format("✔ " if day == 0 else ""), "callback_data": "{} {} {}".format(command, page, 0)})
        temp_button.append(temp_row_button)

        return temp_button

    def __textmessage(self, index, user_subscriptions, keys, txt_prepend="", by_enum=False, enum_by_key=False):
        user_subscriptions_len = len(user_subscriptions)

        # Verifico che l'indice di pagina non superi la lunghezza massima stabilita,
        # se tale valore viene superato, allora verrà impostato il più alto indice di pagina
        if index > user_subscriptions_len - 1:
            page_idx = ((user_subscriptions_len - 1) // self.SUB_X_PAGE) * self.SUB_X_PAGE
        else:
            page_idx = index

        txt_prepend += self.__indent_array_table(user_subscriptions, page_idx, self.SUB_X_PAGE, keys, by_enum, enum_by_key)
        txt_prepend += "\nPage {} of {}".format(
            page_idx // self.SUB_X_PAGE + 1,
            (user_subscriptions_len - 1) // self.SUB_X_PAGE + 1
        )
        return txt_prepend, page_idx

    @classmethod
    def __indent_array_table(cls, array, start, lent, key_index, by_enum=False, enum_by_key=False):
        # subscri[0] -> social
        # subscri[1] -> title
        # subscri[2] -> internal_id
        # subscri[3] -> status
        # subscri[4] -> expire_date
        # subscri[5] -> category (opzionale)
        result = ""
        key_value = [None] * len(key_index)
        counter = 1
        for subscri in array[start: start + lent]:
            indent = 0
            sub_key = False  # Controllo per reinterare la stampa delle sottochiavi
            for i, item in enumerate(key_index):
                if subscri[item] != key_value[i] or sub_key:
                    indents = ' ' * indent
                    if by_enum and enum_by_key and item == key_index[0]:
                        result += "<b>{}{} {}</b>\n".format(indents, cls.__replace_all(str(counter), cls.NUMBER_DICT), cls.__truncate(subscri[item]))
                        counter += 1
                    else:
                        result += "<b>{}• {}</b>\n".format(indents, cls.__truncate(subscri[item]))

                    key_value[i] = subscri[item]
                    sub_key = True
                indent += 2
            indents = ' ' * indent
            if subscri[4] <= int(time.time()):
                # If expire_date <= date.now
                # significa che lo stato è già scaduto quindi
                # visualizziamo semplicemente l'elemento
                if by_enum and not enum_by_key:
                    result += "{}{} {}\n".format(indents, cls.__replace_all(str(counter), cls.NUMBER_DICT), cls.__truncate(subscri[1]))
                    counter += 1
                else:
                    result += "{}• {}\n".format(indents, cls.__truncate(subscri[1]))
            else:
                # Lo stato non è ancora scaduto, dobbiamo visualizzare lo stato
                if by_enum and not enum_by_key:
                    result += "{}{} {} {}\n".format(indents, cls.__replace_all(str(counter), cls.NUMBER_DICT), cls.__replace_all(str(subscri[3]), cls.STATUS_DICT), cls.__truncate(subscri[1]))
                    counter += 1
                else:
                    result += "{}• {} {}\n".format(indents, cls.__replace_all(str(subscri[3]), cls.STATUS_DICT), cls.__truncate(subscri[1]))

        return result

    @classmethod
    def __replace_all(cls, text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

    @classmethod
    def __truncate(cls, text):
        if len(text) > cls.LINE_LIMIT:
            text = "{}...".format(text[:cls.LINE_LIMIT - 3])
        return text

    @classmethod
    def __mk_list_op_json(cls, op_tuples):
        op_list = []
        tmp_role_pos_in_list = {}
        for operator in op_tuples:
            if operator[1] not in tmp_role_pos_in_list:
                tmp_role_pos_in_list[operator[1]] = len(op_list)
                op_list.append({"name": operator[1], "nodes": []})
            op_list[tmp_role_pos_in_list[operator[1]]]["nodes"].append({"name": operator[0], "data": {"username": operator[2]}})
        return op_list

    @classmethod
    def __mk_list_op_decorate(cls, op_list):
        for role in op_list:
            role["name"] = cls.__replace_all(str(role["name"]), cls.ROLES_P)
            i = 0
            for node in role["nodes"]:
                role["nodes"][i]["name"] = "<a href='tg://user?id={0}'>{1}</a>".format(node["name"], node["data"]["username"] if node["data"]["username"] else node["name"])
                i += 1
        return op_list

    # List structure:
    # v1.0 [{"nodes": ["a", "b"], "name": "Operator"}, {"nodes": ["c", "d"], "name": "Moderator"}]
    # v2.0 [{"nodes": [{"name": "0123456789", data: {"username": "testUser1"}}], "name": "Operator"}, {"nodes": [{"name": "9876543210", data: {"username": "testUser2"}}], "name": "Moderator"}]
    @classmethod
    def __mk_list(cls, op_list):
        txt = ""
        for role in op_list:
            txt += "<b>{}</b>\n".format(role["name"])
            for node in role["nodes"]:
                txt += "{}• {}\n".format(" " * 2, node["name"])
        return txt

    def __unsubscription(self, sub, user_id):
        # Spostare fuori questo dizionario
        social_abilited = {"instagram": "instagram", "ig": "instagram"}

        # Check if there's enough data
        if not ((sub["social"] and sub["username"]) or (sub["social"] and sub["internal_id"])):
            return {"ok": False, "description": "notEnoughData"}

        # Check if social is abilited
        if sub["social"] in social_abilited:
            sub["social"] = social_abilited[sub["social"]]  # Uniforma tutti gli alias dei social ad un unico nome
        else:
            return {"ok": False, "description": "socialNotAbilitedOrMisstyped"}

        # Check if user is subscribed to the issued sn profile
        # if it is subscribed it returns the internal_id otherwise None
        if sub["internal_id"] is None:
            is_subscribed, sub["internal_id"] = self.__db.check_if_subscribed(user_id, sub["social"], username=sub["username"])
        else:
            is_subscribed, _ = self.__db.check_if_subscribed(user_id, sub["social"], internal_id=sub["internal_id"])

        # If subscribed then unsubscribe, otherwise return error
        if is_subscribed:
            if self.__db.unfollow_social_account(user_id, sub["social"], sub["internal_id"]):
                response = {"ok": True, "description": "unsubscribed"}
            else:
                response = {"ok": False, "description": "userNotSubscribed"}  # It happens only if between the check and the deleted the subscription is deleted by an nother istance/thread (it basically never happens)
        else:
            response = {"ok": False, "description": "userNotSubscribed"}
        return response

    def __iscrizione(self, sub, user_id):
        # Spostare fuori questo dizionario
        social_abilited = {"instagram": "instagram", "ig": "instagram"}

        # Check if there's enough data
        if not ((sub["social"] and sub["username"]) or sub["link"]):
            return None

        # Check user's number of subscriptions
        user_subs = self.__db.check_number_subscribtions(user_id)
        if user_subs["actual_registrations"] >= user_subs["max_registrations"]:
            return "Max subs limit reached"

        # Extracts from string URL all data possible
        sub = self.__check_url_validity(sub)
        if not sub["social"]:
            return None

        # Check if social is abilited
        if sub["social"] in social_abilited:
            sub["social"] = social_abilited[sub["social"]]  # Uniforma tutti gli alias dei social ad un unico nome
        else:
            return "Social not abilited or mistyped"

        # Extract partial data locally on supported socials
        sub["subStatus"] = "social_id_not_present"
        social_user_search_supported = {"instagram": None}
        if (sub["username"] or sub["internal_id"]) and (sub["social"] in social_user_search_supported):
            sub = self.__db.get_first_social_id_from_internal_user_social_and_if_present_subscribe(user_id, sub, False)

        # È uguale a: sub["subStatus"] == "notInDatabase" or sub["subStatus"] == "internalId_or_username_not_present"
        # Check if from your local data (db and url string) you've been able to extract the social_id
        # Note1: If you have social_id means that it's also already in the database, ergo: it has already been processed
        # Note2: Significa che a questo punto hai fatto del tuo meglio per estrarre i dati localmente, e ti trovi di fronte a tre casi:
        # 1) È stato inserito un link da cui è impossibile estrarre la username o l'id interno (il social lo si riesce ad estrarre sempre)
        # 2) I dati estratti non hanno trovato riscontro nel database locale, quindi è necessario ricercare online
        # 3) I dati estratti hanno trovato riscontro nel database e l'utente è risultato O già iscritto O non ancora iscritto, in quest'ultimo
        #    caso l'untente viene automaticamente iscritto subito e questo if viene saltato
        if not sub["social_id"]:
            # Extract data online
            sub = self.__extract_data_social(sub)
            # If exists, check if already in the database
            # If in the database subscribe, else add and subscribe
            if sub["subStatus"] == "subscribable":
                sub = self.__db.get_first_social_id_from_internal_user_social_and_if_present_subscribe(user_id, sub, True)

        if sub["subStatus"] == "JustSubscribed" or sub["subStatus"] == "CreatedSocialAccAndSubscribed":
            if sub["status"] == "public":
                text = "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"
            elif sub["status"] == "private":
                text = "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou've been subscribed to a social account that is private!\nYou'll not receive feeds until it switches to public!"
            else:
                text = "Social: " + str(sub["social"]) + "\nUser: " + str(sub["title"]) + "\nMmmh, something went really wrong, the status is unknown :/\nYou should get in touch with the admin!"
        elif sub["subStatus"] == "AlreadySubscribed":
            text = "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou're already subscribed to this account!"
        elif sub["subStatus"] == "NotExists":
            text = "Social: " + sub["social"] + "\nThis account doesn't exists!"
        elif sub["subStatus"] == "NotExistsOrPrivate":
            text = "Social: " + sub["social"] + "\nThis account doesn't exists or is private!"
        elif sub["subStatus"] == "noSpecificMethodToExtractData" or sub["subStatus"] == "noMethodToExtractData":
            text = "Social: " + str(sub["social"]) + "\nMmmh, this shouldn't happen, no method (or specific method) to extract data."
        else:
            text = "Social: " + str(sub["social"]) + "\nI don't know what happened! O_o\""
        return text

    def __set_sub_state(self, sub, user_id, state, exp_time):
        # Spostare fuori questo dizionario
        social_abilited = {"instagram": "instagram", "ig": "instagram"}

        # Check if there's enough data
        if not ((sub["social"] and sub["username"]) or (sub["social"] and sub["internal_id"])):
            return {"ok": False, "description": "notEnoughData"}

        # Check if social is abilited
        if sub["social"] in social_abilited:
            sub["social"] = social_abilited[sub["social"]]  # Uniforma tutti gli alias dei social ad un unico nome
        else:
            return {"ok": False, "description": "socialNotAbilitedOrMisstyped"}

        # Check if user is subscribed to the issued sn profile
        # if it is subscribed it returns the internal_id otherwise None
        if sub["internal_id"] is None:
            is_subscribed, sub["internal_id"] = self.__db.check_if_subscribed(user_id, sub["social"], username=sub["username"])
        else:
            is_subscribed, _ = self.__db.check_if_subscribed(user_id, sub["social"], internal_id=sub["internal_id"])

        if int(exp_time[:-1]) != 0:
            if exp_time[-1:] == "d":
                exp_time = int(exp_time[:-1])
                exp_time = int(time.time()) + exp_time * 86400
            elif exp_time[-1:] == "h":
                exp_time = int(exp_time[:-1])
                exp_time = int(time.time()) + exp_time * 3600
            else:
                return {"ok": False, "description": "errorOnTimeFormat"}  # Caso impossibile da finirci dato il controllo della regexp ma messo per sicurezza
        else:
            exp_time = -1
            state = 0
        # If subscribed then unsubscribe, otherwise return error
        if is_subscribed:
            if self.__db.set_state_of_social_account(user_id, sub["social"], sub["internal_id"], state, exp_time):
                response = {"ok": True, "description": "changedState"}
            else:
                response = {"ok": False, "description": "userNotSubscribed"}  # It happens only if between the check and the deleted the subscription is deleted by an nother istance/thread (it basically never happens)
        else:
            response = {"ok": False, "description": "userNotSubscribed"}
        return response

    def __set_cat_state(self, user_id, category, state, exp_time):

        if int(exp_time[:-1]) != 0:
            if exp_time[-1:] == "d":
                exp_time = int(exp_time[:-1])
                exp_time = int(time.time()) + exp_time * 86400
            elif exp_time[-1:] == "h":
                exp_time = int(exp_time[:-1])
                exp_time = int(time.time()) + exp_time * 3600
            else:
                return {"ok": False, "description": "errorOnTimeFormat"}  # Caso impossibile da finirci dato il controllo della regexp ma messo per sicurezza
        else:
            exp_time = -1
            state = 0

        if self.__db.set_state_of_category(user_id, category, state, exp_time):
            response = {"ok": True, "description": "changedState"}
        else:
            response = {"ok": False, "description": "userMissCategory"}  # It happens only if between the check and the deleted the subscription is deleted by an nother istance/thread (it basically never happens)
        return response

    def __set_sub_category(self, sub, user_id, category):
        # Spostare fuori questo dizionario
        social_abilited = {"instagram": "instagram", "ig": "instagram"}

        # Check if there's enough data
        if not ((sub["social"] and sub["username"]) or (sub["social"] and sub["internal_id"])):
            return {"ok": False, "description": "notEnoughData"}

        # Check if social is abilited
        if sub["social"] in social_abilited:
            sub["social"] = social_abilited[sub["social"]]  # Uniforma tutti gli alias dei social ad un unico nome
        else:
            return {"ok": False, "description": "socialNotAbilitedOrMisstyped"}

        # Check if user is subscribed to the issued sn profile
        # if it is subscribed it returns the internal_id otherwise None
        if sub["internal_id"] is None:
            is_subscribed, sub["internal_id"] = self.__db.check_if_subscribed(user_id, sub["social"], username=sub["username"])
        else:
            is_subscribed, _ = self.__db.check_if_subscribed(user_id, sub["social"], internal_id=sub["internal_id"])

        # If subscribed then unsubscribe, otherwise return error
        if is_subscribed:
            if self.__db.set_category_of_social_account(user_id, sub["social"], sub["internal_id"], category):
                response = {"ok": True, "description": "changedState"}
            else:
                response = {"ok": False, "description": "userNotSubscribed"}  # It happens only if between the check and the deleted the subscription is deleted by an nother istance/thread (it basically never happens)
        else:
            response = {"ok": False, "description": "userNotSubscribed"}
        return response

    def __check_url_validity(self, sub):
        if sub["link"]:
            sub["data"] = {}
            # Instagram
            tmp = self.__re_link["instagram"]["p"].search(sub["link"])
            if tmp:
                sub["social"] = "instagram"
                sub["link"] = tmp.group(0)
                sub["data"]["p"] = tmp.group(1)
                return sub
            tmp = self.__re_link["instagram"]["username"].search(sub["link"])
            if tmp:
                sub["social"] = "instagram"
                sub["link"] = tmp.group(0)
                sub["username"] = tmp.group(1)
                return sub
        return sub

    def __extract_data_social(self, sub):
        if sub["social"] == "instagram":
            sub = self.__socials[0].extract_data(sub)
        return sub

    def __re_compiler(self):
        self.__re_link = {}

        # Instagram
        self.__re_link["instagram"] = {}
        self.__re_link["instagram"]["p"] = re.compile(r"(?:https:\/\/www\.|www\.)?instagram\.com\/p\/([A-Za-z0-9-_]{1,30})")
        self.__re_link["instagram"]["username"] = re.compile(r"(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")
