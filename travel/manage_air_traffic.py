import csv
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


def read_cities_from_file(city_file, geo_api_key):
    result = []
    with open(city_file) as f:
        index = 0
        for row in f:
            row = row.split(sep=',')
            json_res = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                    {'key': geo_api_key, 'address': row[0]}).json()
            result.append({
                'index': index,
                'zone': row[2].strip('\n'),
                'city': row[0],
                'location': json_res['results'][0]['geometry']['location'] if json_res['results'] is not None else 'Unknown',
                'bounding_box': json_res['results'][0]['geometry']['bounds'],
                'population': row[1].strip('\n')
            })
            index += 1
    return result


# Sort data from airport.api.aero on origin and destination airports.
def sort_per_origin(list_input):
    sorted_list = sorted(list_input, key=lambda k: (k['ORIGIN'], k['DEST']))
    current_origin = ['', '', 0]
    result = []
    for row in sorted_list:
        if row['ORIGIN'] != current_origin[0] or row['DEST'] != current_origin[1]:
            result.append(current_origin)
            current_origin = [row['ORIGIN'], row['DEST'], int(float(row['PASSENGERS']))]
        else:
            current_origin[2] += int(float(row['PASSENGERS']))
    result.pop(0)
    return result


# Initiate and sort the t100market database.
def read_air_travel_data(filename):
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file)
        origin_list = sort_per_origin(reader)
    return sorted(origin_list, key=lambda k: k[2])


# Adding airport codes of the relevant cities we are tracking
def populate_airports_from_json(airport_file):
    with open(airport_file) as data:
        result = json.load(data)
    return result


def calculate_travel_matrix(airport_data, data, matrix_size):
    city_matrix = [[0] * matrix_size for x in range(matrix_size)]
    shortened = []
    for key in airport_data:
        for airport in airport_data[key]:
            shortened.append(airport)

    for row in data:
        if row[0] in shortened and row[1] in shortened and row[2] != 0:
            origin_index = get_city_index(row[0], airport_data)
            destination_index = get_city_index(row[1], airport_data)
            city_matrix[origin_index][destination_index] += row[2]
            city_matrix[destination_index][origin_index] += row[2]


    for i in range(0, 52):
        for u in range(0, 52):
            city_matrix[i][u] = int((city_matrix[i][u] / 365))

    matrix_document = []
    index = 0
    for row in city_matrix:
        matrix_document.append({
            # city_list[index]: row
            'travel': row
        })
        index += 1
    return matrix_document


def get_city_index(airport_code, airports):
    for key in airports:
        if airport_code in airports[key]:
            return city_list.index(key)
    return -1


def map_airports_to_cities(api_lookup, res_dict):
    for airport in api_lookup['airports']:
        if airport['city'] in res_dict:
            if airport['code'] not in res_dict[airport['city']] and airport['code'] is not None:
                res_dict[airport['city']].append(airport['code'])
    return res_dict


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
