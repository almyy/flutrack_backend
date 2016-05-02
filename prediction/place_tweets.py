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
        'result_type': 'locality'
    }
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    result = requests.get(url, params).json()
    if len(result['results']) > 0:
        for component in result['results'][0]['address_components']:
            print(component['types'])
            if 'locality' in component['types']:
                return component['long_name']
        # return result['results'][0]['address_components'][0]['long_name']
    else:
        return 'Unknown location'

if __name__ == '__main__':
    cursor = collection.find()
    for doc in cursor:
        print(lookup_tweet(doc))
