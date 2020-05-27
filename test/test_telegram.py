#!/usr/bin/env python3

import test.constants as cnst

import json
import re
import queue
import threading
from random import randrange, sample
from time import time, sleep
import requests_mock
from nose.tools import assert_equal, assert_true

from feedgram.lib.telegram import Telegram

TELEGRAM_API_KEY = "258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa"


def test_get_updates():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    matcher = re.compile(r"^https:\/\/api\.telegram\.org\/bot\d{9}:[A-Za-z0-9-_]{35}\/getUpdates\?timeout=\d{1,4}(&offset=-?\d{1,4})?$")

    api_responses = [cnst.JSON_GENERIC, cnst.API_NO_UPDATES, cnst.API_ONE_MESSAGE]

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


GLOBAL_COUNTER = 0


def custom_matcher_no_json(request):
    global GLOBAL_COUNTER
    # print(request.path_url)
    if GLOBAL_COUNTER == 0:
        GLOBAL_COUNTER += 1
        text = "THIS IS A TEST"
    else:
        GLOBAL_COUNTER = 0
        text = json.dumps(cnst.JSON_GENERIC)
    return requests_mock.create_response(request, status_code=200, text=text)


def test_get_updates_no_json_error():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher_no_json)
        response = tel_interface.get_updates()
    assert_equal(response, cnst.JSON_GENERIC)


def custom_matcher(request):
    # print(request.path_url)
    if request.path_url.startswith("/bot"):
        return requests_mock.create_response(request,
                                             status_code=200,
                                             text=json.dumps({
                                                 "ok": True,
                                                 "result": "Message sent"
                                             }))
    return None


def test_send_message():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    api_queries = [cnst.ONE_MESSAGE_STANDARD,
                   cnst.ONE_MESSAGE_STANDARD_INLN_KYBD,
                   cnst.ONE_MESSAGE_STANDARD_MALFORMED,
                   cnst.ONE_MESSAGE_STANDARD_LNG_TXT,
                   cnst.ONE_MESSAGE_CLLBCKQRY,
                   cnst.ONE_MESSAGE_CLLBCKQRY_MALFORMED,
                   cnst.EDIT_MESSAGE_TEXT_INLN_KYBD,
                   cnst.EDIT_MESSAGE_TEXT_INLN_MSG_ID,
                   cnst.EDIT_MESSAGE_TEXT_MALFORMED_1,
                   cnst.EDIT_MESSAGE_TEXT_MALFORMED_2,
                   cnst.NON_EXISTENT_TYPE]
    for api_query in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.add_matcher(custom_matcher)
            tel_interface.send_message(api_query)

# > Max 30 messages per second overall
# Sends 90 messages to 90 unique chat_id as fast as possible
# The first message is immediately sent. This means that the delay in seconds
# for the Nth message is:
# DELAY = (N // 30) * 1sec
# Note: for simplicity the delay introduced by the hardware/code efficiency is
# not counted!
# For example to send 1800 messages to 1800 unique chat_id the daly is 60 seoconds.


def test_send_messages_max_one_sec_different_chat_ids():
    tel_interface = Telegram(TELEGRAM_API_KEY)
    coda = queue.Queue()

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/5 (1/10 is too much)
    tel_interface.ONE_SECOND_TIME = 0.5
    tel_interface.SIXTY_SECONDS_TIME = 30

    one_sec = tel_interface.ONE_SECOND_TIME

    # Generate 1800 messages with unique chat_ids and put them into the queue
    messages = 1800
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
# The first message is immediately sent. This means that the delay in seconds
# for the Nth message (if it doesn't exceeds the rate limit per minute) is:
# DELAY = (N - 1) * 1sec
# For example to send 20 messages the daly is 19 seoconds.
# If we exceed the rate limit per minute the delay in seconds for the Nth
# message is:
# DELAY = 60sec * (N // 20) + (N % 20 - 1) * 1sec
# Note: the number 20 in the equation above is the rate limit per minute.
# For example to send 21 messages the delay is 60 seconds.
def test_send_messages_max_one_min_same_chat_ids():
    tel_interface = Telegram(TELEGRAM_API_KEY)
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


# 90 unique chat_id sends 20 messages at minute = 1800 messages at minute
def test_send_messages_max_one_sec_max_one_min_same_chat_ids():
    tel_interface = Telegram(TELEGRAM_API_KEY)
    coda = queue.Queue()

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/5 (1/10 is too much)
    tel_interface.ONE_SECOND_TIME = 0.5
    tel_interface.SIXTY_SECONDS_TIME = 30

    one_sec = tel_interface.ONE_SECOND_TIME

    # Generate 90 users with unique chat_ids and put them into the queue
    users = 90
    chat_id_unique_list = sample(range(10000, 99999), users)
    for _ in range(20):
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
    delay = ((users * 20) // 30) * one_sec
    assert_true(delay * 0.95 <= elapsed_time <= delay * 1.05)


def test_send_messages_random():
    tel_interface = Telegram(TELEGRAM_API_KEY)
    coda = queue.Queue()

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/10
    tel_interface.ONE_SECOND_TIME = 0.1
    tel_interface.SIXTY_SECONDS_TIME = 6

    # Generate 90 users with unique chat_ids and put them into the queue
    users = 10
    chat_id_unique_list = sample(range(10000, 99999), users)
    for _ in range(100):
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
        tel_interface.send_messages(coda)


CODA_THREAD = queue.Queue()


def dummy_send_messages():
    sleep(2)
    CODA_THREAD.put(cnst.ONE_MESSAGE_STANDARD)

# Enters into a while loop accessible only when the queue is empty


def test_send_messages_while():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    # For the sake of the duration of the tests the time windows of one second
    # and one minute has been reduced at 1/10
    tel_interface.ONE_SECOND_TIME = 0.1
    tel_interface.SIXTY_SECONDS_TIME = 6

    thread = threading.Thread(target=dummy_send_messages)
    thread.start()

    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher)
        start_time = time()
        tel_interface.send_messages(CODA_THREAD)
        stop_time = time()
    thread.join()
    elapsed_time = (stop_time - start_time)
    assert_true(2 <= elapsed_time <= 3)
