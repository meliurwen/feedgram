#!/usr/bin/env python3
from os import path, remove
from app.lib.process_input import Processinput
from app.lib.database import MyDatabase

COMMAND_START = {
    "ok": True,
    "result": [
        {
            "update_id": 731419464,
            "message": {
                "message_id": 1256,
                "from": {
                    "id": 62517772,
                    "is_bot": False,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
                    "language_code": "it",
                },
                "chat": {
                    "id": 62517772,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
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
                    "id": 62517772,
                    "is_bot": False,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
                    "language_code": "it",
                },
                "chat": {
                    "id": 62517772,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
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
                    "id": 62517772,
                    "is_bot": False,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
                    "language_code": "it",
                },
                "chat": {
                    "id": 62517772,
                    "first_name": "Ivan",
                    "last_name": "Donati",
                    "username": "Territory",
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

# Instanzio il database che utilizzarà il process input
DATABASE_PATH = "./test/processinputTest.sqlite3"


def test_process_input_stop_not_registred():

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(DATABASE_PATH):
        try:
            remove(DATABASE_PATH)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: %s - %s." % (err.filename, err.strerror))

    assert not path.exists(DATABASE_PATH)

    database = MyDatabase(DATABASE_PATH)

    myprocess_input = Processinput(database)  # da dare in input i social

    result = myprocess_input.process(COMMAND_STOP)

    # verifico che il messaggio di risposta sia un messaggio normale
    assert result[0]["type"] == "sendMessage"

    # verifico che la risposta sia data sulla chat giusta
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico che il messaggio di risposta sia coretto
    assert result[0]["text"] == "You're not registered, type /start to subscribe!"


def test_process_input_start_not_registred():

    database = MyDatabase(DATABASE_PATH)

    myprocess_input = Processinput(database)  # da dare in input i social

    result = myprocess_input.process(COMMAND_START)

    # verifico che il messaggio di risposta sia un messaggio normale
    assert result[0]["type"] == "sendMessage"

    # verifico che la risposta sia data sulla chat giusta
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico hc eil messaggio di risposta sia coretto
    assert result[0]["text"] == "Congratulations, you're now registered!\nType /help to learn the commands available!"


def test_process_input_start_registred():

    database = MyDatabase(DATABASE_PATH)

    myprocess_input = Processinput(database)  # da dare in input i social

    result = myprocess_input.process(COMMAND_START)

    # verifico che il messaggio di risposta sia un messaggio normale
    assert result[0]["type"] == "sendMessage"

    # verifico che la risposta sia data sulla chat giusta
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico hc eil messaggio di risposta sia coretto
    assert result[0]["text"] == "You're alredy registred.\nType /help to learn the commands available!"


def test_process_input_not_command_registred():

    database = MyDatabase(DATABASE_PATH)

    myprocess_input = Processinput(database)  # da dare in input i social

    result = myprocess_input.process(NOT_COMMAND)

    # verifico che il messaggio di risposta sia un messaggio normale
    assert result[0]["type"] == "sendMessage"

    # verifico che la risposta sia data sulla chat giusta
    assert NOT_COMMAND["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico hc eil messaggio di risposta sia coretto
    assert result[0]["text"] == "[AUTHORIZED] You can send text only!"


def test_process_input_stop_registred():

    database = MyDatabase(DATABASE_PATH)

    myprocess_input = Processinput(database)  # da dare in input i social

    result = myprocess_input.process(COMMAND_STOP)

    # verifico che il messaggio di risposta sia un messaggio normale
    assert result[0]["type"] == "sendMessage"

    # verifico che la risposta sia data sulla chat giusta
    assert COMMAND_START["result"][0]["message"]["chat"]["id"] == result[0]["chat_id"]

    # Verifico hc eil messaggio di risposta sia coretto
    assert result[0]["text"] == "You're no longer subscribed!\nWe already <i>miss</i> you, please come back soon! 😢\nTip: In order to re-joyn type /start *wink* *wink*"
