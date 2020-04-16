#!/usr/bin/env python3
import json
import re
import requests_mock
from nose.tools import assert_equal

from app.social.instagram import Instagram

IG_API_SCRP_USERNAME_EXIST_PUB = {
    "query": {
        "username": "alice",
        "internal_id": 123456789,
        "title": "alice",
        "subStatus": "subscribable",
        "status": "public"
    },
    "response": {
        "entry_data": {
            "ProfilePage": [
                {
                    "graphql": {
                        "user": {
                            "id": 123456789,
                            "is_private": False
                        }
                    }
                }
            ]
        }
    }
}

IG_API_SCRP_USERNAME_EXIST_PRIV = {
    "query": {
        "username": "alice",
        "internal_id": 123456789,
        "title": "alice",
        "subStatus": "subscribable",
        "status": "private"
    },
    "response": {
        "entry_data": {
            "ProfilePage": [
                {
                    "graphql": {
                        "user": {
                            "id": 123456789,
                            "is_private": True
                        }
                    }
                }
            ]
        }
    }
}

IG_API_SCRP_USERNAME_NO_EXIST = {
    "query": {
        "username": "alice",
        "subStatus": "NotExists",
        "status": "unknown"
    },
    "response": {
        "entry_data": {
        }
    }
}


def ig_html_src(ig_scrape_api):
    return "window._sharedData = " + \
        json.dumps(ig_scrape_api) + \
        ";</script>"


def test_extract_data_username():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")

    api_queries = [IG_API_SCRP_USERNAME_EXIST_PUB,
                   IG_API_SCRP_USERNAME_EXIST_PRIV,
                   IG_API_SCRP_USERNAME_NO_EXIST]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=ig_html_src(api["response"]))
            response = igram.extract_data(api["query"])
        assert_equal(response, api["query"])


IG_API_SCRP_P_EXIST_PUB = {
    "query": {
        "username": "",
        "internal_id": 123456789,
        "title": "alice",
        "subStatus": "subscribable",
        "status": "public",
        "data": {
            "p": "A-8Rimyao89"
        }
    },
    "response": {
        "entry_data": {
            "PostPage": [
                {
                    "graphql": {
                        "shortcode_media": {
                            "owner": {
                                "username": "alice",
                                "id": 123456789
                            }
                        }
                    }
                }
            ]
        }
    }
}

IG_API_SCRP_P_NO_EXIST_OR_PRIV = {
    "query": {
        "username": "",
        "internal_id": 123456789,
        "title": "alice",
        "subStatus": "subscribable",
        "status": "public",
        "data": {
            "p": "A-8Rimyao89"
        }
    },
    "response": {
    }
}


def test_extract_data_p():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/p\/([A-Za-z0-9-_]{1,30})")

    api_queries = [IG_API_SCRP_P_EXIST_PUB,
                   IG_API_SCRP_P_NO_EXIST_OR_PRIV]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, text=ig_html_src(api["response"]))
            response = igram.extract_data(api["query"])
        api["query"]["username"] = api["query"]["title"]
        assert_equal(response, api["query"])


IG_API_SCRP_INVALID = {
    "query": {
        "username": "",
        "subStatus": "noSpecificMethodToExtractData",
        "status": "unknown",
        "data": {
        }
    },
    "response": {
    }
}


def test_extract_data_invalid():
    igram = Instagram()

    matcher = re.compile(r"")

    api = IG_API_SCRP_INVALID
    with requests_mock.mock() as mock_get:
        mock_get.get(matcher, text=ig_html_src(api["response"]))
        response = igram.extract_data(api["query"])

    del api["query"]["username"]
    assert_equal(response, api["query"])


GLOBAL_COUNTER = 0


def custom_matcher_no_json(request):
    global GLOBAL_COUNTER
    # print(request.path_url)
    if GLOBAL_COUNTER == 0:
        GLOBAL_COUNTER += 1
        return requests_mock.create_response(request, status_code=200, text="THIS IS A TEST")
    else:
        GLOBAL_COUNTER = 0
        return requests_mock.create_response(request, status_code=200, text=ig_html_src(IG_API_SCRP_USERNAME_EXIST_PUB["response"]))


def test_extract_data_no_json_error():
    igram = Instagram()

    api = IG_API_SCRP_USERNAME_EXIST_PUB
    with requests_mock.mock() as mock_get:
        mock_get.add_matcher(custom_matcher_no_json)
        response = igram.extract_data(api["query"])
    assert_equal(response, api["query"])
