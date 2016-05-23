import csv
import requests
import json
import os

import xlrd
from pymongo import MongoClient
from bson.json_util import dumps, loads

t100market = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market.csv'
# t100market2000 = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market2000.csv'

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
    s = [[str(e) for e in row] for row in result_matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
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

