#!/usr/bin/env python3
import time
import logging
import requests

LOGGER = logging.getLogger('telegram_bot.utils')


# For `requests` module exceptions handling see: https://2.python-requests.org/en/latest/api/
# For `decode` classs handling see: https://docs.python.org/3/library/codecs.html#codecs.decode


def get_url(url):
    i = 0
    before_get_url_exception = False
    while True:
        try:
            content = requests.get(url, timeout=(3, 300)).content.decode("utf8")
            if before_get_url_exception:
                before_get_url_exception = False
                LOGGER.info("Connection restored! :D")
            return content
        except requests.RequestException:
            before_get_url_exception = True
            LOGGER.warning("Connection error or lost, attempting to connect again in %s seconds... :(", 2**i)
        except ValueError:
            before_get_url_exception = True
            LOGGER.warning("Decoding error, attempting to connect again in %s seconds... :(", 2**i)
        time.sleep(2**i)
        LOGGER.warning("Re-rying to connect...")
        if i < 6:
            i = i + 1
