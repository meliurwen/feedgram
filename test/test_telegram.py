#!/usr/bin/env python3

import json
import re
import queue
from random import randrange, sample
from time import time
import requests_mock
from nose.tools import assert_equal, assert_true

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
    # print(request.path_url)
    if request.path_url.startswith("/bot"):
        return requests_mock.create_response(request, status_code=200, text=json.dumps({"ok": True, "result": "Message sent"}))
    return None


def test_send_message():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")

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


def test_send_messages_max_one_sec_different_chat_ids():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")
    coda = queue.Queue()

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/5 (1/10 is too much)
    tel_interface.ONE_SECOND_TIME = 0.5
    tel_interface.SIXTY_SECONDS_TIME = 30

    one_sec = tel_interface.ONE_SECOND_TIME

    # Generate 90 messages with unique chat_ids and put them into the queue
    messages = 90
    chat_id_unique_list = sample(range(10000, 99999), messages)
    for chat_id in chat_id_unique_list:
        message = {
            "type": "sendMessage",
            "text": "<b>⚠️TEST⚠️</b>\nTest message.",
            "chat_id": chat_id,
            "markdown": "HTML"
        }
        coda.put(message)

    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher)
        start_time = time()
        tel_interface.send_messages(coda)
        stop_time = time()
    elapsed_time = (stop_time - start_time)
    delay = (messages // 30) * one_sec
    assert_true(delay * 0.95 <= elapsed_time <= delay * 1.05)


# > Max 1 message per second for the same chat_id.
# > Max 20 messages per minute for the same chat_it.
# The first message is sent immediately. This means that the delay in seconds
# for the Nth message (if it doesn't exceeds the rate limit per minute) is:
# DELAY = (N - 1) * 1
# For example to send 20 messages the daly is 19 seoconds.
# If we exceed the rate limit per minute the delay in seconds for the Nth
# message is:
# DELAY = 60sec * (N // 20) + (N % 20 - 1) * 1sec
# Note: the number 20 in the equation above is the rate limit per minute.
# For example to send 21 messages the delay is 60 seconds.
def test_send_messages_max_one_min_same_chat_ids():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")
    coda = queue.Queue()

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/10
    tel_interface.ONE_SECOND_TIME = 0.1
    tel_interface.SIXTY_SECONDS_TIME = 6

    one_sec = tel_interface.ONE_SECOND_TIME
    sixty_sec = tel_interface.SIXTY_SECONDS_TIME

    # Generate 21 messages with same chat_ids and put them into the queue.
    # It will deliver the first 20 immediately and then wait the cooldown to
    # send the other 1.
    messages = 21
    for _ in range(messages):
        message = {
            "type": "sendMessage",
            "text": "<b>⚠️TEST⚠️</b>\nTest message.",
            "chat_id": 123456789,
            "markdown": "HTML"
        }
        coda.put(message)

    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher)
        start_time = time()
        tel_interface.send_messages(coda)
        stop_time = time()
    elapsed_time = (stop_time - start_time)

    # Calculates the expected delay
    delay = sixty_sec * (messages // 20) + (messages % 20 - 1) * one_sec

    # Some tolerances are added in the comparison
    assert_true(delay * 0.95 <= elapsed_time <= delay * 1.05)
