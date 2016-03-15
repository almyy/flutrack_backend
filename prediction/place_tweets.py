import os
import requests
import pprint
from pymongo import MongoClient

if os.environ.get('MONGOLAB_URI'):
    client = MongoClient(os.environ.get('MONGOLAB_URI'))
    db = client.heroku_k99m6wnb
else:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.flutrack

collection = db.tweets


def lookup_tweet(tweet):
    latlng = tweet['lat'] + ',' + tweet['lng']
    geo_api_key = os.environ.get('GEOLOCATION_KEY')
    params = {
        'latlng': latlng,
        'key': geo_api_key,
        'result_type': 'administrative_area_level_1'
    }
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    result = requests.get(url, params).json()
    city_name = result['results'][0]['address_components'][0]['long_name']

if __name__ == '__main__':
    cursor = collection.find_one()
    lookup_tweet(cursor)
