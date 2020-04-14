#!/usr/bin/env python3

import json
from unittest.mock import patch
import requests_mock
import requests
from nose.tools import assert_is_not_none, assert_equal

from app.lib.utils import get_url

API_MESSAGE = {
    "success": True,
    "description": "This is a test"
}


def test_get_url_connection_ok():
    with patch('app.lib.utils.requests.get') as mock_get:
        mock_get.return_value.ok = True
        response = get_url("https://test.com")
        assert_is_not_none(response)


def test_get_url_connection_error():
    with patch('app.lib.utils.requests.get') as mock_get:
        mock_get.side_effect = iter([requests.exceptions.ConnectionError(), mock_get.return_value.ok])
        response = get_url("https://test.com")
    assert_is_not_none(response)
    assert_equal(mock_get.call_count, 2)


def test_get_url_content_ok():
    with requests_mock.mock() as mock_get:
        mock_get.get('https://test.com', text=json.dumps(API_MESSAGE))
        response = get_url("https://test.com")
    print(response)
    assert_equal(json.loads(response), API_MESSAGE)
