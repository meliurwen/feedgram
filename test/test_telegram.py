#!/usr/bin/env python3

import json
import re
from random import randrange
import requests_mock
from nose.tools import assert_equal

from app.lib.telegram import Telegram

JSON_GENERIC = {
    "success": True,
    "description": "This is a test"
}

API_NO_UPDATES = {
    "ok": True,
    "result": [
    ]
}

API_ONE_MESSAGE = {
    "ok": True,
    "result": [
        {
            "update_id": 125789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "username": "test",
                    "language_code": "en"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "username": "test",
                    "type": "private"
                },
                "date": 1586905641,
                "text": "Test Message"
            }
        }
    ]
}


def test_get_updates():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")

    matcher = re.compile(r"^https:\/\/api\.telegram\.org\/bot\d{9}:[A-Za-z0-9-_]{35}\/getUpdates\?timeout=\d{1,4}(&offset=-?\d{1,4})?$")

    api_responses = [JSON_GENERIC, API_NO_UPDATES, API_ONE_MESSAGE]

    # Without offset
    for api_response in api_responses:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=json.dumps(api_response))
            response = tel_interface.get_updates()
        assert_equal(response, api_response)

    # With offset
    for api_response in api_responses:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=json.dumps(api_response))
            response = tel_interface.get_updates(randrange(-5, 5))
        assert_equal(response, api_response)


ONE_MESSAGE_STANDARD = {
    "type": "sendMessage",
    "text": "<b>⚠️TEST⚠️</b>\nTest message.",
    "chat_id": "123456789",
    "markdown": "HTML"
}

ONE_MESSAGE_STANDARD_INLN_KYBD = {
    "type": "sendMessage",
    "text": "<b>[HELP]</b>\nHere some help",
    "chat_id": "123456789",
    "markdown": "HTML",
    "reply_markup": {
        "inline_keyboard": [
            [
                {
                    "text": "🗑",
                    "callback_data": "remove_mode"
                },
                {
                    "text": "✏️",
                    "callback_data": "add_mode"
                }
            ],
            [
                {
                    "text": "🔕",
                    "callback_data": "notifications_mode_off"
                },
                {
                    "text": "📖",
                    "callback_data": "help_mode"
                }
            ]
        ]
    }
}

ONE_MESSAGE_STANDARD_MALFORMED = {
    "type": "sendMessage",
    "text": "<b>⚠️TEST⚠️</b>\nStandard malformed message.",
    "chat_id_bumblebeee": "123456789",
    "markdown": "HTML"
}

ONE_MESSAGE_CLLBCKQRY = {
    "type": "answerCallbackQuery",
    "text": "Test Alert!",
    "callback_query_id": "123456789",
    "show_alert": True
}

ONE_MESSAGE_CLLBCKQRY_MALFORMED = {
    "type": "answerCallbackQuery",
    "text": "Test Alert!",
    "ponies": "123456789",
    "show_alert": True
}


EDIT_MESSAGE_TEXT_INLN_KYBD = {
    "type": "editMessageText",
    "message_id": "123456789",
    "text": "<b>⚠️HELP⚠️</b>\nStuff with a keyboard.",
    "chat_id": "123456789",
    "markdown": "HTML",
    "disable_web_page_preview": True,
    "reply_markup": {
        "inline_keyboard": [
            [
                {
                    "text": "🗑",
                    "callback_data": "remove_mode"
                },
                {
                    "text": "✏️",
                    "callback_data": "add_mode"
                }
            ],
            [
                {
                    "text": "🔕",
                    "callback_data": "notifications_mode_off"
                },
                {
                    "text": "📖",
                    "callback_data": "help_mode"
                }
            ]
        ]
    }
}

EDIT_MESSAGE_TEXT_INLN_MSG_ID = {
    "type": "editMessageText",
    "inline_message_id": 123456789,
    "text": "Edited Message using inline_message_id",
    "markdown": "HTML"
}

# No text parameter
EDIT_MESSAGE_TEXT_MALFORMED_1 = {
    "type": "editMessageText",
    "inline_message_id": 123456789,
    "markdown": "HTML"
}

# No message_id parameter
EDIT_MESSAGE_TEXT_MALFORMED_2 = {
    "type": "editMessageText",
    "chat_id": "123456789",
    "text": "Hello",
    "markdown": "HTML",
}

# Non-existent type
NON_EXISTENT_TYPE = {
    "type": "unicorn",
    "chat_id": "123456789",
    "text": "Hello",
    "markdown": "HTML",
}


def custom_matcher(request):
    print(request.path_url)
    if request.path_url.startswith("/bot"):
        return requests_mock.create_response(request, status_code=200, text=json.dumps({"ok": True, "result": "Message sent"}))
    return None


def test_send_message():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")

    # matcher = re.compile(r"^https:\/\/api\.telegram\.org\/bot\d{9}:[A-Za-z0-9-_]{35}\/\S+$")

    api_queries = [ONE_MESSAGE_STANDARD,
                   ONE_MESSAGE_STANDARD_INLN_KYBD,
                   ONE_MESSAGE_STANDARD_MALFORMED,
                   ONE_MESSAGE_CLLBCKQRY,
                   ONE_MESSAGE_CLLBCKQRY_MALFORMED,
                   EDIT_MESSAGE_TEXT_INLN_KYBD,
                   EDIT_MESSAGE_TEXT_INLN_MSG_ID,
                   EDIT_MESSAGE_TEXT_MALFORMED_1,
                   EDIT_MESSAGE_TEXT_MALFORMED_2,
                   NON_EXISTENT_TYPE]
    for api_query in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.add_matcher(custom_matcher)
            tel_interface.send_message(api_query)
