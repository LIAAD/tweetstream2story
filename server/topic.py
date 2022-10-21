import math
from utils import clean_tweet, time_unit_to_mins
from services import es, twitter, TwitterAPI, TwitterPager, schedule, extract_narrative
from datetime import datetime, timedelta

modes = {
    "NOW": "1",
    "FUTURE": "2",
    "PAST": "3",
}


class Topic:

    def __init__(
        self, tag, start_date, end_date,
        time_interval=10, time_unit="minutes",
        twitter_id=0, es_id=0,
        active=False, finished=False,
        lang="pt", mode=modes["NOW"], time_windows=[]
    ):

        self.tag = tag
        self.keywords = tag.split()
        self.lang = lang

        self.mode = mode                # {'past', 'future', 'now'}
        self.start_date = start_date    # UTC string YYYY-mm-DDTHH:MM:SSZ
        self.end_date = end_date
        self.time_interval = time_interval
        self.time_unit = time_unit

        self.active = active
        self.finished = finished

        self.twitter_id = twitter_id    # ID of the twitter rule used for streaming tweets, 0 if it's a past event
        self.es_id = es_id              # ID of this topic on the ElasticSearch index "topics"

        self.time_windows = time_windows

        if self.finished:
            return

        # Job scheduled to extract narrative every x time units
        self.results_job = None

        if mode == modes["FUTURE"]:
            print("schedule")
            [start_day, start_time] = self.start_date.split("T")
            [end_day, end_time] = self.end_date.split("T")

            start_time = start_time[0:5]  # HH:MM
            end_time = end_time[0:5]

            if (not self.active) and (not self.finished):
                schedule.every().day.at(start_time).do(self.start)

            if not self.finished:
                schedule.every().day.at(end_time).do(self.stop)

    def start(self):

        # Start twitter stream for this topic
        r = twitter.request(
            'tweets/search/stream/rules',
            {
                'add': [{
                    "value":  "(" + (" OR ".join(self.keywords)) + ") -is:retweet lang:" + self.lang,
                    "tag": self.tag
                }]
            }
        )
        print(f'[{r.status_code}] RULE ADDED: {r.text}')

        self.active = True
        self.twitter_id = r.json()["data"][0]["id"]
        self.start_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if self.time_unit == "minutes":
            self.results_job = schedule.every(
                self.time_interval).minutes.do(self.add_window)

        elif self.time_unit == "hours":
            self.results_job = schedule.every(
                self.time_interval).hours.do(self.add_window)

        elif self.time_unit == "days":
            self.results_job = schedule.every(
                self.time_interval).days.do(self.add_window)

        try:
            es.update("topics", self.es_id, body={
                "doc": {
                    "start_date": self.start_date,
                    "active": self.active
                }
            })
        except Exception as e:
            print(e)

        return schedule.CancelJob

    def add_window(self):

        print("Adding window to topic " + self.es_id)
        index = len(self.time_windows)
        if self.time_unit == "days":
            minutes = self.time_interval * 60 * 24
        elif self.time_unit == "hours":
            minutes = self.time_interval * 60
        else:
            minutes = self.time_interval

        # Dates in YYYY-MM-DD format
        start_date = datetime.fromisoformat(self.start_date[:-1])
        start_date = start_date.strftime("%Y-%m-%d")
        dateUTC = datetime.fromisoformat(
            self.start_date[:-1]) + timedelta(minutes=minutes*index)
        date = dateUTC.strftime("%Y-%m-%d")
        tools = {
            "AllenNLP": True,
            "AllenNLP (Sematic Role Labeling)": True,
            "NLTK": True,
            "py_heideltime": True,
            "spaCy": True,
            "Spacy (Objectal Linking)": True
        }

        # Global Narrative
        global_text = [tweet["_source"]["clean_text"] +
                       "." for tweet in self.results(index, True)]
        global_text = "\n".join(global_text)

        # Interval Narrative
        interval_text = [tweet["_source"]["clean_text"] +
                         "." for tweet in self.results(index, False)]
        interval_text = "\n".join(interval_text)

        try:
            global_narrative = extract_narrative(
                global_text, self.lang, tools, start_date)
        except Exception as e:
            print(e)
            global_narrative = {}

        try:
            interval_narrative = extract_narrative(
                interval_text, self.lang, tools, date)
        except Exception as e:
            print(e)
            interval_narrative = {}

        # Check which actors are new compared to graph of previews global window
        if ("actors_dict" in global_narrative):
            if index == 0:
                global_narrative["new_actors"] = list(
                    global_narrative["actors_dict"].values())
            else:
                prev_window = self.time_windows[index-1]
                if "actors_dict" in prev_window["global_narrative"]:
                    prev_actors = set(
                        prev_window["global_narrative"]["actors_dict"].values())
                    actors = set(global_narrative["actors_dict"].values())
                    new_actors = list(set(actors) - set(prev_actors))
                    global_narrative["new_actors"] = new_actors
                else:
                    global_narrative["new_actors"] = list(
                        global_narrative["actors_dict"].values())

            interval_narrative["new_actors"] = []

        time_window = {
            "start_time": dateUTC.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "global_narrative": global_narrative,
            "interval_narrative": interval_narrative
        }

        self.time_windows.append(time_window)

        # Update time windows on elasticsearch
        try:
            res = es.update(index="topics", id=self.es_id, doc={
                "time_windows": self.time_windows
            })
        except Exception as e:
            print(e)

        return time_window

    def stop(self):

        # Stop twitter stream for this topic
        r = twitter.request('tweets/search/stream/rules',
                            {'delete': {"ids": [self.twitter_id]}})
        print(f'[{r.status_code}] DELETE RULE: {r.text}')

        self.end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.active = False
        self.finished = True

        schedule.cancel_job(self.results_job)

        # Update topic on elasticsearch
        try:
            es.update("topics", self.es_id, body={
                "doc": {
                    "active": self.active,
                    "finished": self.finished,
                    "end_date": self.end_date,
                }
            })
        except Exception as e:
            print(e)

        return schedule.CancelJob

    def results(self, window_index=-1, isGlobal=False):

        # If window isn't specified, get results for next window
        if window_index == -1:
            window_index = len(self.time_windows)

        query = " ".join(self.keywords)
        minutes = self.time_interval if self.time_unit == "minutes" else self.time_interval*60

        global_start_time = datetime.fromisoformat(
            self.start_date[:-1]) if self.start_date[-1] == "Z" else datetime.fromisoformat(self.start_date)
        window_start_time = global_start_time + \
            timedelta(minutes=minutes*int(window_index))
        window_end_time = window_start_time + timedelta(minutes=minutes)

        dateQuery = {
            "lte": window_end_time.isoformat(),
            "gte": global_start_time.isoformat() if isGlobal else window_start_time.isoformat()
        }

        try:
            res = es.search(
                index=self.es_id.lower(),
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"text": query}},
                            ],
                            "filter": [{"range": {"date": dateQuery}}]
                        }
                    }
                },
                size=50,
                _source=["text", "clean_text", "date"],
                timeout=f"{minutes}m"
            )

            # Sort tweets chronologically
            results = res['hits']['hits']
            results.sort(key=lambda x: x["_source"]["date"], reverse=False)
            return results

        except Exception as e:
            print(e)

        return {}



    def rebuild_results(self):
        '''
        # Updating clean_text for all documents
        for entry in self.es_iterate_all_documents(es, self.es_id.lower()):
            es.update(self.es_id.lower(), id=entry["_id"], body={
                "doc": {
                    "clean_text": clean_tweet(entry["_source"]["text"])
                }
            })
        '''

        query = " ".join(self.keywords)

        # Convert to minutes for elasticsearch query
        minutes = time_unit_to_mins(self)

        window_count = 0
        start_date = 0
        if self.start_date[-1] == "Z":
            start_date = datetime.fromisoformat(self.start_date[:-1])
            window_count = math.floor((datetime.fromisoformat(
                self.end_date[:-1]) - start_date)/timedelta(minutes=minutes))

        if '.' in self.start_date:
            start_date = datetime.fromisoformat(self.start_date.split('.')[0])
            window_count = math.floor((datetime.fromisoformat(
                self.end_date.split('.')[0]) - start_date)/timedelta(minutes=minutes))

        for i in range(window_count):
            window_start_time = start_date + timedelta(minutes=minutes*i)
            window_end_time = window_start_time + timedelta(minutes=minutes)
            window = {
                "start_time": window_start_time,
                "interval_results": [],
                "global_results": []
            }

            # Interval Results
            try:
                res = es.search(
                    index=self.es_id.lower(),
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {"match": {"text": query}},
                                ],
                                "filter": [{"range": {"date": {
                                    "gte": window_start_time.isoformat(),
                                    "lte": window_end_time.isoformat()
                                }}}]
                            }
                        }
                    },
                    size=50,
                    _source=["text", "clean_text", "date"],
                    timeout=f"{minutes}m"
                )

                # Sort tweets chronologically
                interval_results = res['hits']['hits']
                interval_results.sort(
                    key=lambda x: x["_source"]["date"], reverse=False)
                window["interval_results"] = interval_results

            except Exception as e:
                print(e)

            # Global Results
            try:
                res = es.search(
                    index=self.es_id.lower(),
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {"match": {"text": query}},
                                ],
                                "filter": [{"range": {"date": {
                                    "lte": window_end_time.isoformat()
                                }}}]
                            }
                        }
                    },
                    size=50,
                    _source=["text", "clean_text", "date"],
                    timeout=f"{minutes}m"
                )

                # Sort tweets chronologically
                global_results = res['hits']['hits']
                global_results.sort(
                    key=lambda x: x["_source"]["date"], reverse=False)
                window["global_results"] = global_results

            except Exception as e:
                print(e)

            self.time_windows.append(window)


    def es_iterate_all_documents(self, es, index, pagesize=1000, **kwargs):
        """
        Helper to iterate ALL values from
        Yields all the documents.
        """
        offset = 0
        while True:
            result = es.search(index=index, **kwargs, body={
                "size": pagesize,
                "from": offset
            })
            hits = result["hits"]["hits"]
            # Stop after no more docs
            if not hits:
                break
            # Yield each entry
            yield from (hit for hit in hits)
            # Continue from there
            offset += pagesize

    def to_dict(self):
        return {
            "tag": self.tag,
            "keywords": self.keywords,
            "lang": self.lang,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "time_interval": self.time_interval,
            "time_unit": self.time_unit,
            "active": self.active,
            "finished": self.finished,
            "twitter_id": self.twitter_id,
            "es_id": self.es_id,
            "mode": self.mode,
            "time_windows": self.time_windows
        }

    def retrieve_past_tweets(self, key, secret):

        twitter_api = TwitterAPI(
            key, secret, auth_type='oAuth2', api_version='2')
        print("Retrieving past tweets: " + str(self.es_id))
        self.active = True
        query = "(" + (" ".join(self.keywords)) + \
            ") -is:retweet lang:" + self.lang,
        r = TwitterPager(twitter_api, 'tweets/search/all', {
            "query": query,
            "max_results": 100,
            "tweet.fields": "created_at",
            "start_time": self.start_date,
            "end_time": self.end_date
        })

        # With OAuth2, 450 requests/15 mins = 1 request every 2 secs
        for item in r.get_iterator(wait=2):
            if "text" in item:
                tweet = {
                    "id": item['id'],
                    "text": item['text'],
                    "date": item['created_at'],
                    "clean_text": clean_tweet(item['text'])
                }
                try:
                    es.index(index=self.es_id.lower(), document=tweet)
                except Exception as e:
                    print(e)

            elif "message" in item:
                print(item["message"])

        self.finished = True
        self.active = False

        try:
            es.update("topics", self.es_id, body={
                "doc": {
                    "start_date": self.start_date,
                    "active": self.active
                }
            })
        except Exception as e:
            print(e)

        # self.rebuild_results()
