import csv
import requests
import json
import os

import xlrd
from pymongo import MongoClient
from bson.json_util import dumps, loads

# t100 = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market.csv'
# t100_2000 = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market2000.csv'
# chosen_airports = os.path.abspath(os.path.dirname(__file__)) + '/data/chosen_airports.csv'
dummy_matrix_file = os.path.abspath(os.path.dirname(__file__)) + '/data/dummy_matrix.xlsx'
# grais_matrix_file = os.path.abspath(os.path.dirname(__file__)) + '/data/grais_matrix.xlsx'

matrix_size = 52
mongo_uri = os.environ.get('MONGOLAB_URI')

db = MongoClient(mongo_uri).heroku_k99m6wnb
city_collection = db.cities
transportation_collection = db.transportation_matrix
city_list = []


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

# Initiate a dictionary of matrix cities, with city name as key.
# def init_city_dictionary():
#     res_dict = {}
#     f = open(cities)
#     for line in f:
#         res_dict[line.replace("\n", "")] = []
#     f.close()
#     return res_dict


def init_city_dictionary():
    res_dict = {}
    for row in city_collection.find():
        res_dict[row['city']] = []
        city_list.append(row['city'])
    return res_dict


# Map all belonging airports to a city in the dictionary.
def map_airports_to_cities(res_dict, api_lookup):
    for airport in api_lookup['airports']:
        if airport['city'] in res_dict:
            if airport['code'] not in res_dict[airport['city']] and airport['code'] is not None:
                res_dict[airport['city']].append(airport['code'])
    return res_dict


def get_city_index(airport_code, airports):
    for key in airports:
        if airport_code in airports[key]:
            return city_list.index(key)
    return -1


# def write_airports_to_file(shortened):
#     result_file = open(chosen_airports, 'w')
#     wr = csv.writer(result_file, dialect='excel')
#     wr.writerow(shortened)


# Initiate the matrix with travel data between the cities.
def init_city_travel_matrix(airports, data):
    city_matrix = [[0] * matrix_size for x in range(matrix_size)]
    shortened = []
    for key in airports:
        for airport in airports[key]:
            shortened.append(airport)

    for row in data:
        if row[0] in shortened and row[1] in shortened:
            origin_index = get_city_index(row[0], airports)
            destination_index = get_city_index(row[1], airports)
            city_matrix[origin_index][destination_index] += int(row[2] / 365)
    return city_matrix


def get_transportation_matrix():
    result_matrix = []
    print("yolo")
    for document in transportation_collection.find():
        result_matrix.append(document['travel'])
        print("yolo")
    return result_matrix


# Reading the matrix from Rvachev & Longini's original paper.
# def create_dummy_matrix():
#     wkb = xlrd.open_workbook(dummy_matrix_file)
#     sheet = wkb.sheet_by_index(0)
#     _result = []
#
#     for row in range(1, sheet.nrows):
#         _row = []
#         for col in range(1, sheet.ncols):
#             _row.append(sheet.cell_value(row, col))
#         _result.append(_row)
#     return _result
#
#
# Reading the matrix from Grais et al's paper.
# def create_grais_matrix():
#     wkb = xlrd.open_workbook(grais_matrix_file)
#     sheet = wkb.sheet_by_index(0)
#     _result = []
#
#     for row in range(1, sheet.nrows):
#         _row = []
#         for col in range(1, sheet.ncols):
#             _row.append(sheet.cell_value(row, col))
#         _result.append(_row)
#     return _result

# # Returns the city matrix needed for prediction
# def calculate_travel_matrix():
#     airports = map_airports_to_cities(init_city_dictionary(), get_flight_data_local())
#     print(init_city_dictionary())
#     print(city_list)
#     data = read_air_travel_data(t100)
#     return init_city_travel_matrix(airports, data)
