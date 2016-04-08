import csv
import requests
import json
import xlrd
import os

airport_file = os.path.abspath(os.path.dirname(__file__)) + '/data/airports.json'
cities = os.path.abspath(os.path.dirname(__file__)) + '/data/cities.txt'
t100 = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market.csv'
chosen_airports = os.path.abspath(os.path.dirname(__file__)) + '/data/chosen_airports.csv'
dummy_matrix_file = os.path.abspath(os.path.dirname(__file__)) + '/data/dummy_matrix.xlsx'
city_matrix = [[0] * 52 for x in range(52)]
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
def read_air_travel_data():
    with open(t100) as csv_file:
        reader = csv.DictReader(csv_file)
        origin_list = sort_per_origin(reader)
    return sorted(origin_list, key=lambda k: k[2])


# Query aiport.aero from flight data based on airports.
def get_flight_data():
    params = {'user_key': 'eb6c3e8d6fb060a9a99f7b9fd061013c'}
    r = requests.get('https://airport.api.aero/airport', params=params)
    result = r.text.replace("callback(", "").replace(")", "")
    result_json = json.loads(result)
    with open(airport_file, 'w') as f:
        json.dump(result_json, f)
    return result_json


# Get an instance of the queried flight data stored locally.
def get_flight_data_local():
    with open(airport_file) as data:
        result = json.load(data)
    return result


# Initiate a dictionary of matrix cities, with city name as key.
def init_city_dictionary():
    res_dict = {}
    f = open(cities)
    for line in f:
        res_dict[line.replace("\n", "")] = []
    f.close()
    return res_dict


# Initiate an alphabetical list of the cities used in the matrix.
def init_city_names():
    f = open(cities)
    for line in f:
        city_list.append(line.replace("\n", ""))
    f.close()


# Map all belonging airports to a city in the dictionary.
def map_airports_to_cities(res_dict, api_lookup):
    for airport in api_lookup['airports']:
        if airport['city'] in res_dict:
            if airport['code'] not in res_dict[airport['city']] and airport['code'] is not None:
                res_dict[airport['city']].append(airport['code'])
    return res_dict


# Return the number of passengers that has travelled between two cities.
def get_passengers_between_cities(city1, city2):
    return city_matrix[city_list.index(city1)][city_list.index(city2)] + city_matrix[city_list.index(city2)][
        city_list.index(city1)]


def get_city_index(airport_code, airports):
    for key in airports:
        if airport_code in airports[key]:
            return city_list.index(key)
    return 0


def write_airports_to_file(shortened):
    # TODO implement this method for faster initialization of airport codes.
    result_file = open(chosen_airports, 'w')
    wr = csv.writer(result_file, dialect='excel')
    wr.writerow(shortened)


# Initiate the matrix with travel data between the cities.
def init_city_travel_matrix(airports, data):
    # TODO Implement the matrix to have travel data on a daily number of travelers between cities.
    shortened = []
    for key in airports:
        for airport in airports[key]:
            shortened.append(airport)

    for row in data:
        if row[0] in shortened and row[1] in shortened:
            origin_index = get_city_index(row[0], airports)
            destination_index = get_city_index(row[1], airports)
            city_matrix[origin_index][destination_index] += row[2]


def create_dummy_matrix():
    wkb = xlrd.open_workbook(dummy_matrix_file)
    sheet = wkb.sheet_by_index(0)
    _result = []

    for row in range(1, sheet.nrows):
        _row = []
        for col in range(1, sheet.ncols):
            _row.append(sheet.cell_value(row, col))
        _result.append(_row)
    return _result


init_city_names()
airports = map_airports_to_cities(init_city_dictionary(), get_flight_data_local())
data = read_air_travel_data()
init_city_travel_matrix(airports, data)
