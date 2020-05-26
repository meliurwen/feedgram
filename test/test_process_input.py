#!/usr/bin/env python3

import test.constants as cnst

from os import path, remove
from unittest.mock import patch

from feedgram.lib.process_input import Processinput
from feedgram.lib.database import MyDatabase
from feedgram.social.instagram import Instagram


# Instanzio il database che utilizzarà il process input
DATABASE_PATH = "./test/processinputTest.sqlite3"


def test_stop_not_registered():

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


def test_start_not_registered():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "Congratulations, you're now registered!\nType /help to learn the commands available!"


def test_start_registered():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_START)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're alredy registered.\nType /help to learn the commands available!"


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
                " • /unsub <i>social</i> <i>username</i>\n"
                " • /mute <i>social</i> <i>username</i> <i>time</i>\n"
                " • /halt <i>social</i> <i>username</i> <i>time</i>\n"
                " • /pause <i>social</i> <i>username</i> <i>time</i>\n"
                "<b>Bot:</b>\n"
                " • /stop to stop and unsubscribe from the bot.")

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_HELP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_HELP["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_help


def test_not_command_registered():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.NOT_COMMAND)

    assert result[0]["type"] == "sendMessage"
    assert cnst.NOT_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "[AUTHORIZED] You can send text only!"


