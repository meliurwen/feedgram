#!/usr/bin/env python3

import copy


# Module: test.test_database

SUB_BY_POST_LINK = {"social": "instagram",
                    "username": "il_post",
                    "internal_id": None,
                    "social_id": None,
                    "link": "www.instagram.com/il_post",
                    "data": {},
                    "subStatus": "social_id_not_present"
                    }

SUB_BY_POST_LINK2 = {"social": "instagram",
                     "username": "il_post",
                     "internal_id": "1769583068",
                     "social_id": None,
                     "link": "www.instagram.com/il_post",
                     "data": {},
                     "subStatus": "subscribable",
                     "title": "il_post",
                     "status": "public"
                     }

QUERY_TODO_UPDATE = {"update": [{"type": "retreive_time",
                                 "social": "instagram",
                                 "internal_id": "1769583068",
                                 "retreive_time": "999999999"
                                 },
                                {"type": "status",
                                 "social": "instagram",
                                 "internal_id": "1769583068",
                                 "status": "private"
                                 }
                                ],
                     "delete": []
                     }


# Module: test.test_instagram

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
        "title": "alice",
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

COMMAND_START = {
    "ok": True,
    "result": [
        {
            "update_id": 731419464,
            "message": {
                "message_id": 1256,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "dte": 1587049598,
                "text": "/start",
                "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
            },
        }
    ],
}

COMMAND_STOP = {
    "ok": True,
    "result": [
        {
            "update_id": 731419465,
            "message": {
                "message_id": 1257,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "date": 1587049603,
                "text": "/stop",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
    ],
}

NOT_COMMAND = {
    "ok": True,
    "result": [
        {
            "update_id": 731419483,
            "message": {
                "message_id": 1292,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "date": 1587065931,
                "sticker": {
                    "width": 512,
                    "height": 444,
                    "emoji": "🙏",
                    "set_name": "Animushit",
                    "is_animated": False,
                    "thumb": {
                        "file_id": "AAMCBAADGQEAAgUMXpi0S9HRxQd2Wqrpb0g3ekOugrMAAogAA4j_wBXpMkiwXLg5zwABbeAZAAQBAAdtAAM3NQACGAQ",
                        "file_unique_id": "AQAEbeAZAAQ3NQAC",
                        "file_size": 4334,
                        "width": 128,
                        "height": 111,
                    },
                    "file_id": "CAACAgQAAxkBAAIFDF6YtEvR0cUHdlqq6W9IN3pDroKzAAKIAAOI_8AV6TJIsFy4Oc8YBA",
                    "file_unique_id": "AgADiAADiP_AFQ",
                    "file_size": 44914,
                },
            },
        }
    ],
}

CALLBACK_HELP = {
    "ok": True,
    "result": [
        {
            "update_id": 731420180,
            "callback_query": {
                "id": "268511788082888011",
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 2120,
                    "from": {
                        "id": 987654321,
                        "is_bot": True,
                        "first_name": "TestbotID",
                        "username": "Territory_ID_Bot"
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private"
                    },
                    "date": 1588349911,
                    "text": "📖 Help\n\nYou can follow up to <i>10 social accounts</i>.\nSocials currently supported:\n • <i>Instagram</i>\nYou can follow only <b>public</b> accounts.\n\n<b>Receive Feeds:</b>\n • /sub <i>social</i> <i>username</i>\n • /sub <i>link</i>\n<b>Bot:</b>\n • /stop to stop and unsubscribe from the bot.",
                    "entities": [
                        {
                            "offset": 30,
                            "length": 18,
                            "type": "italic"
                        },
                        {
                            "offset": 82,
                            "length": 9,
                            "type": "italic"
                        },
                        {
                            "offset": 112,
                            "length": 6,
                            "type": "bold"
                        },
                        {
                            "offset": 130,
                            "length": 14,
                            "type": "bold"
                        },
                        {
                            "offset": 148,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 153,
                            "length": 6,
                            "type": "italic"
                        },
                        {
                            "offset": 160,
                            "length": 8,
                            "type": "italic"
                        },
                        {
                            "offset": 172,
                            "length": 4,
                            "type": "bot_command"
                        },
                        {
                            "offset": 177,
                            "length": 4,
                            "type": "italic"
                        },
                        {
                            "offset": 182,
                            "length": 4,
                            "type": "bold"
                        },
                        {
                            "offset": 190,
                            "length": 5,
                            "type": "bot_command"
                        }
                    ],
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "📋",
                                    "callback_data": "list_mode"
                                },
                                {
                                    "text": "🏷",
                                    "callback_data": "category_mode"
                                }
                            ]
                        ]
                    }
                },
                "chat_instance": "4557971575337840976",
                "data": "help_mode"
            }
        }],
}

