#!/usr/bin/env python3
from os import path, remove
import copy
from unittest.mock import patch

from feedgram.lib.process_input import Processinput
from feedgram.lib.database import MyDatabase
from feedgram.social.instagram import Instagram

COMMAND_START = {
    "ok": True,
    "result": [
        {
            "update_id": 731419464,
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
                "dte": 1587049598,
                "text": "/start",
                "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
            },
        }
    ],
}

COMMAND_STOP = {
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
                "text": "/stop",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
    ],
}

NOT_COMMAND = {
    "ok": True,
    "result": [
        {
            "update_id": 731419483,
            "message": {
                "message_id": 1292,
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
                "date": 1587065931,
                "sticker": {
                    "width": 512,
                    "height": 444,
                    "emoji": "\ud83d\ude4f",
                    "set_name": "Animushit",
                    "is_animated": False,
                    "thumb": {
                        "file_id": "AAMCBAADGQEAAgUMXpi0S9HRxQd2Wqrpb0g3ekOugrMAAogAA4j_wBXpMkiwXLg5zwABbeAZAAQBAAdtAAM3NQACGAQ",
                        "file_unique_id": "AQAEbeAZAAQ3NQAC",
                        "file_size": 4334,
                        "width": 128,
                        "height": 111,
                    },
                    "file_id": "CAACAgQAAxkBAAIFDF6YtEvR0cUHdlqq6W9IN3pDroKzAAKIAAOI_8AV6TJIsFy4Oc8YBA",
                    "file_unique_id": "AgADiAADiP_AFQ",
                    "file_size": 44914,
                },
            },
        }
    ],
}

WRONG_COMMAND = {
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
                "text": "/stops",
                "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
            },
        }
    ],
}


COMMAND_HELP = {
    "ok": True,
    "result": [
        {
            "update_id": 731419464,
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
                "dte": 1587049598,
                "text": "/help",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
    ],
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
            "text": "Social: instagram\nUser: testProfile\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"
        }
    ]
}

MSG_CMD_SUB_BAD_FORMAT = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_BAD_FORMAT["query"]["result"][0]["message"]["text"] = "/sub potato"
MSG_CMD_SUB_BAD_FORMAT["response"] = {}

MSG_CMD_SUB_BAD_FORMAT["result"][0]["text"] = "/sub command badly compiled"


MSG_CMD_SUB_AGAIN = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_AGAIN["result"][0]["text"] = "Social: instagram\nUser: testProfile\nYou're already subscribed to this account!"

