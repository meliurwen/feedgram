#!/usr/bin/env python3

import json
from unittest.mock import patch
import requests_mock
import requests
from nose.tools import assert_is_not_none, assert_equal

from feedgram.lib.utils import get_url

API_MESSAGE = {
    "success": True,
    "description": "This is a test"
}


def test_get_url_connection_ok():
    with patch('feedgram.lib.utils.requests.get') as mock_get:
        mock_get.return_value.ok = True
        response = get_url("https://test.com")["content"]
        assert_is_not_none(response)


def test_get_url_connection_error():
    with patch('feedgram.lib.utils.requests.get') as mock_get:
        mock_get.side_effect = iter([requests.exceptions.ConnectionError(), mock_get.return_value.ok])
        response = get_url("https://test.com")["content"]
    assert_is_not_none(response)
    assert_equal(mock_get.call_count, 2)


def test_get_url_content_ok():
    with requests_mock.mock() as mock_get:
        mock_get.get('https://test.com', text=json.dumps(API_MESSAGE))
        response = get_url("https://test.com")["content"]
    assert_equal(json.loads(response), API_MESSAGE)


GLOBAL_COUNTER = 0


def custom_matcher_no_json(request):
    global GLOBAL_COUNTER
    # print(request.path_url)
    if GLOBAL_COUNTER == 0:
        GLOBAL_COUNTER += 1
        return requests_mock.create_response(request, status_code=200, text=b'')
    else:
        GLOBAL_COUNTER = 0
        return requests_mock.create_response(request, status_code=200, text="hello")


def test_get_url_type_error():
    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher_no_json)
        response = get_url("https://test.com")["content"]
    assert_equal(response, "hello")