WRONG_COMMAND = {
    "ok": True,
    "result": [
        {
            "update_id": 731419465,
            "message": {
                "message_id": 1257,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "date": 1587049603,
                "text": "/stops",
                "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
            },
        }
    ],
}

COMMAND_HELP = {
    "ok": True,
    "result": [
        {
            "update_id": 731419464,
            "message": {
                "message_id": 1256,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "TestUsername",
                    "type": "private",
                },
                "dte": 1587049598,
                "text": "/help",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
    ],
}

MSG_CMD_SUB_STANDARD = {
    "query": {
        "ok": True,
        "result": [
            {
                "update_id": 12345,
                "message": {
                    "message_id": 1256,
                    "from": {
                        "id": 123456789,
                        "is_bot": False,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "language_code": "en",
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "John",
                        "last_name": "Doe",
                        "username": "TestUsername",
                        "type": "private",
                    },
                    "dte": 159753,
                    "text": "/sub instagram testProfile",
                    "entities": [{"offset": 0, "length": 1, "type": "bot_command"}],
                },
            }
        ],
    },
    "response": {
        "social": "instagram",
        "username": "testProfile",
        "internal_id": 546545337,
        "title": "testProfile",
        "subStatus": "subscribable",
        "status": "public",
        "link": None,
        "data": {
        }
    },
    "result": [
        {
            "type": "sendMessage",
            "chat_id": 123456789,
            "markdown": "HTML",
            "text": "Social: instagram\nUser: testProfile\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"
        }
    ]
}

MSG_CMD_SUB_BAD_FORMAT = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_BAD_FORMAT["query"]["result"][0]["message"]["text"] = "/sub potato"
MSG_CMD_SUB_BAD_FORMAT["response"] = {}

MSG_CMD_SUB_BAD_FORMAT["result"][0]["text"] = "<b>⚠️Warning</b>\n<code>/sub</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/sub &lt;link&gt;</code>\n<i>or</i>\n<code>/sub &lt;social&gt; &lt;username&gt;</code>"

MSG_CMD_SUB_AGAIN = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_AGAIN["result"][0]["text"] = "Social: instagram\nUser: testProfile\nYou're already subscribed to this account!"

MSG_CMD_SUB_NO_EXIST = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_NO_EXIST["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileInexistent"
MSG_CMD_SUB_NO_EXIST["response"] = {
    "social": "instagram",
    "username": "testProfileInexistent",
    "subStatus": "NotExists",
    "status": "unknown",
    "data": {
    }
}
MSG_CMD_SUB_NO_EXIST["result"][0]["text"] = "Social: instagram\nThis account doesn't exists!"

MSG_CMD_SUB_UNXPCTD_SUB_STATUS = copy.deepcopy(MSG_CMD_SUB_NO_EXIST)
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileImpossible"
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["response"] = {
    "social": "instagram",
    "username": "testProfileImpossible",
    "subStatus": "banana",
    "status": "unknown",
    "data": {
    }
}
MSG_CMD_SUB_UNXPCTD_SUB_STATUS["result"][0]["text"] = "Social: instagram\nI don't know what happened! O_o\""

MSG_CMD_SUB_PRIVATE = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_PRIVATE["query"]["result"][0]["message"]["text"] = "/sub instagram testProfilePrivate"
MSG_CMD_SUB_PRIVATE["response"] = {
    "social": "instagram",
    "username": "testProfilePrivate",
    "internal_id": 741852963,
    "title": "testProfilePrivate",
    "subStatus": "subscribable",
    "status": "private",
    "link": None,
    "data": {
    }
}
MSG_CMD_SUB_PRIVATE["result"][0]["text"] = "Social: instagram\nUser: testProfilePrivate\nYou've been subscribed to a social account that is private!\nYou'll not receive feeds until it switches to public!"

MSG_CMD_SUB_UNXPCTD_STATUS = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_UNXPCTD_STATUS["query"]["result"][0]["message"]["text"] = "/sub instagram testProfileStrangeStatus"
MSG_CMD_SUB_UNXPCTD_STATUS["response"] = {
    "social": "instagram",
    "username": "testProfileStrangeStatus",
    "internal_id": 963852741,
    "title": "testProfileStrangeStatus",
    "subStatus": "subscribable",
    "status": "banana",
    "link": None,
    "data": {
    }
}
MSG_CMD_SUB_UNXPCTD_STATUS["result"][0]["text"] = "Social: instagram\nUser: testProfileStrangeStatus\nMmmh, something went really wrong, the status is unknown :/\nYou should get in touch with the admin!"

MSG_CMD_SUB_IG_HOME = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_HOME["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/testIgProfileLinkHome"
MSG_CMD_SUB_IG_HOME["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkHome",
    "internal_id": 897546782,
    "title": "testIgProfileLinkHome",
    "subStatus": "subscribable",
    "status": "public",
    "link": "https://www.instagram.com/testIgProfileLinkHome",
    "data": {
    }
}
MSG_CMD_SUB_IG_HOME["result"][0]["text"] = "Social: instagram\nUser: testIgProfileLinkHome\nYou've been successfully subscribed!\nFrom now on, you'll start to receive feeds from this account!"

MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/p/dD8-su2dF/"
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkP",
    "subStatus": "NotExistsOrPrivate",
    "status": "unknown",
    "link": "https://www.instagram.com/p/dD8-su2dF",
    "data": {
        "p": "dD8-su2dF"
    }
}
MSG_CMD_SUB_IG_P_NO_EXST_OR_PRIV["result"][0]["text"] = "Social: instagram\nThis account doesn't exists or is private!"

MSG_CMD_SUB_IG_P_NO_SPEC_MTHD = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["text"] = "/sub https://www.instagram.com/p/Yu9Jfi8/"
del MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["from"]["username"]
del MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["query"]["result"][0]["message"]["chat"]["username"]
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["response"] = {
    "social": "instagram",
    "username": "testIgProfileLinkP",
    "subStatus": "noSpecificMethodToExtractData",
    "status": "unknown",
    "link": "https://www.instagram.com/p/Yu9Jfi8",
    "data": {
        "p": "Yu9Jfi8"
    }
}
MSG_CMD_SUB_IG_P_NO_SPEC_MTHD["result"][0]["text"] = "Social: instagram\nMmmh, this shouldn't happen, no method (or specific method) to extract data."

MSG_CMD_SUB_INVALID_URL = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_INVALID_URL["query"]["result"][0]["message"]["text"] = "/sub https://www.potato.banana"
MSG_CMD_SUB_INVALID_URL["response"] = {}
MSG_CMD_SUB_INVALID_URL["result"][0]["text"] = "<b>⚠️Warning</b>\n<code>/sub</code> command badly compiled!\n\n<b>ℹ️ Tip</b>\nHow to use this command:\n<code>/sub &lt;link&gt;</code>\n<i>or</i>\n<code>/sub &lt;social&gt; &lt;username&gt;</code>"

MSG_CMD_SUB_INVALID_SOCIAL = copy.deepcopy(MSG_CMD_SUB_STANDARD)
MSG_CMD_SUB_INVALID_SOCIAL["query"]["result"][0]["message"]["text"] = "/sub banana potato"
MSG_CMD_SUB_INVALID_SOCIAL["response"] = {}
MSG_CMD_SUB_INVALID_SOCIAL["result"][0]["text"] = "Social not abilited or mistyped"


# Module: test.test_telegram

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

ONE_MESSAGE_STANDARD = {
    "type": "sendMessage",
    "text": "<b>⚠️TEST⚠️</b>\nTest message.",
    "chat_id": 123456789,
    "markdown": "HTML"
}

# More than 4096 chars (5120)
ONE_MESSAGE_STANDARD_LNG_TXT = {
    "type": "sendMessage",
    "text": "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",
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
