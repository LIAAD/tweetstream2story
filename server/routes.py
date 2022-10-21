import pickle
import time
from flask import abort, render_template, request
from topic import Topic
from app import create_app, es, topics, examples, get_topic_by_es_id
from services import TwitterAPI, es, extract_narrative, threading

app = create_app()

@app.route('/')
def load_template():
    return render_template("index.html")


@app.route('/api/demo/', methods=['POST'])
def api_post():
    print("POST new narrative extraction.....")

    json_parsed = request.json

    # Validation
    if json_parsed['lang'] != 'pt' and json_parsed['lang'] != 'en':
        print("Lang must be 'pt' or 'en'")
        return pickle.dumps({"error": "Lang must be 'pt' or 'en"})

    if len(json_parsed['text']) > 7500:
        print("Text too large: " + str(len(json_parsed['text'])))
        return pickle.dumps({"error": "Text too large"})

    #print(f"Input Text: \n{json_parsed['text']}")

    data = extract_narrative(
        json_parsed['text'],
        json_parsed['lang'],
        json_parsed['tools'],
        time.strftime("%Y-%m-%d"),
    )

    return data


@app.route('/api/topics/', methods=['GET'])
def get_topics():
    print(request.headers.get("Authorization"))
    if request.headers.get("Authorization"):
        user = request.headers.get('Authorization').split()[1]
        user_topics = topics[user] if user in topics else []
        return {"topics": [topic.to_dict() for topic in user_topics]}

    else:
        return {"topics": [topic.to_dict() for topic in examples]}


@app.route('/api/topic/<id>', methods=['GET'])
def get_topic(id):
    if request.headers.get("Authorization"):
        user = request.headers.get('Authorization').split()[1]
        topic = get_topic_by_es_id(id, user)
    else:
        topic = get_topic_by_es_id(id)

    if topic == -1:
        abort(404, description="Topic not found")

    print("GET topic: " + id)

    return {"topic": topic.to_dict()}

@app.route('/api/topic/', methods=['POST'])
def add_topic():
    user = request.headers.get('Authorization').split()[1]

    query = request.json["query"]
    print("POST new topic: " +  query)

    # Twitter Credentials required for retrieving tweets in the past
    if request.json["mode"] == 3:
        try:
            r = TwitterAPI(request.json["consumerKey"], request.json["consumerSecret"], auth_type="oAuth2", api_version='2')
        except Exception as e:
            print(e)
            abort(403, description="Invalid Twitter API credentials")

    topic = Topic(
        tag = query,
        start_date = request.json["startDate"],
        end_date = request.json["endDate"],
        time_interval = request.json["timeInterval"],
        time_unit = request.json["timeUnit"],
        lang = request.json["lang"],
        mode = request.json["mode"]
    )

    doc = topic.to_dict()
    doc['user'] = user
    res = es.index(index="topics", document=doc)
    topic.es_id = res["_id"]
    es.indices.create(index=topic.es_id.lower(), ignore=400)

    if not user in topics:
        topics[user] = []
    topics[user].append(topic)

    if topic.mode=='3':
        thread = threading.Thread(target=topic.retrieve_past_tweets, kwargs={"key": request.json["consumerKey"], "secret": request.json["consumerSecret"]})
        thread.start()
    
    return {"topic": topic.to_dict()}


@app.route('/api/start_topic/', methods=['POST'])
def start_topic():
    user = request.headers.get('Authorization').split()[1]
    id = request.json['es_id']
    topic = get_topic_by_es_id(id, user)

    if topic == -1:
        abort(404, description="Topic not found")

    print("POST Start streaming topic: " + str(id))

    topic.start()
    return {"topic": topic.to_dict()}


@app.route('/api/stop_topic/', methods=['POST'])
def stop_topic():
    user = request.headers.get('Authorization').split()[1]
    id = request.json['es_id']
    topic = get_topic_by_es_id(id, user)

    if topic == -1:
        abort(404, description="Topic not found")

    print("POST Stop streaming topic: " + id)

    topic.stop()
    return {"topic": topic.to_dict()}


