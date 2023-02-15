import time
import calendar
import datetime
import logging
import json
from random import randrange
from feedgram.lib.utils import get_url

class Error(Exception):
    pass


class RateLimitError(Error):
    pass

class Flickr:
    """
        The purpose of this class is to act as a layer between the app and the social
        network. It manages all the comunication back and forth, and all the functions
        related to this social network.
    """

    def __init__(self):
        self.__logger = logging.getLogger('telegram_bot.flickr')
        self.__logger.info('Creating an instance of Flickr')

    def __get_json_from_url(self, url, social):
        before_json_exception = False
        while True:
            content = get_url(url)
            if social == "flickr-username":
                tmp = content["content"].find("/services/feeds/photos_public.gne?id&#x3D;") #If it finds nothing returns -1, else the index
                if tmp == -1: #If it finds nothing means that the user doesn't exist
                    return None
                content["content"] = content["content"][tmp+len("/services/feeds/photos_public.gne?id&#x3D;"):]
                content["content"] = {"internal_id": content["content"][:content["content"].find("&amp")]}
                return content["content"]
            elif social == "flickr-internal_id":
                content["content"] = content["content"][content["content"].find("jsonFlickrFeed(")+15:-1] #15 is the length of "jsonFlickrFeed("
                try:
                    return json.loads(content["content"]) #If the internal_id is not valid flickr's responds with a non-json page
                except:
                    print("The content of the flickr's url is not json, I assume the account has been deleted...")
                    print("\n######START######\n" + content["content"] + "\n######END######") #Added this line only to investigate about an issue about false positive detections of deleted accounts. Remove this when finished.
                    return {"error": True, "reason": "userNotFound"}
            try:
                content["content"] = json.loads(content["content"])
                if before_json_exception:
                    before_json_exception = False
                    self.__logger.warning("This time the the content retrived contains json! :D")
                if content["status_code"] == 404:
                    content["content"] = {"entry_data": {}}
                return content["content"]
            except json.JSONDecodeError:
                if content["status_code"] == 404:
                    content["content"] = {"entry_data": {}}
                    return content
                before_json_exception = True
                wait_time = randrange(10, 20)
                self.__logger.warning("The content of the url is not json, now i print the content...")
                self.__logger.warning(content["content"])
                self.__logger.warning("Trying again in %s seconds...", wait_time)
            except RateLimitError:
                before_json_exception = True
                wait_time = randrange(60, 240)
                self.__logger.warning("Rate Limited...")
                self.__logger.warning("Trying again in %s seconds...", wait_time)
            time.sleep(wait_time)
            self.__logger.warning("Trying to retreive again the content from the url...")

    def extract_data(self, sn_account: dict) -> dict:
        """
            Given pieces of informations enough to univocally identify an user,
            etract data of such user querying the remote source.
            Arguments:
                sn_account: Dictionary with enough informations to univocally identify the user.
            Returns:
                Definitive informations gathered.
        """
        print(sn_account)
        if sn_account["internal_id"]:
            f = self.__get_json_from_url("http://api.flickr.com/services/feeds/photos_public.gne?id="+sn_account["internal_id"]+"&format=json", "flickr-internal_id")
            try:
                tmp = re.search("photos\/([a-zA-Z0-9]{1,32})", f["link"])
                sn_account["username"] = tmp.group(1)
                sn_account["title"] = tmp.group(1)
                sn_account["subStatus"] = "subscribable"
                sn_account["status"] = "public"
            except:
                sn_account["subStatus"] = "NotExists"
                sn_account["status"] = "unknown"
        elif sn_account["username"]:
            f = self.__get_json_from_url("https://www.flickr.com/photos/"+sn_account["username"]+"/", "flickr-username")
            print(f)
            try:
                sn_account["internal_id"] = f["internal_id"]
                sn_account["title"] = sn_account["username"]
                sn_account["subStatus"] = "subscribable"
                sn_account["status"] = "public"
            except TypeError:
                sn_account["subStatus"] = "NotExists"
                sn_account["status"] = "unknown"
        else:
            sn_account["subStatus"] = "noSpecificMethodToExtractData"
            sn_account["status"] = "unknown"
        return sn_account

    def get_feed(self, social_accounts: list) -> dict:

        messages = []
        queries = {}
        queries["update"] = []
        queries["delete"] = []

        for value in social_accounts:

            userId = value["internal_id"]
            user = value["username"]
            title = value["title"]
            status = value["status"]

            self.__logger.info("Getting JSON from Flickr of "+value["username"]+"...")
            f = self.__get_json_from_url("http://api.flickr.com/services/feeds/photos_public.gne?id="+userId+"&format=json", "flickr-internal_id")

            request_status = True
            if "error" in f: #Controllo che non ci siano errori come account non esistente (o cancellato) o chiave non valida
                reason = f["reason"]
                request_status = False
            elif "items" in f: #Controllo che il canale non sia vuoto
                if not f["items"]:
                    reason = "emptyChannel"
                    request_status = False

            if request_status: #Se l'account esiste e non è vuoto

                item_lastDate = int(value["retreive_time"])#-17280000

                item_lastDate_Temp = item_lastDate
                for post in f["items"]:
                    item_title = post["title"]
                    item_description = post["description"]
                    item_url = post["link"]
                    item_date = int(calendar.timegm(datetime.datetime.strptime(post["published"], "%Y-%m-%dT%H:%M:%SZ").timetuple()))
                    if item_date > item_lastDate:
                        messages.append({"type": "new_post", "social": "flickr", "internal_id": userId, "username": user, "title": title, "post_title": item_title, "post_description": item_description, "post_url": item_url, "media_source": None, "post_date": item_date})
                        if item_date > item_lastDate_Temp:
                            item_lastDate_Temp = item_date

                item_lastDate = item_lastDate_Temp

                queries["update"].append({'type':'retreive_time', 'social':'flickr', 'internal_id': userId, 'retreive_time': str(item_lastDate)})

            else:
                if reason == "userNotFound":
                    #Se l'account non esiste più allora lo cancello
                    self.__logger.info("Il profilo "+user+" non esiste più, ora lo cancello.")
                    queries["delete"].append({'type':'socialAccount', 'social':'flickr', 'internal_id': userId})
                    messages.append({"type": "deleted_account" ,"social": "flickr", "internal_id": userId, "username": user, 'title': title, "post_url": "https://www.flickr.com/people/"+user, "post_date": int(time.time())})
                elif reason == "emptyChannel":
                    pass
                else:
                    pass #Oltrepassato il rate limit od errore sconosciuto


        #Messaggi ordinati cronologicamente
        messages.reverse()
        
        return {'messages': messages, 'queries': queries}


