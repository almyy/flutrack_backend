from pymongo import MongoClient
import requests
from pymongo.errors import OperationFailure

client = MongoClient('mongodb://heroku_k99m6wnb:slu38scru44f1c5s2v4h60ig72@ds011238.mongolab.com:11238/heroku_k99m6wnb')
print('client connected')
db = client.flutrack_db
tweets = db.tweets


def populate_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/results.json")
    data = r.json()
    populate_from_json(data)


def populate_from_json(json):
    for t in json:
        tweet = {
            'lat': t['latitude'],
            'lng': t['longitude'],
            'username': t['user_name'],
            'text': t['tweet_text']
        }
        try:
            tweets.insert_one(tweet)
        except OperationFailure as e:
            print(e.details)


def __main__():
    populate_from_flutrack_api()


__main__()
