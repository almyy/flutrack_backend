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
    cities = db.cities

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


def populate_from_txt(file):

    with open(file) as f:
        for row in f:
            row = row.split(sep=',')
            json = requests.get('https://maps.googleapis.com/maps/api/geocode/json', {'key': os.environ.get('GEOLOCATION_KEY'), 'address': row[0]}).json()
            cities.insert({
                'city': row[0],
                'location': json['results'][0]['geometry']['location'],
                'population': row[1].strip('\n')
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


if __name__ == '__main__':
    populate_from_txt('../prediction/data/citypopulation.csv')
