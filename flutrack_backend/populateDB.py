import csv

import xlrd
from pymongo import MongoClient
import requests
import os
import json

geo_api_key = os.environ.get('GEOLOCATION_KEY')
mongo_uri = os.environ.get('MONGOLAB_URI')

airport_file = os.path.abspath(os.path.dirname(__file__)) + '/data/airports.json'
city_file = os.path.abspath(os.path.dirname(__file__)) + '/data/cities.csv'
city_file_test = os.path.abspath(os.path.dirname(__file__)) + '/data/cities_test.csv'
grais_city_file = os.path.abspath((os.path.dirname(__file__))) + '/data/grais_population.csv'
t100market = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market.csv'
t100market2000 = os.path.abspath(os.path.dirname(__file__)) + '/data/t100market2000.csv'
dummy_matrix_file = os.path.abspath(os.path.dirname(__file__)) + '/data/dummy_matrix.xlsx'


# Collect tweets from the last 60 days from the flutrack API.
def populate_tweets_from_flutrack_api():
    r = requests.get("http://api.flutrack.org/?time=60")
    data = json.loads(r.text)
    populate_tweets_from_json(data)


# Check if the the tweets from flutrack have a location in one of the cities we are tracking.
def populate_tweets_from_json(data):
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


# Populate the database with the cities we want to track.
def populate_cities_from_text():
    result = []
    with open(city_file) as f:
        index = 0
        for row in f:
            row = row.split(sep=',')
            json_res = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                    {'key': os.environ.get('GEOLOCATION_KEY'), 'address': row[0]}).json()
            print(row[0])
            result.append({
                'index': index,
                'zone': row[2].strip('\n'),
                'city': row[0],
                'location': json_res['results'][0]['geometry']['location'] if json_res['results'] is not None else 'Unknown',
                'bounding_box': json_res['results'][0]['geometry']['bounds'],
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


def populate_airports_from_json():
    with open(airport_file) as data:
        result = json.load(data)
    airports.insert(result)
    return result


def populate_transportation_matrix_from_csv(airport_data, data):
    matrix_size = db.cities.count()
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
    db.transportation_matrix.insert(matrix_document)


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

    for row in result:
        if row[0] == 'LAX' or row[0] == 'LGA' or row[0] == 'JFK':
            if row[1] == 'LAX' or row[1] == 'LGA' or row[1] == 'JFK':
                print(row)
    result.pop(0)
    return result


# Initiate and sort the t100market database.
def read_air_travel_data():
    with open(t100market) as csv_file:
        reader = csv.DictReader(csv_file)
        origin_list = sort_per_origin(reader)
    return sorted(origin_list, key=lambda k: k[2])


def get_city_index(airport_code, airports):
    for key in airports:
        if airport_code in airports[key]:
            return city_list.index(key)
    return -1


def map_airports_to_cities(api_lookup):
    for airport in api_lookup['airports']:
        if airport['city'] in res_dict:
            if airport['code'] not in res_dict[airport['city']] and airport['code'] is not None:
                res_dict[airport['city']].append(airport['code'])
    return res_dict


# Reading the matrix from Rvachev & Longini's original paper.
def create_dummy_matrix():
    wkb = xlrd.open_workbook(dummy_matrix_file)
    sheet = wkb.sheet_by_index(0)
    _result = []

    for row in range(1, sheet.nrows):
        _row = []
        for col in range(1, sheet.ncols):
            _row.append(sheet.cell_value(row, col))
        _result.append(_row)
    matrix_document = []
    for row in _result:
        matrix_document.append({
            'travel': row
        })
    db.transportation_matrix.insert(matrix_document)


def populate_collections():
    db.tweets.drop()
    db.transportation_matrix.drop()
    db.airports.drop()
    populate_tweets_from_flutrack_api()
    airp = populate_airports_from_json()
    populate_transportation_matrix_from_csv(map_airports_to_cities(airp), read_air_travel_data())
    # create_dummy_matrix()


if mongo_uri:
    db = MongoClient(mongo_uri).heroku_k99m6wnb
    cities = db.cities
    tweets = db.tweets
    airports = db.airports
    db.cities.drop()
    populate_cities_from_text()
    cursor = cities.find()
    city_bounds = []
    city_list = []
    res_dict = {}
    for document in cursor:
        city_bounds.append({'box': document['bounding_box'], 'city': document['city']})
        city_list.append(document['city'])
        res_dict[document['city']] = []
else:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.flutrack
    cities = db.cities
    tweets = db.tweets
    airports = db.airports

populate_collections()
