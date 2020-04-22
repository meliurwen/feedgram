#!/usr/bin/env python3

import test.constants as cnst

from os import path, remove
from unittest.mock import patch

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


def test_stop_registred():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're no longer subscribed!\nWe already <i>miss</i> you, please come back soon! 😢\nTip: In order to re-joyn type /start *wink* *wink*"
