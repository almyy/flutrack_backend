from pymongo import MongoClient
import requests
import os
import pprint

geo_api_key = os.environ.get('GEOLOCATION_KEY')
mongo_uri = os.environ.get('MONGOLAB_URI')
if mongo_uri:
    client = MongoClient(mongo_uri)
    print('client connected')
    db = client.heroku_k99m6wnb
    tweets = db.tweets
else:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.flutrack
    tweets = db.tweets


def populate_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/results.json")
    data = r.json()
    populate_from_json(data)


def populate_from_json(data):
    for tweet in data:
        lat = tweet['latitude']
        lng = tweet['longitude']
        city = lookup_city(lat, lng)
        tweets.insert({
            'username': tweet['user_name'],
            'lat': lat,
            'lng': lng,
            'text': tweet['tweet_text'],
            'city': city
        })


def lookup_city(lat, lng):
    params = {
        'format': 'json',
        'lat': lat,
        'lng': lng,
        'addressdetails': 1
    }
    url = 'http://nominatim.openstreetmap.org/reverse?format=json&lat='+lat+'&lng='+lng+'&addressdetails=1'
    result = requests.get(url).json()
    pprint.pprint(result)
    return 'Nein'


def __main__():
    populate_from_flutrack_api()


__main__()