MSG_CMD_SUB_NO_EXIST = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_NO_EXIST["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileInexistent"
MSG_CMD_SUB_NO_EXIST["response"] = {
    "social": "instagram",
    "username": "testProfileInexistent",
    "subStatus": "NotExists",
    "status": "unknown",
    "data": {
    }
}
MSG_CMD_SUB_NO_EXIST["result"][0]["text"] = "Social: instagram\nThis account doesn't exists!"

MSG_CMD_SUB_UNXPCTD_SUB_STATUS = copy.deepcopy(MSG_CMD_SUB_NO_EXIST)
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileImpossible"
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["response"] = {
    "social": "instagram",
    "username": "testProfileImpossible",
    "subStatus": "banana",
    "status": "unknown",
    "data": {
    }
}
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["result"][0]["text"] = "Social: instagram\nI don't know what happened! O_o\""

MSG_CMD_SUB_PRIVATE = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_PRIVATE["query"]["result"][0]["message"]["text"] = "/sub instagram testProfilePrivate"
MSG_CMD_SUB_PRIVATE["response"] = {
    "social": "instagram",
    "username": "testProfilePrivate",
    "internal_id": 741852963,
    "title": "testProfilePrivate",
    "subStatus": "subscribable",
    "status": "private",
    "link": None,
    "data": {
    }
}
MSG_CMD_SUB_PRIVATE["result"][0]["text"] = "Social: instagram\nUser: testProfilePrivate\nYou've been subscribed to a social account that is private!\nYou'll not receive feeds until it switches to public!"

MSG_CMD_SUB_UNXPCTD_STATUS = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_UNXPCTD_STATUS["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileStrangeStatus"
MSG_CMD_SUB_UNXPCTD_STATUS["response"] = {
    "social": "instagram",
    "username": "testProfileStrangeStatus",
    "internal_id": 963852741,
    "title": "testProfileStrangeStatus",
    "subStatus": "subscribable",
    "status": "banana",
    "link": None,
    "data": {
    }
}
MSG_CMD_SUB_UNXPCTD_STATUS["result"][0]["text"] = "Social: instagram\nUser: testProfileStrangeStatus\nMmmh, something went really wrong, the status is unknown :/\nYou should get in touch with the admin!"

MSG_CMD_SUB_IG_HOME = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_HOME["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/testIgProfileLinkHome"
MSG_CMD_SUB_IG_HOME["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkHome",
    "internal_id": 897546782,
    "title": "testIgProfileLinkHome",
    "subStatus": "subscribable",
    "status": "public",
    "link": "https://www.instagram.com/testIgProfileLinkHome",
    "data": {
    }
}
MSG_CMD_SUB_IG_HOME["result"][0]["text"] = "Social: instagram\nUser: testIgProfileLinkHome\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"

MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/p/dD8-su2dF/"
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkP",
    "subStatus": "NotExistsOrPrivate",
    "status": "unknown",
    "link": "https://www.instagram.com/p/dD8-su2dF",
    "data": {
        "p": "dD8-su2dF"
    }
}
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["result"][0]["text"] = "Social: instagram\nThis account doesn't exists or is private!"

MSG_CMD_SUB_IG_P_NO_SPEC_MTHD = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/p/Yu9Jfi8/"
del MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["from"]["username"]
del MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["chat"]["username"]
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkP",
    "subStatus": "noSpecificMethodToExtractData",
    "status": "unknown",
    "link": "https://www.instagram.com/p/Yu9Jfi8",
    "data": {
        "p": "Yu9Jfi8"
    }
}
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["result"][0]["text"] = "Social: instagram\nMmmh, this shouldn't happen, no method (or specific method) to extract data."

MSG_CMD_SUB_INVALID_URL = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_INVALID_URL["query"]["result"][0]["message"]["text"] = "/sub https://www.potato.banana"
MSG_CMD_SUB_INVALID_URL["response"] = {}
MSG_CMD_SUB_INVALID_URL["result"][0]["text"] = "/sub command badly compiled"

MSG_CMD_SUB_INVALID_SOCIAL = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_INVALID_SOCIAL["query"]["result"][0]["message"]["text"] = "/sub banana potato"
MSG_CMD_SUB_INVALID_SOCIAL["response"] = {}
MSG_CMD_SUB_INVALID_SOCIAL["result"][0]["text"] = "Social not abilited or mistyped"


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
    result = myprocess_input.process(COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico che il messaggio di risposta sia coretto
    assert result[0]["text"] == "You're not registered, type /start to subscribe!"


def test_start_not_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "Congratulations, you're now registered!\nType /help to learn the commands available!"


def test_start_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're alredy registred.\nType /help to learn the commands available!"


def test_wrong_command():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(WRONG_COMMAND)

    assert result[0]["type"] == "sendMessage"
    assert WRONG_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "Unrecognized command"


def test_help_command():

    msm_help = ("📖Help\n\nYou can follow up to <i>10 social accounts</i>.\n"
                "Socials currently supported:\n"
                " • <i>Instagram</i>\n"
                "You can follow only <b>public</b> accounts.\n"
                "\n"
                "<b>Receive Feeds:</b>\n"
                " • /sub <i>social</i> <i>username</i>\n"
                " • /sub <i>link</i>\n"
                "/stop to stop and unsubscribe from the bot.\n"
                "That's all. :)")

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(COMMAND_HELP)

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_HELP["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_help


def test_not_command_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(NOT_COMMAND)

    assert result[0]["type"] == "sendMessage"
    assert NOT_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "[AUTHORIZED] You can send text only!"


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

        queries = [MSG_CMD_SUB_STANDARD,
                   MSG_CMD_SUB_AGAIN,
                   MSG_CMD_SUB_BAD_FORMAT,
                   MSG_CMD_SUB_NO_EXIST,
                   MSG_CMD_SUB_UNXPCTD_SUB_STATUS,
                   MSG_CMD_SUB_PRIVATE,
                   MSG_CMD_SUB_UNXPCTD_STATUS,
                   MSG_CMD_SUB_INVALID_SOCIAL]

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

        queries = [MSG_CMD_SUB_IG_HOME,
                   MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV,
                   MSG_CMD_SUB_IG_P_NO_SPEC_MTHD,
                   MSG_CMD_SUB_INVALID_URL]

        for query in queries:
            GLOBAL_EXTRCT_DATA_RETURN = query["response"]
            result = myprocess_input.process(query["query"])
            assert result[0] == query["result"][0]


def test_stop_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're no longer subscribed!\nWe already <i>miss</i> you, please come back soon! 😢\nTip: In order to re-joyn type /start *wink* *wink*"
