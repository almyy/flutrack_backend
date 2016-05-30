import json
import os
from datetime import date

import requests
from pymongo import MongoClient

from travel import manage_air_traffic

geo_api_key = os.environ.get('GEOLOCATION_KEY')
mongo_uri = os.environ.get('MONGOLAB_URI')

airport_file = os.path.abspath(os.path.dirname(__file__)) + '/data/airports.json'
city_file = os.path.abspath(os.path.dirname(__file__)) + '/data/cities.csv'
t100market = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market.csv'


# Collect tweets from the last 60 days from the flutrack API.
def populate_tweets_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/?time=60")
    data = json.loads(r.text)
    populate_tweets_from_json(data)


# Check if the the tweets from flutrack have a location in one of the cities we are tracking.
def populate_tweets_from_json(data):
    result = []
    city_bounds = []
    for x in db.cities.find():
        city_bounds.append({'box': x['bounding_box'], 'city': x['city']})
    for tweet in data:
        lat = tweet['latitude']
        lng = tweet['longitude']
        city = lookup_city_name(lat, lng, city_bounds)
        if city:
            result.append({
                'text': tweet['tweet_text'],
                'city': city,
                'date': tweet['tweet_date']
            })
    tweets.insert(result)


# Populate the database with the cities we want to track.
def populate_cities_from_text():
    result = manage_air_traffic.read_cities_from_file(city_file, geo_api_key)
    cities.insert(result)


def lookup_city_name(lat, lng, city_bounds):
    for row in city_bounds:
        if is_within_bounds(lat, lng, row['box']):
            return row['city']
    return None


def is_within_bounds(lat, lng, box):
    return float(box['southwest']['lat']) < float(lat) < float(box['northeast']['lat']) and float(
            box['southwest']['lng']) < float(lng) < float(box['northeast']['lng'])


# Adding the travel data to the transportation matrix
def populate_transportation_matrix_from_csv(airport_data, data):
    matrix_size = db.cities.count()
    matrix_document = manage_air_traffic.calculate_travel_matrix(airport_data, data, matrix_size)
    db.transportation_matrix.insert(matrix_document)


def populate_collections():
    db.cities.drop()
    print("Adding cities...")
    populate_cities_from_text()
    print("Cities successfully added to database!")
    cursor = cities.find()
    city_list = []
    res_dict = {}
    for document in cursor:
        city_list.append(document['city'])
        res_dict[document['city']] = []
    db.tweets.drop()
    db.transportation_matrix.drop()
    db.airports.drop()
    print("Adding tweets...")
    populate_tweets_from_flutrack_api()
    print("Tweets successfully added!")
    print("Adding travel data...")
    manage_air_traffic.init_city_dictionary()
    airport_data = manage_air_traffic.populate_airports_from_json(airport_file)
    airports.insert(airport_data)
    airport_dictionary = manage_air_traffic.map_airports_to_cities(airport_data, res_dict)
    populate_transportation_matrix_from_csv(airport_dictionary, manage_air_traffic.read_air_travel_data(t100market))
    print("Travel data successfully added!")

db = MongoClient(mongo_uri).heroku_k99m6wnb
if __name__ == '__main__':
    cities = db.cities
    tweets = db.tweets
    airports = db.airports
    populate_collections()
    print("Done.")
