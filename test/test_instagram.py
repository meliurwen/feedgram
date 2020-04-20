#!/usr/bin/env python3
import json
import re
import copy
from unittest import mock
import requests_mock
from nose.tools import assert_equal

from feedgram.social.instagram import Instagram

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


SOCIAL_QUERY_PRIVATE_NOW_PUBLIC = {
    "query": {
        "internal_id": "123456789",
        "username": "alice",
        "title": "alice",
        "status": "private",
        "retreive_time": 613008000
    },
    "response": {
        "entry_data": {
            "ProfilePage": [
                {
                    "graphql": {
                        "user": {
                            "id": 123456789,
                            "is_private": False,
                            "username": "alice",
                            "edge_owner_to_timeline_media": {
                                "edges": [
                                    {
                                        "node": {
                                            "taken_at_timestamp": 613008001,
                                            "shortcode": "B-8Nimggo19",
                                            "display_url": "https://scontent-mxp1-1.cdninstagram.com/v/t51.1445-17/e35/93191433_133356738528267_2151435490383986134_n.jpg?a_lot_of=trash",
                                            "edge_media_to_caption": {
                                                "edges": [
                                                    {
                                                        "node": {
                                                            "text": "Some test stuff"
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        }
    },
    "result": {
        "messages": [
            {
                "type": "new_post",
                "social": "instagram",
                "internal_id": "123456789",
                "username": "alice",
                "title": "alice",
                "post_title": None,
                "post_description": "Some test stuff",
                "post_url": "https://www.instagram.com/p/B-8Nimggo19/",
                "media_source": "https://scontent-mxp1-1.cdninstagram.com/v/t51.1445-17/e35/93191433_133356738528267_2151435490383986134_n.jpg?a_lot_of=trash",
                "post_date": 613008001
            }
        ],
        "queries": {
            "update": [
                {
                    "type": "status",
                    "status": "public",
                    "social": "instagram",
                    "internal_id": "123456789"
                },
                {
                    "type": "retreive_time",
                    "social": "instagram",
                    "internal_id": "123456789",
                    "retreive_time": "613008001"
                }
            ],
            "delete": [
            ]
        }
    }
}


SOCIAL_QUERY_DLT_OR_NO_EXIST = {
    "query": {
        "internal_id": "123456789",
        "username": "alice",
        "title": "alice",
        "status": "private",
        "retreive_time": 613008000
    },
    "response": {
        "entry_data": {
        }
    },
    "result": {
        "messages": [
            {
                "type": "deleted_account",
                "social": "instagram",
                "internal_id": "123456789",
                "username": "alice",
                "title": "alice",
                "post_url": "https://www.instagram.com/alice/",
                "post_date": 61300805
            }
        ],
        "queries": {
            "update": [
            ],
            "delete": [
                {
                    "type": "socialAccount",
                    "social": "instagram",
                    "internal_id": "123456789"
                }
            ]
        }
    }
}


SOCIAL_QUERY_PRIVATE_NOW_PUBLIC_NOTEXT = copy.deepcopy(SOCIAL_QUERY_PRIVATE_NOW_PUBLIC)
del SOCIAL_QUERY_PRIVATE_NOW_PUBLIC_NOTEXT["response"]["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
SOCIAL_QUERY_PRIVATE_NOW_PUBLIC_NOTEXT["result"]["messages"][0]["post_description"] = None


SOCIAL_QUERY_PUBLIC_NOW_PRIVATE = copy.deepcopy(SOCIAL_QUERY_PRIVATE_NOW_PUBLIC)
SOCIAL_QUERY_PUBLIC_NOW_PRIVATE["query"]["status"] = "public"
SOCIAL_QUERY_PUBLIC_NOW_PRIVATE["response"]["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_private"] = True
SOCIAL_QUERY_PUBLIC_NOW_PRIVATE["response"]["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"] = {}

SOCIAL_QUERY_PUBLIC_NOW_PRIVATE["result"]["messages"] = [
    {
        "type": "now_private",
        "social": "instagram",
        "internal_id": "123456789",
        "username": "alice",
        "post_url": "https://www.instagram.com/alice/",
        "post_date": 61300805
    }
]
SOCIAL_QUERY_PUBLIC_NOW_PRIVATE["result"]["queries"] = {
    "update": [
        {
            "type": "status",
            "status": "private",
            "social": "instagram",
            "internal_id": "123456789"
        }
    ],
    "delete": [
    ]
}


@mock.patch('feedgram.social.instagram.time.time', mock.MagicMock(return_value=61300805))
def test_get_feed():
    igram = Instagram()

    matcher = re.compile(r"^(?:https:\/\/www\.|www\.)?instagram\.com\/([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)")

    api_queries = [SOCIAL_QUERY_PRIVATE_NOW_PUBLIC,
                   SOCIAL_QUERY_PRIVATE_NOW_PUBLIC_NOTEXT,
                   SOCIAL_QUERY_PUBLIC_NOW_PRIVATE,
                   SOCIAL_QUERY_DLT_OR_NO_EXIST]

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

    api_queries = [IG_API_SCRP_USERNAME_NO_EXIST]

    for api in api_queries:
        with requests_mock.mock() as mock_get:
            mock_get.get(matcher, status_code=404, text="trash")
            response = igram.extract_data(api["query"])
        assert_equal(response, api["query"])