@app.route("/api/delete_topic/", methods=["DELETE"])
def delete_topic():
    if not request.headers.get('Authorization'):
        abort(403, "You don't have permissions to delete this topic.")
        
    user = request.headers.get('Authorization').split()[1]
    id = request.json['es_id']
    
    index = [index for index, topic in enumerate(topics[user]) if topic.es_id == id]
    topic = topics[user].pop(index[0]) if index else -1
    
    if topic == -1:
        abort(404, description="Topic not found")

    print("DELETE topic: " + id)

    if topic.active:
        topic.stop()

    es.delete(index="topics", id=id)
    es.indices.delete(index=topic.es_id.lower(), ignore=[400, 404])

    return {"topic": topic.to_dict()} 


@app.route("/api/topic/<id>/window/<window_index>/tweets", methods=["GET"])
def get_window_tweets(id, window_index):

    user = request.headers.get('Authorization').split()[1]
    topic = get_topic_by_es_id(id)

    if topic == -1:
        if not request.headers.get('Authorization'):
            abort(403, "You don't have permissions to view these tweets.")
        topic = get_topic_by_es_id(id, user)

    if topic == -1:
        abort(404, description="Topic not found")

    try:
        tweets = {
            "global_tweets": topic.results(window_index, True), # global tweets,
            "interval_tweets": topic.results(window_index, False) # interval tweets
        }
    except Exception as e:
        abort(500, description="Error retrieving tweets")
    
    return {"tweets": tweets}


@app.route("/api/topic/<id>/tweets/", methods=["GET"])
def get_tweets(id):
    user = request.headers.get('Authorization').split()[1]
    topic = get_topic_by_es_id(id, user)
    print("GET Tweets for topic: " + id)

    if topic == -1:
        abort(404, "Topic not found")

    res = es.search(index=id.lower(), query={"match_all": {}})
    return {"tweets": res['hits']['hits']}


@app.route("/api/topic/<id>/results/", methods=["GET"])
def get_results(id):
    user = request.headers.get('Authorization').split()[1]
    topic = get_topic_by_es_id(id, user)
    if topic == -1:
        abort(404, "Topic not found")

    print("GET Results for topic: " + id)

    return {"results": topic.time_windows}

# ------------------ #
# Development routes #
# ------------------ #

@app.route('/api/topic/<id>/narrative/', methods=['POST'])
def add_window(id):
    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, description="Topic not found")
    return topic.add_window()

@app.route('/api/topic/<id>/narrative/<window_index>', methods=['POST'])
def extract_topic_narrative(id, window_index):

    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, description="Topic not found")

    window_index=int(window_index)

    print("POST new narrative extraction.....")
    json_parsed = request.json
    topic = get_topic_by_es_id(id)

    isGlobal = json_parsed['mode'] == 'global'
    text = [tweet["_source"]["clean_text"] + "." for tweet in topic.results(window_index, isGlobal)]
    text = "\n".join(text)

    if json_parsed['mode'] == 'global' and 'global_narrative' in topic.time_windows[window_index]:
        if topic.time_windows[window_index]['global_narrative'] != {}:
            return topic.time_windows[window_index]['global_narrative']
    if json_parsed['mode'] == 'interval' and 'interval_narrative' in topic.time_windows[window_index]:
        if topic.time_windows[window_index]['interval_narrative'] != {}:
            return topic.time_windows[window_index]['interval_narrative']
    
    # Validation
    if json_parsed['lang'] != 'pt' and json_parsed['lang'] != 'en':
        print("Lang must be 'pt' or 'en'")
        return pickle.dumps({"error": "Lang must be 'pt' or 'en"})

    if len(text) > 7500:
        print("Text too large: " + str(len(json_parsed['text'])))
        return pickle.dumps({"error": "Text too large"})

    #print(f"Input Text: \n{json_parsed['text']}")

    data = extract_narrative(
        json_parsed['text'],
        json_parsed['lang'],
        json_parsed['tools'],
        time.strftime("%Y-%m-%d"),
    )

    if json_parsed['mode'] == 'global':
        topic.time_windows[window_index]['global_narrative'] = data
    if json_parsed['mode'] == 'interval':
        topic.time_windows[window_index]['interval_narrative'] = data
    
    time_windows = [
        { 
            "start_time": window["start_time"],
            "global_narrative": window['global_narrative'] if 'global_narrative' in window else {},
            "interval_narrative": window['interval_narrative'] if 'interval_narrative' in window else {}
        }
        for window in topic.time_windows
    ]
    
    try:
        res = es.update(index="topics", id=id, doc = {
            "time_windows": time_windows
        })
        print(res)
    except Exception as e:
        print(e)

    if data == {}:
        abort(400, "Request missing id parameter")

    return data

