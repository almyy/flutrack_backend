from pymongo import MongoClient
import requests
import os
import json

geo_api_key = os.environ.get('GEOLOCATION_KEY')
mongo_uri = os.environ.get('MONGOLAB_URI')

if mongo_uri:
    client = MongoClient(mongo_uri)
    print('client connected')
    db = client.heroku_k99m6wnb
    db.tweets.drop()
    cities = db.cities
    tweets = db.tweets
    cursor = cities.find()
    city_bounds = []
    for document in cursor:
        city_bounds.append({'box': document['bounding_box'], 'city': document['city']})
else:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.flutrack
    cities = db.cities
    tweets = db.tweets


def populate_tweets_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/?time=60")
    data = json.loads(r.text)
    populate_from_json(data)


def populate_from_json(data):
    result = []
    for tweet in data:
        lat = tweet['latitude']
        lng = tweet['longitude']
        city = lookup_city_name(lat, lng)
        result.append({
            'text': tweet['tweet_text'],
            'city': city,
            'date': tweet['tweet_date']
        })
    tweets.insert(result)


def populate_cities_from_text(file):
    result = []
    with open(file) as f:
        index = 0
        for row in f:
            row = row.split(sep=',')
            json = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                {'key': os.environ.get('GEOLOCATION_KEY'), 'address': row[0]}).json()
            result.append({
                'index': index,
                'zone': row[2].strip('\n'),
                'city': row[0],
                'location': json['results'][0]['geometry']['location'],
                'bounding_box': json['results'][0]['geometry']['bounds'],
                'population': row[1].strip('\n')
            })
            index += 1
    cities.insert(result)


def lookup_city_name(lat, lng):
    for row in city_bounds:
        if is_within_bounds(lat, lng, row['box']):
            return row['city']
    cursor.rewind()
    return "Unknown city"



def is_within_bounds(lat, lng, box):
    return float(box['southwest']['lat']) < float(lat) < float(box['northeast']['lat']) and float(
            box['southwest']['lng']) < float(lng) < float(box['northeast']['lng'])


def populate_collections():
    populate_tweets_from_flutrack_api()
    populate_cities_from_text('data/cities.csv')


if __name__ == '__main__':
    populate_collections()
