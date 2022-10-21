from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import re
import unicodedata
import demoji

def clean_tweet(tweet):

        # Normalize unicode characters
        tweet = unicodedata.normalize("NFKD", tweet)
        tweet = unicodedata.normalize("NFC", tweet)

        # Remove emojis
        tweet = demoji.replace(tweet, "")
        emoji_pattern = re.compile("["u"\U0001FA70-\U0001FAFF""]+", flags=re.UNICODE) # Some emojis are not found in demoji
        tweet = re.sub(emoji_pattern, '', tweet)

        # Remove emoticons e.g. ":)"
        with open('assets/emoticon_dict.p', 'rb') as fp:
            emoticon_Dict = pickle.load(fp)
        emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in emoticon_Dict) + u')')
        tweet = re.sub(emoticon_pattern, '', tweet)
        
        # Remove urls
        tweet = re.sub(r'http\S+', '', tweet)
        tweet = " ".join(tweet.split())

        # Remove hashtags and mentions at the end
        hashtag_pattern = re.compile("(( [#@]\S+)*)$")
        tweet = re.sub(hashtag_pattern, '', tweet)
        tweet = " ".join(tweet.split())

        # Remove punctuation signs
        punctuation_pattern = re.compile("[\?!.]*$")
        tweet = re.sub(punctuation_pattern, '', tweet)

        # Remove # and @ signs 
        hashtag_pattern = re.compile("#|@")
        tweet = re.sub(hashtag_pattern, '', tweet)

        tweet = " ".join(tweet.split())
        return tweet

def is_similar(tweet, es, index):
    res = es.search(
        index=index,
        body = {
            "query": {
                "match_all": {}
            },
        },
        size=10000
    )

    if len(res['hits']['hits']) == 0:
        return False
    
    tweets =  [hit['_source'] for hit in res['hits']['hits']]
    tweets_text = [tweet['clean_text'] for tweet in tweets]

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(tweets_text+[tweet])

    #   | new doc
    # --|---------
    # A |
    # B |
    # C |
    threshold = 0.8
    cosine_sim = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:])
    for sim in cosine_sim:
        if sim > threshold:
            return True
    return False

def time_unit_to_mins(topic):
    minutes = topic.time_interval
    if topic.time_unit == "hours":
        minutes *= 60
    elif topic.time_unit == "days":
        minutes *= 60 * 24
    return minutes