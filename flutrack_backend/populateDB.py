from pymongo import MongoClient
import requests

client = MongoClient()
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
        tweets.insert_one(tweet)


def __main__():
    populate_from_flutrack_api()


__main__()
