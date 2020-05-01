#!/usr/bin/env python3
import logging
import re


class Processinput:

    def __init__(self, database, social_list):
        self.__logger = logging.getLogger('telegram_bot.process_input')
        self.__db = database
        self.__re_compiler()
        self.__socials = social_list

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
                  "<b>Bot:</b>\n"
                  " • /stop to stop and unsubscribe from the bot.")

    # inline keyboard
    __ilk_help = {"text": "📖", "callback_data": "help_mode"}

    __ilk_pause = {"text": "⏯️", "callback_data": "pause_mode"}
    __ilk_notoff = {"text": "🔕", "callback_data": "notifications_mode_off"}
    __ilk_stop = {"text": "⏹", "callback_data": "stop_mode"}
    __ilk_rem = {"text": "🗑", "callback_data": "remove"}

    __ilk_list = {"text": "📋", "callback_data": "list_mode"}
    __ilk_category = {"text": "🏷", "callback_data": "category_mode"}

    def process(self, updates):
        messages = []
        for update in updates["result"]:
            mss_type = None
            if 'message' in update:
                mss_type = "message"
            elif 'edited_message' in update:
                mss_type = "edited_message"
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

                                elif text == "/start":
                                    messages.append(self.__ms_maker(chat_id, "You're alredy registred.\nType /help to learn the commands available!"))
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
                        else:
                            messages.append(self.__ms_maker(chat_id, "[AUTHORIZED] You can send text only!"))
                    else:
                        if 'text' in update[mss_type]:
                            text = update[mss_type]["text"]
                            if text == "/start":
                                self.__db.subscribe_user(user_id, username, chat_id, 1, 10)
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
    def __ms_maker(cls, chatid, text, markdown=None, link_preview=None, notification=None, markup=None):
        temp_dict = {}

        temp_dict["type"] = "sendMessage"
        temp_dict["chat_id"] = chatid
        temp_dict["text"] = text

        # markdown <==> parser_mode di telegram
        if markdown:
            temp_dict["markdown"] = markdown

        if link_preview:
            temp_dict["disable_web_page_preview"] = link_preview

        if notification:
            temp_dict["disable_notification"] = not notification

        if markup:
            temp_dict["reply_markup"] = markup

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
    def __ms_edit(cls, chat_id, message_id, text, markdown=None, markup=None):
        temp_dict = {}

        temp_dict["type"] = "editMessageText"
        temp_dict["chat_id"] = chat_id
        temp_dict["message_id"] = message_id
        temp_dict["text"] = text

        # markdown <==> parser_mode di telegram
        if markdown:
            temp_dict["markdown"] = markdown

        if markup:
            temp_dict["reply_markup"] = markup

        return temp_dict

    def __iscrizione(self, sub, user_id):
        # Spostare fuori quessto dizionario
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
                return "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"
            elif sub["status"] == "private":
                return "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou've been subscribed to a social account that is private!\nYou'll not receive feeds until it switches to public!"
            else:
                return "Social: " + str(sub["social"]) + "\nUser: " + str(sub["title"]) + "\nMmmh, something went really wrong, the status is unknown :/\nYou should get in touch with the admin!"
        elif sub["subStatus"] == "AlreadySubscribed":
            return "Social: " + sub["social"] + "\nUser: " + sub["title"] + "\nYou're already subscribed to this account!"
        elif sub["subStatus"] == "NotExists":
            return "Social: " + sub["social"] + "\nThis account doesn't exists!"
        elif sub["subStatus"] == "NotExistsOrPrivate":
            return "Social: " + sub["social"] + "\nThis account doesn't exists or is private!"
        elif sub["subStatus"] == "noSpecificMethodToExtractData" or sub["subStatus"] == "noMethodToExtractData":
            return "Social: " + str(sub["social"]) + "\nMmmh, this shouldn't happen, no method (or specific method) to extract data."
        else:
            return "Social: " + str(sub["social"]) + "\nI don't know what happened! O_o\""

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
