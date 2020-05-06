#!/usr/bin/env python3

import test.constants as cnst

from os import path, remove
from unittest.mock import patch
import copy

from feedgram.lib.process_input import Processinput
from feedgram.lib.database import MyDatabase
from feedgram.social.instagram import Instagram


# Instanzio il database che utilizzarà il process input
DATABASE_PATH = "./test/processinputTest.sqlite3"


def test_stop_not_registred():

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(DATABASE_PATH):
        try:
            remove(DATABASE_PATH)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: %s - %s." % (err.filename, err.strerror))

    assert not path.exists(DATABASE_PATH)

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico che il messaggio di risposta sia coretto
    assert result[0]["text"] == "You're not registered, type /start to subscribe!"


def test_start_not_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "Congratulations, you're now registered!\nType /help to learn the commands available!"


def test_start_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're alredy registred.\nType /help to learn the commands available!"


def test_wrong_command():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.WRONG_COMMAND)

    assert result[0]["type"] == "sendMessage"
    assert cnst.WRONG_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "Unrecognized command"


def test_help_command():

    msm_help = ("📖 Help\n\nYou can follow up to <i>10 social accounts</i>.\n"
                "Socials currently supported:\n"
                " • <i>Instagram</i>\n"
                "You can follow only <b>public</b> accounts.\n"
                "\n"
                "<b>Receive Feeds:</b>\n"
                " • /sub <i>social</i> <i>username</i>\n"
                " • /sub <i>link</i>\n"
                "<b>Bot:</b>\n"
                " • /stop to stop and unsubscribe from the bot.")

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_HELP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_HELP["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_help


def test_not_command_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.NOT_COMMAND)

    assert result[0]["type"] == "sendMessage"
    assert cnst.NOT_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "[AUTHORIZED] You can send text only!"


