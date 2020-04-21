#!/usr/bin/env python3

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
    tel_interface = Telegram(TELEGRAM_API_KEY)

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


GLOBAL_COUNTER = 0


def custom_matcher_no_json(request):
    global GLOBAL_COUNTER
    # print(request.path_url)
    if GLOBAL_COUNTER == 0:
        GLOBAL_COUNTER += 1
        return requests_mock.create_response(request, status_code=200, text="THIS IS A TEST")
    else:
        GLOBAL_COUNTER = 0
        return requests_mock.create_response(request, status_code=200, text=json.dumps(JSON_GENERIC))


def test_get_updates_no_json_error():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher_no_json)
        response = tel_interface.get_updates()
    assert_equal(response, JSON_GENERIC)


ONE_MESSAGE_STANDARD = {
    "type": "sendMessage",
    "text": "<b>⚠️TEST⚠️</b>\nTest message.",
    "chat_id": 123456789,
    "markdown": "HTML"
}

# More than 4096 chars (5120)
ONE_MESSAGE_STANDARD_LNG_TXT = {
    "type": "sendMessage",
    "text": "hUfoW3SjWWSN9TfokiTANf6cnRQMpzdAdhcYBg7WxynmzIx9L2cbo6St8L0mt7G1KgRMxwaLYXUyDLGDiSjVZ9Udn4vM4DRT4tJmrrwJ20S17AJLMIQ7cVmlUa1VgkR6VncEba76PWQQbl2PNeoUkHMcMeiB3O9t9cBJVsWAXSM6beIkcVSchA1eM3NQhYqTwEq7qhFoJwuurOk6Fm8ACpXYW8aCnBaUjKmzfuLJxDpvWkcNk1ndy0oOa2KaghaGEWm7gya7MxvYcWTHaJ40AkrY3WpLqY5cDlfSZgsEesUfK13jr6Fn9HRUFnFlabd9ZGoFTWtnHlSMFLkPAavCaA1ktJoBcCXGb6czNZhv3YRoS0ByzQRDoF6bYoWuNiv0Lqv6Ik6PNo5JTrrgkdmVTA6zW9Sh0VPR0L6TbHV39LRplzN4skB7xEdtBLQ4TVy46n4weCaoEWdWyxDyE4qGRZ8pRv7aNLbqyAafI5E0l6ujeat0V2UVGDz1QhfqH1gJ3W6J7bclTSKO6VvLLQCg15d8mNTZZzdEUVHHBjkFxbFvftDSFLyzR1tL1r2VeLr65NoMmxm7xq9YDnveXTd2dAcQSV9hC32v0ved1C3JnyUzFWAlUiVQI4pZU3GK7ReqRhcERMMe55zZ0dEMcZ65Kns9R6n4HUtsSk9Op0sdb22lREfxi8GQP0Zj6xRgMngnB2rEe2p3wGEtysegx4cQyIwn3pcMsuCo20AzR1MnbvlXfu4stQdZ2kUWRHKF3s3OTakqzexrY9J0x50ifyxqVFchvZd5wiv2VghQVnbS7lL46CajwfiXc54vu2zDhA3yMuSF5Of7nom5yiW0tgcRN0XvvpoLXVW00uThOgcpMr8ZpAeQnWxkOTL2gM1jie97Zy41khuDF73UvkWbylZQmalOjqfXMztzVcDPjeBXgL05XtIEMLCt2nFXFDF7H0Txw51rz6NgQMHCv9Dh7NIN3GUcG0qYWqo8AcQ2KFhm3iDQJoJlkKeOFXflsioNHoSwXP5T5TieTofrMpPdxQHXRyk6jcjKT7DS4FkILfuYdipudJ67eqVOciE17l7KieBLuC2uPv86oU8QOnUZFEOiIjy2qnMtb4hsSBx83W4obqvWMU5eXagTXrOlWgFylhlN2wP6aaANVFml1wcpMxrYRfUfwlGoMFcEpij6lBLgZ9eYb8b6MTf74tOKZh74ZOtfEqzheZLhZUcP0MNM7JnfXXqmp2xt3kvKNc4TXifLDhxFsEmJut633zheRMHS8yRpNq8177DWsmuTtjkEEE2F2vhRELNcI3gG1M6Vw2iUSiw2MS04MRAmmv4Eo5iuCyAVf0X8rW3brU5fTs7I0oQLZymRl6rXJ0hhb5jKkAh8nXkFFjIwOVXBSM7FghEKXsHKTRup1OBCRW4dmSzWTG7DmhtvJWscClwVbInTvg882J7QbHolN7cPO0DiKcYveF0DpjC0UvG3HpluxQKIdCju9xqhoAsoqL5Uxqo8tuTkWJdav9frYvQv2xL4ixURATCuST4Ri6o92F0M4mAaaWhYN84nm928UbITJy13LKkqUwAVmcqdzvf1c5IW5X7zr35Jec3Ss9LRqVBXQjUYl2HVw3Upx67nugot6zjxL3l1wYJo6uXUu17VQae24pFq0GWEuN9AKyXdrUVqokdzatypNI1C7mMvGdd9NNbSXiPa79v0ThdPuWMmNNAzvJHmxhgfq5VhDYOJsexPTjvUQbNhvlATSVu2JoAuRLlMAc77qg1C3WfMwyTcAfHPr3DZhZ6AQGEpmjGWazUv4kPaa5JAmDBrH8DXEGXcVEl2y1JDj3MzQqoUBJtOUQlLHHNfjfrHp3M15GnZcWBNkDYdFqSCmjcrst8slHjcNZ5tMQ8Pvg4QubHTmyfaSWrC5INCCk39ptKY21kG5OiNkGJNb4ZaYpxMyktXwtdoy6ieZ2FQ9cD80mSTN2DCe4cU2Xa0RiaX5sk8M9Og4HMqtgyKlvYBrbeV5PlL7IzwVlPMAPKlUL2Q3OurEENGBZd5jHOZoKjFfKXABw0ygCEcEQYjkYYhXIcmFigRqA3FhWKJrymfJWvvEZ6QLtqfXbchw6pKvsKhqVArgEjWiAeZTbWadfs2hoAAl66JWii0ru3J3e9yVjqoGlRN43tJ7gKb5pMWxnQLbNpQtvRiRgTHmwWbVq2oO0i0WehSB4EYy1UlPaPSPfzjWpf8FOf0FYuEvq3lo3Gyew7M5ZAUOtXpacRGikXK4YJ0nHgdaPbuAKDrh8qCaawPb46zq2ubNEgn4lg9zFRClUuUFJVhiYGkWVTB4e1GLK6BCPnU9iCYksLWrY7csCU8Z9aYpceu4iIUbP7IHieqEH7e0uejSftGQtJ4y9cBGffZ9uBxRAb47ocMd3VHz849K534br98fjQRuwMXl3zxeKXTDVcNXQHAckqF6Ks6ZNbZENdr1L0yOCKhnU92JNSgsdlMNCdE3TjEmfNU6tvrqjpFnvyswAg66uDa4CoMJ1qlgHpwc54sRqokXAiFeTZGwkiHFNr55baL01ke3xuFLBWw7RfVynpYLMgbz7zoVxMjc2fAdh0VWdsOQVxxxryVgrOvYWsk0uFTLDG5JhlRYOUMK9ZOvvF8FCro4lq6EXzURJD694U3axkSmmRpG7zS727k1XsovLLDWQapvUNWneqc1CsOkj8fBf7JGyjlmk2leVtBNsaiOAxJjXfj6LuVwCA5JlcxidDFFpQJJcqQldLqSYLkKdoEtt1K1BJF7MQ1EkqcZiyljeJ3jsfuP7cDYeQIT3O38FvV8aOsosr9WciLKv5QIon0s2BPliStM8KJOh3BGf62xh67uZFKVpBr26TobVRhrzTzrWtwmSgkTQFjQbw37kQukEQWAjZQjOZUJ3dBhNdXzvoiIbTDXIBV2x4uFGck9DODZAdFtwrvuamxyPYoEm1Yo6tgdZJacw3AHclVKtjrl8w1mxHSaefwX7urYW5iCI5s4QBgh5HmPWT08gmQ6B1ZAHb6e8H3gECCyI6PI7P08cl8mlmESbNtaYu9bp58hfOAcwXLMNSogIbbWchA1DlTJ3IjhlMbScWGcBQtlHmNGROgQXuxRMSuoW48XHHTApnpMmgAxsgtmElT63rzbWdm9jORCEMMv5qJ5MwUtKWMm3T06IZUB4gQFhitrYGf3MzKpSQh8QAm8o5MgoboS5DotBL43lEK2eAUVyxsIArerfmZaUmYppy1HkjVKWfXRl8snJdMjzW6JK5dB8RA1S2YftU6LhWFo0b9jh8HBwXYFdz1b0SEZiVcZXUxjS4WZNUG5O1RnQcrnNrMdvK4YERnFAycOI0ZpJutebJ92KLi4Z4UcO09Gs6qSMzWSfOzQoEGnX3WyBd0yls3F2kMWKn6xnceTpeSwfYPYSNz5hVr6MW2taC5izXMTyV5hxArIOBamuj7z5awqLeP40O1orYfsAVkh5EPaM5iolpQdyGur737tlWCP4977zt8RoQYPcV4ux8RBSdRGTBMpKDl5sjz5CSbsIeL79yzY9s7FgIi49HBTc4QuCY6QgjzEmK9XwqLImEI6D1RTVaednwPBWX2RFI5zeSOwGLXi7NOdo29vwCWzYlj5OsQhkBg9Gq3VJ4OuXwkcJVHib8OE0UTrw8GcMCDQ9ipyviWU4D1yLPltvuH43zh9adJQxhi79JOQvKecnOUY9IZDHkkpYMS4kHDcagt8QVSUhz9hVEPsp90DrzgyTVcozq2xYgCZAYeeXyfGRuKpyawa7ji3utKdCXoDvOrp5489n63exoQKhAu8aPqHFIRx9W8hG5ZGyU5VE3K5GTUXVQhJQTMIpAoM0MiCWUBdbimrh4di8CdZ8JDHJMI0lGQVsIkuBpVKvIeMuoroKNyvgVlPcP9HvAr2Z6GgdJZXUUlLZJuaNVNRvPnsFdiDYyJFyFkdcWM9XdWrxBhWx9jOIi04AtkUiECGQLjGrqZ4P15wtxzmlQX0Rtb4JwSwuwXiAK8k9WrZbKQHCoCiMzKHdmMp3nCNs1iVOgWDIOF4w4qfyqNhL83rqqpMDJ43clmBGYCeiHF3OSLJnSHc7MHjoKtuIoB1DmT9bvodonZJGfEFgFAV75pwxDJnbCeudk5zLbcfqsKTUcqJDebPTKlWUvDD80I7r8rSHapxVUAglaiiUQhKfYlXJnkJNpuRaCUOQ04iOdfJqXa8EDkf1E3PXnoTKpfzzODWlfgrigU20WkdOTBG85GAZzwnHgQ9DuHxZfVKKTSiiqcfB7A7F1wO4mI7M7VcYEE6ykw8tsob8mw9DoGfMwZIQNFwaUEqyMjO3d7vqF02YsLRdphd5ere1p38ODfz9E1ZnbzFJNUWY1LLav6mctBq7gNz08qIxfTmiU8hIUBlqIwGvq578XQlJYCDnH3Hqith7wO0Cu5UlRm3oSyXWCB3hyKwC0UYKjlVbikP3AQy9kM8JD2L8qICP8fjeue0iOxrq53qeQY8BXGAcdsr6m2I58279kPRJbR9QeZy9xK2ZuzEkGAG9WBhLriBZ2egXhYoWhrZgd5548wzaOVEPR50dMbFyBKPSmZiPRw79jZWQGih20zhjInasvAU9VzvOgKJu6b8VOFlGsL9QqNHIA4D9rN0WVDMTreNEYwN9ZZHadE0zhzXbC7Q2rtPsfwdR1T5FSWqsKFzRZN1h1vdAtRoRtk8I2jXfQRdtTcVBofnssBI2YOcoGgXfDLJNP0W9cLBh4s3h33MOfcZUwOxujDgnb4StPD6nZj6uMH8PRxexN7y6kC6DZyELdjdeh6mJUmxHw7I5LmroOqMXxJIaMZRaA9Wx0xUDneaZjo5ZNBMKPVkWj04kKqYogR9EtRMW7MvZaiJvEXAnCdAm1VizQPtV0MXnacu50B5Sdi8B5Gv4n5yXTfSh3D0Zz3eg1JF5xy3nSqqqURQBl2h6OzGJhKeN4wrJkEgIbOxQYitAu9XheXCnhGD9Yb56B80QjHorVwa2LfLzR38U9pEMgRKjNPv7P3DY2xemySwAnkUXe6Btxzjp3k99T8E19ul9u27pBgDfAnjkbzb3UyFhoLpmWDerDHUgBMv1xRReAdJ7nMfW7q6aAw6iz1kfpr",
    "chat_id": 123456789,
    "markdown": "HTML"
}

