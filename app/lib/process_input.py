#!/usr/bin/env python3
import logging


class Processinput:

    def __init__(self, database):
        self.__logger = logging.getLogger('telegram_bot.process_input')
        self.__db = database

    # Big message
    __msm_stop = ("You're no longer subscribed!\n"
                  "We already <i>miss</i> you, please come back soon! 😢\n"
                  "Tip: In order to re-joyn type /start *wink* *wink*")

    __msm_help = ("📖Help\n\nYou can follow up to <i>10 social accounts</i>.\n"
                  "Socials currently supported:\n"
                  " • <i>Instagram</i>\n"
                  "You can follow only <b>public</b> accounts.\n"
                  "\n"
                  "<b>Receive Feeds:</b>\n"
                  " • /sub <i>social</i> <i>username</i>\n"
                  " • /sub <i>link</i>\n"
                  "/stop to stop and unsubscribe from the bot.\n"
                  "That's all. :)")

    def process(self, updates):
        messages = []
        for update in updates["result"]:
            mss_type = None
            if 'message' in update:
                mss_type = "message"
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
                                        messages.append(self.__ms_maker(chat_id, "Something bad happened, you're STILL registered!\nTry again later." ))
                                    else:
                                        messages.append(self.__ms_maker(chat_id, self.__msm_stop, "HTML"))
                                elif text == "/help":
                                    tets = self.__ms_maker(chat_id, self.__msm_help, "HTML")
                                    messages.append(tets)
                                elif text == "/start":
                                    messages.append(self.__ms_maker(chat_id, "You're alredy registred.\nType /help to learn the commands available!"))
                                else:
                                    messages.append(self.__ms_maker(chat_id, "Unrecognized command"))
                        # "chat_id":chat_id non è prevista dalle API di Telegram per answerCallbackQuery, serve solo alla funzione Telegram.send_messages(coda, condizione)
                        # che si basa sul parametro "chat_id" per schedualare i messaggi da inviare
                        # TODO: Togliere i chat_id inutili non appena è stato risolto il problema nel send_messages perché questa è una soluzione triste (ma non troppo)
                        # NOTA: Mi sa che questa "soluzione triste" rimarrà così per sempre, od almeno finchè Telegram non rilascerà specifiche più dettagliate.
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
