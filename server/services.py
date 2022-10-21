from TwitterAPI import TwitterAPI, TwitterPager
from elasticsearch import Elasticsearch
import threading
import schedule
import time
import socket
import pickle
import os

from dotenv import load_dotenv
load_dotenv('.env') 

# Twitter credentials
CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")

twitter = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, auth_type='oAuth2', api_version='2')

# ElasticSearch credentials
HOST = 'elasticsearch'
PORT = 9200
ES_USER = 'elastic'
ES_PASSWORD = os.environ.get("ES_PASSWORD")
print(ES_PASSWORD)
es = Elasticsearch([{'host': HOST, 'port': PORT}], timeout=10000, http_auth=(ES_USER, ES_PASSWORD))
mappings = {
    'mappings': {
        'dynamic': 'false',
        'properties': {
            'tag': {'type': 'text'},
            'start_date': {'type':'date', 'format': 'date_time_no_millis'},
            'end_date': {'type':'date', 'format': 'date_time_no_millis'},
            'time_interval': {'type': 'integer'},
            'time_unit': {'type': 'text'},
            'stream_id': {'type':'integer'},
            'active': {'type': 'boolean'},
            'finished': {'type': 'boolean'},
            'lang': {'type': 'text'},
            'time_windows': { 
                'properties': {
                    'start_time': { 'type': 'date', 'format': 'date_time_no_millis'},
                    'global_narrative': {
                        'type': 'object',
                        'properties': {
                            'actors_dict': {'type': 'object'},
                            'ann_str': {'type': 'text'},
                            'drs_str': {'type': 'text'},
                            'events_dict': {'type': 'object'},
                            'input_text': {'type': 'text'},
                            'msc_str': {'type': 'text'},
                            'new_actors': {'type': 'text'},
                            'non_event_relations': {'type': 'text'},
                        }
                    },
                    'interval_narrative': {
                        'type': 'object',
                        'properties': {
                            'actors_dict': {'type': 'object'},
                            'ann_str': {'type': 'text'},
                            'drs_str': {'type': 'text'},
                            'events_dict': {'type': 'object'},
                            'input_text': {'type': 'text'},
                            'msc_string': {'type': 'text'},
                            'new_actors': {'type': 'text'},
                            'non_event_relations': {'type': 'text'},
                        }
                    },
                }
            }
        }
    }
}

# Create topics index and ignore if already exists
es.indices.create(index='topics', ignore=400, body=mappings)

# Thread for schedule
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()

def extract_narrative(text, lang, tools, date):

    print('Connecting to socket')
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.connect(('t2s', 65432)) # Should be set in env

    print('Extracting narrative')
    soc.sendall(pickle.dumps({
        'lang': lang,
        'text': text,
        'tools': tools,
        'publication_date': date,
    }))

    # total data partwise in an array
    data = []

    while True:
        try:
            incoming_part = soc.recv(4096)
            if not incoming_part:
                break
            data.append(incoming_part)
        except:
            print('Unable to connect to data server!')
            
    data = pickle.loads(b''.join(data))

    if 'error' in data:
        print(data['error'])
        return {}
        
    return data
