from pymongo import MongoClient
import requests
import os
import json

mongo_uri = os.environ.get('MONGOLAB_URI')
if mongo_uri is not None:
    client = MongoClient(mongo_uri)
    print('client connected')
    db = client.heroku_k99m6wnb
    tweets = db.tweets


def populate_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/results.json")
    data = r.json()
    populate_from_json(data)


def populate_from_json(data):
    print(json.dumps(data))

# def extract_location(json):


def __main__():
    populate_from_flutrack_api()


__main__()