def test_callback_help():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_HELP)

    assert result[0]["type"] == "answerCallbackQuery"
    assert result[0]["text"] == "Help"

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_HELP["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_HELP["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_HELP["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_HELP["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


GLOBAL_EXTRCT_DATA_RETURN = None


def dummy_instagram_extract_data(_):
    global GLOBAL_EXTRCT_DATA_RETURN
    # print(sn_account)
    return GLOBAL_EXTRCT_DATA_RETURN

# `/sub <social> <username>` command
# What respectively does at each cycle:
# 1) Asking to subscribe to social profile A
# 2) I'm subscribed to A, but I ask again to subscribe to A
# 3) Badly formatted /sub command
# 4) Asking to subscribe to an inexistent account
# 5) Forcing an unexpected "subStatus" from the social Module
# 6) Subscribing to a social profile that has the "private" status
# 7) Forcing an unexpected "status" from the social Module
# 8) Invalid social issued


def test_sub_command_social_username():
    global GLOBAL_EXTRCT_DATA_RETURN
    with patch('feedgram.social.instagram.Instagram.extract_data', side_effect=dummy_instagram_extract_data):
        database = MyDatabase(DATABASE_PATH)
        igram = Instagram()
        myprocess_input = Processinput(database, [igram])

        queries = [cnst.MSG_CMD_SUB_STANDARD,
                   cnst.MSG_CMD_SUB_AGAIN,
                   cnst.MSG_CMD_SUB_BAD_FORMAT,
                   cnst.MSG_CMD_SUB_NO_EXIST,
                   cnst.MSG_CMD_SUB_UNXPCTD_SUB_STATUS,
                   cnst.MSG_CMD_SUB_PRIVATE,
                   cnst.MSG_CMD_SUB_UNXPCTD_STATUS,
                   cnst.MSG_CMD_SUB_INVALID_SOCIAL]

        for query in queries:
            GLOBAL_EXTRCT_DATA_RETURN = query["response"]
            result = myprocess_input.process(query["query"])
            assert result[0] == query["result"][0]


# `/sub <link>` command
# What respectively does at each cycle:
# 1) Subscribe using the URL of the home of the social profile
# 2) Use a link that cannot determine if the profile esists or is private
# 3) The link returns a no specific method to retreive the ifo
# 4) Use a valid link pointing to an unrecognized service
def test_sub_command_url():
    global GLOBAL_EXTRCT_DATA_RETURN
    with patch('feedgram.social.instagram.Instagram.extract_data', side_effect=dummy_instagram_extract_data):
        database = MyDatabase(DATABASE_PATH)
        igram = Instagram()
        myprocess_input = Processinput(database, [igram])

        queries = [cnst.MSG_CMD_SUB_IG_HOME,
                   cnst.MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV,
                   cnst.MSG_CMD_SUB_IG_P_NO_SPEC_MTHD,
                   cnst.MSG_CMD_SUB_INVALID_URL]

        for query in queries:
            GLOBAL_EXTRCT_DATA_RETURN = query["response"]
            result = myprocess_input.process(query["query"])
            assert result[0] == query["result"][0]


COMMAND_LIST = {
    "ok": True,
    "result": [
        {
            "update_id": 731419465,
            "message": {
                "message_id": 1257,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "date": 1587049603,
                "text": "/list",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
    ],
}
CALLBACK_LIST_PAGE_1 = {
    "ok": True,
    "result": [
        {
            "update_id": 731420180,
            "callback_query": {
                "id": "268511788082888011",
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 2120,
                    "from": {
                        "id": 987654321,
                        "is_bot": True,
                        "first_name": "TestbotID",
                        "username": "Territory_ID_Bot"
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private"
                    },
                    "date": 1588349911,
                    "text": "👥Follow List\n                                                  \nYou are following: \n<b>• instagram</b>\n  • testProfile\n  • testProfilePrivate\n  • testProfileStrangeStatus\n  • testIgProfileLinkHome\n  • testProfile2\n  • testProfile3\n\nPage 1 of 2",
                    "entities": [
                        {
                            "offset": 30,
                            "length": 18,
                            "type": "italic"
                        },
                        {
                            "offset": 82,
                            "length": 9,
                            "type": "italic"
                        },
                        {
                            "offset": 112,
                            "length": 6,
                            "type": "bold"
                        },
                        {
                            "offset": 130,
                            "length": 14,
                            "type": "bold"
                        },
                        {
                            "offset": 148,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 153,
                            "length": 6,
                            "type": "italic"
                        },
                        {
                            "offset": 160,
                            "length": 8,
                            "type": "italic"
                        },
                        {
                            "offset": 172,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 177,
                            "length": 4,
                            "type": "italic"
                        },
                        {
                            "offset": 182,
                            "length": 4,
                            "type": "bold"
                        },
                        {
                            "offset": 190,
                            "length": 5,
                            "type": "bot_command"
                        }
                    ],
                    "reply_markup": {
                        "inline_keyboard": [
                            [{'callback_data': 'list_mode 6', 'text': '»'}],
                            [
                                {
                                    "text": "⏯️",
                                    "callback_data": "pause_mode"
                                },
                                {
                                    "text": "🔕",
                                    "callback_data": "notifications_mode_off"
                                },
                                {
                                    "text": "⏹",
                                    "callback_data": "stop_mode"
                                },
                                {
                                    "text": "🗑",
                                    "callback_data": "remove"
                                }
                            ],
                            [{"text": "📖", "callback_data": "help_mode"}]
                        ]
                    }
                },
                "chat_instance": "4557971575337840976",
                "data": "list_mode"
            }
        }],
}
CALLBACK_LIST_PAGE_2 = {
    "ok": True,
    "result": [
        {
            "update_id": 731420180,
            "callback_query": {
                "id": "268511788082888011",
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 2120,
                    "from": {
                        "id": 987654321,
                        "is_bot": True,
                        "first_name": "TestbotID",
                        "username": "Territory_ID_Bot"
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private"
                    },
                    "date": 1588349911,
                    "text": "👥Follow List\n                                                  \nYou are following: \n<b>• instagram</b>\n  • testProfile4\n\nPage 2 of 2",
                    "entities": [
                        {
                            "offset": 30,
                            "length": 18,
                            "type": "italic"
                        },
                        {
                            "offset": 82,
                            "length": 9,
                            "type": "italic"
                        },
                        {
                            "offset": 112,
                            "length": 6,
                            "type": "bold"
                        },
                        {
                            "offset": 130,
                            "length": 14,
                            "type": "bold"
                        },
                        {
                            "offset": 148,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 153,
                            "length": 6,
                            "type": "italic"
                        },
                        {
                            "offset": 160,
                            "length": 8,
                            "type": "italic"
                        },
                        {
                            "offset": 172,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 177,
                            "length": 4,
                            "type": "italic"
                        },
                        {
                            "offset": 182,
                            "length": 4,
                            "type": "bold"
                        },
                        {
                            "offset": 190,
                            "length": 5,
                            "type": "bot_command"
                        }
                    ],
                    "reply_markup": {
                        "inline_keyboard": [
                            [{'callback_data': 'list_mode 0', 'text': '«'}],
                            [
                                {
                                    "text": "⏯️",
                                    "callback_data": "pause_mode"
                                },
                                {
                                    "text": "🔕",
                                    "callback_data": "notifications_mode_off"
                                },
                                {
                                    "text": "⏹",
                                    "callback_data": "stop_mode"
                                },
                                {
                                    "text": "🗑",
                                    "callback_data": "remove"
                                }
                            ],
                            [{"text": "📖", "callback_data": "help_mode"}]
                        ]
                    }
                },
                "chat_instance": "4557971575337840976",
                "data": "list_mode 6"
            }
        }],
}
CALLBACK_LIST_PAGE_3 = {
    "ok": True,
    "result": [
        {
            "update_id": 731420180,
            "callback_query": {
                "id": "268511788082888011",
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 2120,
                    "from": {
                        "id": 987654321,
                        "is_bot": True,
                        "first_name": "TestbotID",
                        "username": "Territory_ID_Bot"
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private"
                    },
                    "date": 1588349911,
                    "text": "👥Follow List\n                                                  \nYou are following: \n<b>• instagram</b>\n  • testProfile4\n\nPage 2 of 2",
                    "entities": [
                        {
                            "offset": 30,
                            "length": 18,
                            "type": "italic"
                        },
                        {
                            "offset": 82,
                            "length": 9,
                            "type": "italic"
                        },
                        {
                            "offset": 112,
                            "length": 6,
                            "type": "bold"
                        },
                        {
                            "offset": 130,
                            "length": 14,
                            "type": "bold"
                        },
                        {
                            "offset": 148,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 153,
                            "length": 6,
                            "type": "italic"
                        },
                        {
                            "offset": 160,
                            "length": 8,
                            "type": "italic"
                        },
                        {
                            "offset": 172,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 177,
                            "length": 4,
                            "type": "italic"
                        },
                        {
                            "offset": 182,
                            "length": 4,
                            "type": "bold"
                        },
                        {
                            "offset": 190,
                            "length": 5,
                            "type": "bot_command"
                        }
                    ],
                    "reply_markup": {
                        "inline_keyboard": [
                            [{'callback_data': 'list_mode 0', 'text': '«'}],
                            [
                                {
                                    "text": "⏯️",
                                    "callback_data": "pause_mode"
                                },
                                {
                                    "text": "🔕",
                                    "callback_data": "notifications_mode_off"
                                },
                                {
                                    "text": "⏹",
                                    "callback_data": "stop_mode"
                                },
                                {
                                    "text": "🗑",
                                    "callback_data": "remove"
                                }
                            ],
                            [{"text": "📖", "callback_data": "help_mode"}]
                        ]
                    }
                },
                "chat_instance": "4557971575337840976",
                "data": "list_mode 24"
            }
        }],
}

MSG_CMD_SUB_STANDARD = {
    "query": {
        "ok": True,
        "result": [
            {
                "update_id": 12345,
                "message": {
                    "message_id": 1256,
                    "from": {
                        "id": 123456789,
                        "is_bot": False,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "language_code": "en",
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private",
                    },
                    "dte": 159753,
                    "text": "/sub instagram testProfile",
                    "entities": [{"offset": 0, "length": 1, "type": "bot_command"}],
                },
            }
        ],
    },
    "response": {
        "social": "instagram",
        "username": "testProfile",
        "internal_id": 546545337,
        "title": "testProfile",
        "subStatus": "subscribable",
        "status": "public",
        "link": None,
        "data": {
        }
    },
    "result": [
        {
            "type": "sendMessage",
            "chat_id": 123456789,
            "markdown": "HTML",
            "text": "Social: instagram\nUser: testProfile\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"
        }
    ]
}

MSG_CMD_SUB_STANDARD_2 = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_STANDARD_2["query"]["result"][0]["message"]["text"] = "/sub instagram testProfile2"
MSG_CMD_SUB_STANDARD_2["response"] = {
    "social": "instagram",
    "username": "testProfile2",
    "internal_id": 4345345,
    "title": "testProfile2",
    "subStatus": "subscribable",
    "status": "public",
    "link": None,
    "data": {}
}

MSG_CMD_SUB_STANDARD_3 = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_STANDARD_3["query"]["result"][0]["message"]["text"] = "/sub instagram testProfile3"
MSG_CMD_SUB_STANDARD_3["response"] = {
    "social": "instagram",
    "username": "testProfile3",
    "internal_id": 782782767,
    "title": "testProfile3",
    "subStatus": "subscribable",
    "status": "public",
    "link": None,
    "data": {
    }
}

MSG_CMD_SUB_STANDARD_4 = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_STANDARD_4["query"]["result"][0]["message"]["text"] = "/sub instagram testProfile4"
MSG_CMD_SUB_STANDARD_4["response"] = {
    "social": "instagram",
    "username": "testProfile4",
    "internal_id": 456765579,
    "title": "testProfile4",
    "subStatus": "subscribable",
    "status": "public",
    "link": None,
    "data": {
    }
}


def test_list_comand():

    # Aggungo ulteriori sottoscrizioni in modo da poter testare le pagine
    global GLOBAL_EXTRCT_DATA_RETURN
    with patch('feedgram.social.instagram.Instagram.extract_data', side_effect=dummy_instagram_extract_data):
        database = MyDatabase(DATABASE_PATH)
        igram = Instagram()
        myprocess_input = Processinput(database, [igram])

        queries = [MSG_CMD_SUB_STANDARD_2,
                   MSG_CMD_SUB_STANDARD_3,
                   MSG_CMD_SUB_STANDARD_4]

        for query in queries:
            GLOBAL_EXTRCT_DATA_RETURN = query["response"]
            result = myprocess_input.process(query["query"])

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(COMMAND_LIST)

    msm_list = ("👥Follow List\n"
                "                                                  "
                "\nYou are following: \n"
                "<b>• instagram</b>\n"
                "  • testProfile\n"
                "  • testProfilePrivate\n"
                "  • testProfileStrangeStatus\n"
                "  • testIgProfileLinkHome\n"
                "  • testProfile2\n"
                "  • testProfile3\n\n"
                "Page 1 of 2")

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_LIST["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_callback_list_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(CALLBACK_LIST_PAGE_1)

    assert result[0]["type"] == "answerCallbackQuery"
    assert result[0]["text"] == "Following list"

    assert result[1]["type"] == "editMessageText"
    assert CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_callback_list_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(CALLBACK_LIST_PAGE_2)

    assert result[0]["type"] == "editMessageText"
    assert CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_callback_list_old_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(CALLBACK_LIST_PAGE_3)

    assert result[0]["type"] == "editMessageText"
    assert CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_stop_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're no longer subscribed!\nWe already <i>miss</i> you, please come back soon! 😢\nTip: In order to re-joyn type /start *wink* *wink*"
