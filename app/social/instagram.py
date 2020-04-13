#!/usr/bin/env python3
import time
import logging
import json
from lib.utils import get_url

LOGGER = logging.getLogger('social.instagram')


class Instagram:

    def __init__(self):
        self.__logger = logging.getLogger('telegram_bot.instagram')
        self.__logger.info('Creating an instance of Instagram')


    # The content retreived here comes from this URL -> "https://www.instagram.com/"+user+"/"
    # For `json.loads` exceptions see: https://docs.python.org/3/library/json.html#json.loads


    @classmethod
    def __get_json_from_url(cls, url):
        before_json_exception = False
        while True:
            content = get_url(url)
            content = content[content.find("window._sharedData = ")+len("window._sharedData = "):]
            content = content[:content.find(";</script>")]
            try:
                jsn = json.loads(content)
                if before_json_exception:
                    before_json_exception = False
                    LOGGER.warning("This time the the content retrived contains json! :D")
                return jsn
            except json.JSONDecodeError:
                before_json_exception = True
                LOGGER.warning("The content of the url is not json, now i print the content...")
                LOGGER.warning(content)
                time.sleep(1)
                LOGGER.warning("Trying to retreive again the content from the url...")

    def get_feed(self, social_accounts):

        #print(social_accounts)
        messages = []
        queries = {}
        queries["update"] = []
        queries["delete"] = []

        for value in social_accounts:

            user_id = value["internal_id"]
            user = value["username"]
            title = value["title"]
            status = value["status"]

            self.__logger.info("Getting JSON from Instagram of %s...", user)
            sn_payload = self.__get_json_from_url("https://www.instagram.com/"+user+"/")

            if sn_payload["entry_data"]: #Controlla se l'account è ancora esistente o meno
                if sn_payload["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_private"]: #Controlla se il profilo è privato o meno
                    if status != "private": #Se prima non era privato allora cambia il suo status, altrimenti non fare nulla
                        self.__logger.info("Il profilo %s è diventato privato", user)
                        queries["update"].append({'type':'status', 'status':'private', 'social':'instagram', 'internal_id': ''+user_id+''})
                        messages.append({"type": "now_private", "social": "instagram", "internal_id": user_id, "username": user, "post_url": "https://www.instagram.com/"+user+"/", "post_date": int(time.time())})
                else:
                    if status == "private": #Se prima era privato allora cambia il suo status, altrimenti non fare nulla
                        self.__logger.info("Il profilo %s da privato è ritornato pubblico", user)
                        queries["update"].append({'type':'status', 'status':'public', 'social':'instagram', 'internal_id': ''+user_id+''})

                    last_post_date = int(value["retreive_time"]) -1728000

                    #print("Got "+str(lastPostDate))

                    last_post_date_temp = last_post_date

                    username = sn_payload["entry_data"]["ProfilePage"][0]["graphql"]["user"]["username"]

                    for post in sn_payload["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]:
                        taken_at_timestamp = int(post["node"]["taken_at_timestamp"])
                        if taken_at_timestamp > last_post_date:
                            shortcode = post["node"]["shortcode"]
                            source_url = post["node"]["display_url"]
                            try:
                                media_description = post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
                                messages.append({"type": "new_post", "social": "instagram", "internal_id": user_id, "username": username, "title": title, "post_title": None, "post_description": media_description, "post_url": "https://www.instagram.com/p/"+shortcode+"/", "media_source":source_url, "post_date": taken_at_timestamp})
                            except (KeyError, IndexError):
                                messages.append({"type": "new_post", "social": "instagram", "internal_id": user_id, "username": username, "title": title, "post_title": None, "post_description": None, "post_url": "https://www.instagram.com/p/"+shortcode+"/", "media_source":source_url, "post_date": taken_at_timestamp})
                            if int(taken_at_timestamp) > last_post_date_temp:
                                last_post_date_temp = int(taken_at_timestamp)

                    last_post_date = last_post_date_temp



                    queries["update"].append({'type':'retreive_time', 'social':'instagram', 'internal_id': ''+user_id+'', 'retreive_time': ''+str(last_post_date)+''})

            else:
                #Se l'account non esiste più allora lo cancello
                LOGGER.info("Il profilo %s non esiste più, ora lo cancello.", user)
                queries["delete"].append({'type':'socialAccount', 'social':'instagram', 'internal_id': ''+user_id+''})
                messages.append({"type": "deleted_account", "social": "instagram", "internal_id": user_id, "username": user, "title": title, "post_url": "https://www.instagram.com/"+user+"/", "post_date": int(time.time())})


        #Messaggi ordinati cronologicamente
        messages.reverse()

        return {'messages': messages, 'queries': queries}