def test_help_callback():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CLBK_MODE_HELP["query"])

    assert result[0]["type"] == "answerCallbackQuery"
    assert result[0]["text"] == "Help"

    assert result[1]["type"] == "editMessageText"
    assert cnst.CLBK_MODE_HELP["query"]["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CLBK_MODE_HELP["query"]["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CLBK_MODE_HELP["query"]["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CLBK_MODE_HELP["query"]["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


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


def test_list_command():

    # Aggungo ulteriori sottoscrizioni in modo da poter testare le pagine
    global GLOBAL_EXTRCT_DATA_RETURN
    with patch('feedgram.social.instagram.Instagram.extract_data', side_effect=dummy_instagram_extract_data):
        database = MyDatabase(DATABASE_PATH)
        igram = Instagram()
        myprocess_input = Processinput(database, [igram])

        queries = [cnst.MSG_CMD_SUB_IG_TEST2,
                   cnst.MSG_CMD_SUB_IG_TEST3,
                   cnst.MSG_CMD_SUB_IG_TEST4]

        for query in queries:
            GLOBAL_EXTRCT_DATA_RETURN = query["response"]
            result = myprocess_input.process(query["query"])

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_LIST)

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
    assert cnst.COMMAND_LIST["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_list_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_LIST_PAGE_1)

    assert result[0]["type"] == "answerCallbackQuery"
    assert result[0]["text"] == "Following list"

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_LIST_PAGE_1["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_list_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_LIST_PAGE_2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_LIST_PAGE_2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_list_callback_old_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_LIST_PAGE_3)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_LIST_PAGE_3["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_mute_command_no_args():
    '''
    Test del comando di mute mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_MUTE)

    msm_list = ('<b>⚠️Warning</b>\n<code>/mute</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/mute &lt;social&gt; &lt;username&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/mute &lt;social&gt; &lt;username&gt; &lt;XXXh&gt;</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_MUTE["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_mute_command_set_mute_hours():
    '''
    Test del comando di mute corettamente formattato indicando le ore
    Il ritorno sarà un messaggio che informa sul coretto mute del profilo social
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_MUTE_WORKING_HOURS)

    msm_list = ('<b>✅🔕 Muted successfully!</b>\n\nSocial: <i>ig</i>\nUser: <i>testProfile3</i>!')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_MUTE_WORKING_HOURS["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_mute_command_set_mute_day():
    '''
        Test del comando di mute correttamente formattato indicando i giorni
        Il ritorno sarà un messaggio che informa sul coretto mute del profilo social
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_MUTE_WORKING_DAY)

    msm_list = ('<b>✅🔕 Muted successfully!</b>\n\nSocial: <i>ig</i>\nUser: <i>testProfile3</i>!')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_MUTE_WORKING_DAY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_mute_command_not_social():
    '''
        Test del comando di mute corettamente formattato ma su di un social
        non abilitato o non ancora implementato nel bot (/mute youtube SpaceX)
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_MUTE_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>socialNotAbilitedOrMisstyped</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_MUTE_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_mute_command_not_subscribed():
    '''
        Test del comando di mute corettamente formattato ma su di un social
        non a cui non si è sottoscritti
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_MUTE_MISS_SUBSCRIPTION)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userNotSubscribed</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_MUTE_MISS_SUBSCRIPTION["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_mute_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_MUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Muted list'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_MUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_MUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_MUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_MUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_mute_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_MUTE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_MUTE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_MUTE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_MUTE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_MUTE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_mute_callback_change_date():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_MUTE_PAGE2_DATE)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_mute_callback_use_mute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_MUTE_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Muted'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_MUTE_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_MUTE_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_MUTE_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_MUTE_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_mute_callback_use_unmute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_MUTE_USE_UNMUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Un-Muted'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_MUTE_USE_UNMUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_MUTE_USE_UNMUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_MUTE_USE_UNMUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_MUTE_USE_UNMUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_pause_command_no_args():
    '''
    Test del comando di pause mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_PAUSE)

    msm_list = ("<b>⚠️Warning</b>\n<code>/pause</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/pause &lt;social&gt; &lt;username&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/pause &lt;social&gt; &lt;username&gt; &lt;XXXh&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_PAUSE["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_pause_command_set_mute_hours():
    '''
    Test del comando di pause corettamente formattato indicando le ore
    Il ritorno sarà un messaggio che informa sul coretto pause del profilo social
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_PAUSE_WORKING_HOURS)

    msm_list = ('<b>✅⏯️ Paused successfully!</b>\n\nSocial: <i>ig</i>\nUser: <i>testProfile3</i>!')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_PAUSE_WORKING_HOURS["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_pause_command_set_mute_day():
    '''
        Test del comando di pause correttamente formattato indicando i giorni
        Il ritorno sarà un messaggio che informa sul coretto pause del profilo social
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_PAUSE_WORKING_DAY)

    msm_list = ('<b>✅⏯️ Paused successfully!</b>\n\nSocial: <i>ig</i>\nUser: <i>testProfile3</i>!')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_PAUSE_WORKING_DAY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_pause_command_not_social():
    '''
        Test del comando di pause corettamente formattato ma su di un social
        non abilitato o non ancora implementato nel bot (/pause youtube SpaceX)
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_PAUSE_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>socialNotAbilitedOrMisstyped</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_PAUSE_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_pause_command_not_subscribed():
    '''
        Test del comando di pause corettamente formattato ma su di un social
        non a cui non si è sottoscritti
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_PAUSE_MISS_SUBSCRIPTION)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userNotSubscribed</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_PAUSE_MISS_SUBSCRIPTION["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_pause_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_PAUSE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Pause list'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_PAUSE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_PAUSE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_PAUSE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_PAUSE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_pause_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_PAUSE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_pause_callback_change_date():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_PAUSE_PAGE2_DATE)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_pause_callback_use_mute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_PAUSE_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Paused'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_PAUSE_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_PAUSE_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_PAUSE_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_PAUSE_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_pause_callback_use_unmute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_PAUSE_USE_UNMUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Un-Paused'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_PAUSE_USE_UNMUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_PAUSE_USE_UNMUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_PAUSE_USE_UNMUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_PAUSE_USE_UNMUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_cmute_command_no_args():
    '''
    Test del comando di mute mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CMUTE)

    msm_list = ("<b>⚠️Warning</b>\n<code>/cmute</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/cmute &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/cmute &lt;category&gt; &lt;XXXh&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CMUTE["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cmute_command_set_cmute_hours():
    '''
    Test del comando di mute mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CMUTE_WORKING_HOURS)

    msm_list = ("<b>✅🔕 Muted successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CMUTE_WORKING_HOURS["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cmute_command_set_cmute_day():
    '''
    Test del comando di mute mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CMUTE_WORKING_DAY)

    msm_list = ("<b>✅🔕 Muted successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CMUTE_WORKING_DAY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cmute_command_not_social():
    '''
    Test del comando di mute mal formattato o senza argomenti
    Il ritorno sarà un messaggio che informa sul coretto utilizzo del comando
    '''
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CMUTE_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userMissCategory</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CMUTE_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_chalt_command_no_args():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CHALT)

    msm_list = ("<b>⚠️Warning</b>\n<code>/chalt</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/chalt &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/chalt &lt;category&gt; &lt;XXXh&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CHALT["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_chalt_command_set_cmute_hours():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CHALT_WORKING_HOURS)

    msm_list = ("<b>✅⏹ Stopped successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CHALT_WORKING_HOURS["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_chalt_command_set_cmute_day():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CHALT_WORKING_DAY)

    msm_list = ("<b>✅⏹ Stopped successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CHALT_WORKING_DAY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_chalt_command_not_social():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CHALT_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userMissCategory</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CHALT_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cpause_command_no_args():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CPAUSE)

    msm_list = ("<b>⚠️Warning</b>\n<code>/cpause</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/cpause &lt;category&gt; &lt;XXXd&gt;</code>\n<i>OR:</i>\n<code>/cpause &lt;category&gt; &lt;XXXh&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CPAUSE["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cpause_command_set_cmute_hours():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CPAUSE_WORKING_HOURS)

    msm_list = ("<b>✅⏯️ Paused successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CPAUSE_WORKING_HOURS["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cpause_command_set_cmute_day():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CPAUSE_WORKING_DAY)

    msm_list = ("<b>✅⏯️ Paused successfully!</b>\n\nCategory: <i>default</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CPAUSE_WORKING_DAY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_cpause_command_not_social():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CPAUSE_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userMissCategory</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CPAUSE_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_category_command_no_args():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CATEGORY)

    msm_list = ("<b>⚠️Warning</b>\n<code>/category</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/category &lt;social&gt; &lt;username&gt; &lt;category&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CATEGORY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_category_command_set_category():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CATEGORY_WORKING)

    msm_list = ("<b>✅Successfully moved!</b>\n\nSocial: <i>ig</i>\nUser: <i>testProfile3</i>\nTo category: <i>test</i>!")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CATEGORY_WORKING["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_category_command_not_social():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CATEGORY_MISS_SOCIAL)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>socialNotAbilitedOrMisstyped</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CATEGORY_MISS_SOCIAL["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_category_command_not_subscribed():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_CATEGORY_MISS_SUBSCRIPTION)

    msm_list = ('<b>⚠️Warning</b>\nError: <code>userNotSubscribed</code>')

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_CATEGORY_MISS_SUBSCRIPTION["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_rename_command_no_args():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_RENAME)

    msm_list = ("<b>⚠️Warning</b>\n<code>/rename</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/rename &lt;category&gt; &lt;category&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_RENAME["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_rename_command_miss_category():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_RENAME_MISS_CATEGORY)

    msm_list = ("<b>⚠️Warning</b>\nError: <code>categoryDontExist</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_RENAME_MISS_CATEGORY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_rename_command_working():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_RENAME_WORKING)

    msm_list = ("<b>✅Successfully renamed!</b>\n\nCategory: <i>test</i>\nInto: <i>newcategory</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_RENAME_WORKING["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_remove_command_no_args():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_REMOVE)

    msm_list = ("<b>⚠️Warning</b>\n<code>/remove</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/remove &lt;category&gt;</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_REMOVE["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_remove_command_miss_category():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_REMOVE_MISS_CATEGORY)

    msm_list = ("<b>⚠️Warning</b>\nError: <code>categoryDontExist</code>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_REMOVE_MISS_CATEGORY["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_remove_command_working():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])

    result = myprocess_input.process(cnst.COMMAND_REMOVE_WORKING)

    msm_list = ("<b>✅Successfully removed!</b>\n\nCategory: <i>newcategory</i>")

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_REMOVE_WORKING["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == msm_list


def test_category_mode_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MODE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == "Category list"

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MODE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MODE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MODE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_MODE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_mode_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MODE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MODE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MODE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MODE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_MODE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]

def test_category_remove_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_REMVOE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == "Only the category will be removed, the subscriptions will be moved to 'default' category"

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_REMVOE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_REMVOE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_remove_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_REMVOE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_REMVOE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_remove_callback_use():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_REMVOE_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category removed'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_REMVOE_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_REMVOE_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]




def test_category_mute_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Mute'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_MUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_mute_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MUTE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_mute_callback_change_date():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MUTE_PAGE2_DATE)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_MUTE_PAGE2_DATE["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_mute_callback_use_mute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MUTE_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Muted'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MUTE_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_MUTE_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_mute_callback_use_unmute():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_MUTE_UNMUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Un-Muted'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_MUTE_UNMUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_UNMUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_MUTE_UNMUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_MUTE_UNMUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]







def test_category_halt_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_HALT)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Stop'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_HALT["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_HALT["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_HALT["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_HALT["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_halt_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_HALT_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_halt_callback_change_date():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_HALT_PAGE2_DATE)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2_DATE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2_DATE["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2_DATE["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_HALT_PAGE2_DATE["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_halt_callback_use_stop():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_HALT_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Stopped'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_HALT_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_HALT_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_halt_callback_use_unstop():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_HALT_UNMUTE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Un-Stopped'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_HALT_UNMUTE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_UNMUTE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_HALT_UNMUTE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_HALT_UNMUTE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]





def test_category_pause_callback_base():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_PAUSE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Pause'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_PAUSE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_PAUSE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_pause_callback_page():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_PAUSE_PAGE2)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_pause_callback_change_date():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_PAUSE_PAGE2_DATE)

    assert result[0]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["message_id"] == result[0]["message_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["text"] == result[0]["text"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_PAGE2_DATE["result"][0]["callback_query"]["message"]["reply_markup"] == result[0]["reply_markup"]


def test_category_pause_callback_use_stop():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_PAUSE_USE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Paused'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_PAUSE_USE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_USE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_USE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_USE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]


def test_category_pause_callback_use_unstop():
    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.CALLBACK_CATEGORY_PAUSE_UNPAUSE)

    assert result[0]["type"] == 'answerCallbackQuery'
    assert result[0]["text"] == 'Category Un-Paused'

    assert result[1]["type"] == "editMessageText"
    assert cnst.CALLBACK_CATEGORY_PAUSE_UNPAUSE["result"][0]["callback_query"]["message"]["chat"]["id"] == result[1]["chat_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_UNPAUSE["result"][0]["callback_query"]["message"]["message_id"] == result[1]["message_id"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_UNPAUSE["result"][0]["callback_query"]["message"]["text"] == result[1]["text"]
    assert cnst.CALLBACK_CATEGORY_PAUSE_UNPAUSE["result"][0]["callback_query"]["message"]["reply_markup"] == result[1]["reply_markup"]










def test_unsub_command():
    database = MyDatabase(DATABASE_PATH)
    igram = Instagram()
    myprocess_input = Processinput(database, [igram])

    queries = [cnst.MSG_CMD_UNSUB_STANDARD,
               cnst.MSG_CMD_UNSUB_AGAIN,
               cnst.MSG_CMD_UNSUB_INVALID_SOCIAL,
               cnst.MSG_CMD_UNSUB_BAD_FORMAT]

    for query in queries:
        result = myprocess_input.process(query["query"])
        assert result[0] == query["result"][0]


def test_unsub_callback():
    database = MyDatabase(DATABASE_PATH)
    igram = Instagram()
    myprocess_input = Processinput(database, [igram])

    queries = [cnst.CLBK_UNSUB_MODE,
               cnst.CLBK_UNSUB_MODE_PAGE,
               cnst.CLBK_UNSUB_MODE_EXST_WRNG_PAGE,
               cnst.CLBK_UNSUB_MODE_EXST_WRNG_PAGE_AND_SOCL]

    for query in queries:
        result = myprocess_input.process(query["query"])
        assert result == query["result"]


def test_stop_registered():

    database = MyDatabase(DATABASE_PATH)
    myprocess_input = Processinput(database, [])
    result = myprocess_input.process(cnst.COMMAND_STOP)

    assert result[0]["type"] == "sendMessage"
    assert cnst.COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]
    assert result[0]["text"] == "You're no longer subscribed!\nWe already <i>miss</i> you, please come back soon! 😢\nTip: In order to re-joyn type /start *wink* *wink*"
