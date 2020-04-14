#!/usr/bin/env python3

import json
import re
from unittest.mock import patch
import requests_mock
import requests
from nose.tools import assert_is_not_none, assert_equal

from app.lib.telegram import Telegram

JSON_GENERIC = {
    "success": True,
    "description": "This is a test"
}

API_NO_UPDATES = {
    "ok":True,
    "result":[
    ]
}

API_ONE_MESSAGE = {
    "ok":True,
    "result":[
        {
            "update_id":125789,
            "message":{
                "message_id":123,
                "from":{
                    "id":123456789,
                    "is_bot":False,
                    "first_name":"John",
                    "username":"test",
                    "language_code":"en"
                },
                "chat":{"id":123456789,
                "first_name":"John",
                "username":"test",
                "type":"private"
                },
            "date":1586905641,
            "text":"Test Message"
            }
        }
    ]
}


def test_get_updates():
    tel_interface = Telegram("258484394:QKPEDbZx8AZcfi6yhHqh2eNCGBNHb3fubQa")

    matcher = re.compile(r"^https:\/\/api\.telegram\.org\/bot\d{9}:[A-Za-z0-9-_]{35}\/getUpdates\?timeout=\d{1,4}(&offset=-?\d{1,4})?$")

    api_responses = [JSON_GENERIC, API_NO_UPDATES, API_ONE_MESSAGE]
    for api_response in api_responses:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=json.dumps(api_response))
            response = tel_interface.get_updates()
        assert_equal(response, api_response)
    
