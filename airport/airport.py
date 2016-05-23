import json
import os

import requests
from bson.json_util import dumps, loads
from pymongo import MongoClient

mongo_uri = os.environ.get('MONGOLAB_URI')

db = MongoClient(mongo_uri).heroku_k99m6wnb
city_collection = db.cities
matrix_size = city_collection.count()
transportation_collection = db.transportation_matrix
city_list = []


# Query aiport.aero from flight data based on airports.
def get_flight_data():
    params = {'user_key': 'eb6c3e8d6fb060a9a99f7b9fd061013c'}
    r = requests.get('https://airport.api.aero/airport', params=params)
    result = r.text.replace("callback(", "").replace(")", "")
    result_json = json.loads(result)
    return result_json


# Get an instance of the queried flight data stored in the database.
def get_flight_data_local():
    result = dumps(db.airports.find())
    result = loads(result)
    return result[0]


def init_city_dictionary():
    res_dict = {}
    for row in city_collection.find():
        res_dict[row['city']] = []
        if row['city'] not in city_list:
            city_list.append(row['city'])
    return res_dict


def get_transportation_matrix():
    result_matrix = []
    for document in transportation_collection.find():
        result_matrix.append(document['travel'])
    return result_matrix
