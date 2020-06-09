#!/usr/bin/env python3
import time
import logging
import requests

LOGGER = logging.getLogger('telegram_bot.utils')

HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Accept-Language": "en-US;q=0.9,en;q=0.8,en-GB;q=0.7"
}
"""
Custom headers with indicating an user-agent and the preferred languages.

This is in order to mask the bot as a comon browser with a common operative system
and a standard preferred language.
The goal is to not make it so obvious that is a bot making the requests.
"""

# For `requests` module exceptions handling see: https://2.python-requests.org/en/latest/api/
# For `decode` classs handling see: https://docs.python.org/3/library/codecs.html#codecs.decode


def get_url(url: str) -> dict:

    """Sends an http ``GET`` request to the issued url.

    Sends an http ``GET`` request to the issued url and returns a dictionary with
    the content and the status code of the response.

    Args:
        url: The already urlencoded Url with the payload.

    Returns:
        A dictionary containing the response with its `status_code` (int)
        and the decoded `content` (str).

    Raises:
        requests.RequestException: When there's a connection error or is lost.
        TypeError: When tere is a deconding error of the response.

    """

    i = 0
    before_get_url_exception = False
    while True:
        try:
            content = requests.get(url, headers=HEADERS, timeout=(3, 300))
            content = {
                "status_code": content.status_code,
                "content": content.content.decode("utf8")
            }
            if before_get_url_exception:
                before_get_url_exception = False
                LOGGER.info("Connection restored! :D")
            return content
        except requests.RequestException:
            before_get_url_exception = True
            LOGGER.warning("Connection error or lost, attempting to connect again in %s seconds... :(", 2**i)
        except TypeError:
            before_get_url_exception = True
            LOGGER.warning("Decoding error, attempting to connect again in %s seconds... :(", 2**i)
        time.sleep(2**i)
        LOGGER.warning("Re-rying to connect...")
        if i < 6:
            i = i + 1