ONE_MESSAGE_STANDARD_INLN_KYBD = {
    "type": "sendMessage",
    "text": "<b>[HELP]</b>\nHere some help",
    "chat_id": 123456789,
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
    "chat_id_bumblebeee": 123456789,
    "markdown": "HTML"
}

ONE_MESSAGE_CLLBCKQRY = {
    "type": "answerCallbackQuery",
    "text": "Test Alert!",
    "callback_query_id": 123456789,
    "show_alert": True
}

ONE_MESSAGE_CLLBCKQRY_MALFORMED = {
    "type": "answerCallbackQuery",
    "text": "Test Alert!",
    "ponies": 123456789,
    "show_alert": True
}


EDIT_MESSAGE_TEXT_INLN_KYBD = {
    "type": "editMessageText",
    "message_id": "123456789",
    "text": "<b>⚠️HELP⚠️</b>\nStuff with a keyboard.",
    "chat_id": 123456789,
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
        return requests_mock.create_response(request,
                                             status_code=200,
                                             text=json.dumps({
                                                 "ok": True,
                                                 "result": "Message sent"
                                             }))
    return None


def test_send_message():
    tel_interface = Telegram(TELEGRAM_API_KEY)

    api_queries = [ONE_MESSAGE_STANDARD,
                   ONE_MESSAGE_STANDARD_INLN_KYBD,
                   ONE_MESSAGE_STANDARD_MALFORMED,
                   ONE_MESSAGE_STANDARD_LNG_TXT,
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
    CODA_THREAD.put(ONE_MESSAGE_STANDARD)

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
