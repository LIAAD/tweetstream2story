from flask import Flask
from flask_cors import CORS
from topic import Topic
import threading
from services import es, twitter, TwitterConnectionError
from utils import clean_tweet, is_similar

# Load topics from ElasticSearch "topics" index, containing metadata for each
topics = {}
examples = []
twitter_streams = {}

res = es.search(index='topics',size=1000)
for hit in res['hits']['hits']:
    data = hit['_source']
    topic = Topic(
        data['tag'],
        data['start_date'],
        data['end_date'],
        int(data['time_interval']),
        data['time_unit'],
        data['twitter_id'] if 'twitter_id' in data else 0,
        hit["_id"],
        data['active'],
        data['finished'],
        data['lang'],
        data['mode'] if 'mode' in data else "2",
    )

    topic.time_windows=data['time_windows'] if 'time_windows' in data else []

    if not 'user' in data:
        examples.append(topic)
    else:
        user = data['user']
        if user in topics:
            topics[user].append(topic)
        else:
            topics[user] = [topic]


def get_topic_by_es_id(id, user=""):
    if user == "":
        index = [index for index, topic in enumerate(examples) if topic.es_id == id]
        return examples[index[0]] if index else -1

    else:
        if not user in topics:
            return -1
        index = [index for index, topic in enumerate(topics[user]) if topic.es_id == id]
        return topics[user][index[0]] if index else -1


def get_topic_by_twitter_id(id):
    for user in topics:
        for topic in topics[user]:
            if topic.twitter_id == id:
                return topic
    return -1

def stream_tweets():
    while True:
        try:
            r = twitter.request('tweets/search/stream', {
                "tweet.fields": "created_at"
            })

            # Each item is a new tweet in the stream
            for item in r:
                
                if not "data" in item:
                    continue

                # Define fields for respective index
                tweet = {
                    "id": item["data"]["id"],
                    "text": item["data"]["text"],
                    "date": item["data"]["created_at"],
                }

                # Get rule that the tweet matches and respective topic
                # A tweet can match different topics
                for rule in item["matching_rules"]:
                    rule_id = rule["id"]

                    topic = get_topic_by_twitter_id(rule_id)
                    
                    if topic == -1:
                        continue

                    # Store tweet in ElasticSearch, in respective index, if it isn't similar to other tweets
                    es_id = topic.es_id.lower()
                    tweet["clean_text"] = clean_tweet(item["data"]["text"])
                    if is_similar(tweet["clean_text"], es, es_id):
                        continue

                    es.index(index=es_id, document=tweet)

        # Retry connection in case of stream interruption
        except TwitterConnectionError:
            pass
        
def get_rules():
    r = twitter.request('tweets/search/stream/rules', method_override='GET')
    print(f'[{r.status_code}] RULES: {r.text}')
    if r.status_code != 200: exit()
    res = r.json()
    ids = list(map(lambda x: (x['id'], x['tag']), res["data"])) if res["meta"]["result_count"] != 0 else []
    return ids
    
def delete_stream_rules():
    active_rules_ids = [x[0] for x in get_rules()]
    if len(active_rules_ids) == 0: return()
    print(active_rules_ids)
    r = twitter.request('tweets/search/stream/rules', {'delete': {"ids": active_rules_ids}})
    print(f'[{r.status_code}] DELETE RULES: {r.text}')
    if r.status_code != 200: exit()

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='frontend/build/', template_folder="frontend/build/")
    cors = CORS(app)
    return app

delete_stream_rules()
twitter_thread = threading.Thread(target=stream_tweets)
twitter_thread.start()