@app.route('/api/topic/<id>/narrative/last', methods=['DELETE'])
def remove_last_window(id):
    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, description="Topic not found")
    
    try:
        topic.time_windows.pop()
        res = es.update(index="topics", id=topic.es_id, doc = {
            "time_windows": topic.time_windows
        })
        print(res)
    except Exception as e:
        print(e)

    return {"topic": topic.to_dict()}

@app.route('/api/topic/<id>/narrative', methods=['DELETE'])
def remove_windows(id):
    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, description="Topic not found")
    
    try:
        topic.time_windows = []
        res = es.update(index="topics", id=topic.es_id, doc = {
            "time_windows": topic.time_windows
        })
        print(res)
    except Exception as e:
        print(e)

    return {"topic": topic.to_dict()}

@app.route("/api/topic/<id>/rebuild_results/", methods=["GET"])
def rebuild_results(id):
    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, "Topic not found")

    topic.rebuild_results()
    return {"results": topic.time_windows}

@app.route('/api/topic/<id>/new_actors', methods=['POST'])
def add_colors_graph(id):

    topic = get_topic_by_es_id(id)
    if topic == -1:
        abort(404, "Topic not found")

    windows = len(topic.time_windows)
    if "actors_dict" in topic.time_windows[0]["global_narrative"]:
        topic.time_windows[0]["global_narrative"]["new_actors"] = list(topic.time_windows[0]["global_narrative"]["actors_dict"].values())
        topic.time_windows[0]["interval_narrative"]["new_actors"] = []

    for i in range(1, windows):
        prev_window = topic.time_windows[i-1]
        window = topic.time_windows[i]
        if "actors_dict" in prev_window["global_narrative"]:
            prev_actors = set(prev_window["global_narrative"]["actors_dict"].values())
            actors = set(window["global_narrative"]["actors_dict"].values())
            new_actors = list(set(actors) - set(prev_actors))
            window["global_narrative"]["new_actors"] = new_actors
        else: 
            new_actors = window["global_narrative"]["new_actors"] = list(window["global_narrative"]["actors_dict"].values())

        window["interval_narrative"]["new_actors"] = []

    try:
        res = es.update(index="topics", id=topic.es_id, doc = {
            "time_windows": topic.time_windows
        })
        print(res)
    except Exception as e:
        print(e)

    return {"topic": topic.to_dict()}

@app.route("/api/topic/<id>/set_finished/", methods=["GET"])
def set_finished(id):
    topic = get_topic_by_es_id(id)

    if topic == -1:
        abort(404, "Topic not found")
    
    res = es.search(index="topics", query={"match_all": {}})
    print(res['hits'])

    res= es.update(index="topics", id=id, doc ={
        "finished": True
    })
    print(res)
    return {"topic": topic.to_dict()}

@app.route("/api/delete_topic/admin", methods=["DELETE"])
def delete_topic_admin():

    id = request.json['es_id']
    index = [index for index, topic in enumerate(examples) if topic.es_id == id]
    topic = examples.pop(index[0]) if index else -1
    
    if topic == -1:
        abort(404, description="Topic not found")

    print("DELETE topic: " + id)

    if topic.active:
        topic.stop()

    es.delete(index="topics", id=id)
    es.indices.delete(index=topic.es_id.lower(), ignore=[400, 404])

    return {"topic": topic.to_dict()} 

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
