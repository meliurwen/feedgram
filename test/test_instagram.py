#!/usr/bin/env python3

import test.constants as cnst

import json
import re
from unittest.mock import patch
from unittest import mock
import requests_mock
from nose.tools import assert_equal

from feedgram.social.instagram import Instagram


def ig_html_src(ig_scrape_api):
    return "window._sharedData = " + \
        json.dumps(ig_scrape_api) + \
        ";</script>"


def test_extract_data_username():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")

    api_queries = [cnst.IG_API_SCRP_USERNAME_EXIST_PUB,
                   cnst.IG_API_SCRP_USERNAME_EXIST_PRIV,
                   cnst.IG_API_SCRP_USERNAME_NO_EXIST]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=ig_html_src(api["response"]))
            response = igram.extract_data(api["query"])
        assert_equal(response, api["query"])


def test_extract_data_p():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/p\/([A-Za-z0-9-_]{1,30})")

    api_queries = [cnst.IG_API_SCRP_P_EXIST_PUB,
                   cnst.IG_API_SCRP_P_NO_EXIST_OR_PRIV]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=ig_html_src(api["response"]))
            response = igram.extract_data(api["query"])
        api["query"]["username"] = api["query"]["title"]
        assert_equal(response, api["query"])


def test_extract_data_invalid():
    igram = Instagram()

    matcher = re.compile(r"")

    api = cnst.IG_API_SCRP_INVALID
    with requests_mock.mock() as mock_get:
        mock_get.get(matcher, text=ig_html_src(api["response"]))
        response = igram.extract_data(api["query"])

    del api["query"]["username"]
    assert_equal(response, api["query"])


GLOBAL_COUNTER = 0


def custom_matcher_no_json(request):
    global GLOBAL_COUNTER
    # print(request.path_url)
    if GLOBAL_COUNTER == 0:  # Not a json
        GLOBAL_COUNTER += 1
        return requests_mock.create_response(request, status_code=200, text="THIS IS A TEST")
    elif GLOBAL_COUNTER == 1:  # A json, but it's the rate limited case, in which a login page is presented
        GLOBAL_COUNTER += 1
        return requests_mock.create_response(request, status_code=200, text=ig_html_src({"entry_data": {"LoginAndSignupPage": None}}))
    else:
        GLOBAL_COUNTER = 0  # A json
        return requests_mock.create_response(request, status_code=200, text=ig_html_src(cnst.IG_API_SCRP_USERNAME_EXIST_PUB["response"]))


# tme.sleep patched so regardless the value issue it is now istant
@patch('feedgram.social.instagram.time.sleep', return_value=None)
def test_extract_data_no_json_error(_):
    igram = Instagram()

    api = cnst.IG_API_SCRP_USERNAME_EXIST_PUB
    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher_no_json)
        response = igram.extract_data(api["query"])
    assert_equal(response, api["query"])


@mock.patch('feedgram.social.instagram.time.time', mock.MagicMock(return_value=61300805))
def test_get_feed():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")

    api_queries = [cnst.SOCIAL_QUERY_PRIVATE_NOW_PUBLIC,
                   cnst.SOCIAL_QUERY_PRIVATE_NOW_PUBLIC_NOTEXT,
                   cnst.SOCIAL_QUERY_PUBLIC_NOW_PRIVATE,
                   cnst.SOCIAL_QUERY_DLT_OR_NO_EXIST]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=ig_html_src(api["response"]))
            response = igram.get_feed([api["query"]])
        assert_equal(response, api["result"])


# This test is a quick patch.
# TODO: Now that the feedgram.lib.utils.get_url function can also return the
# `status_code` of the HTTP stack we should update these tests.

def test_extract_data_username_no_exist():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")

    api_queries = [cnst.IG_API_SCRP_USERNAME_NO_EXIST]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, status_code=404, text="trash")
            response = igram.extract_data(api["query"])
        assert_equal(response, api["query"])
