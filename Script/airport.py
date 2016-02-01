import csv
import requests
import json


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


def read_air_travel_data():
    with open('t100market.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        origin_list = sort_per_origin(reader)
    return sorted(origin_list, key=lambda k: k[2])


def parse_airport_api():
    params = {'user_key': 'eb6c3e8d6fb060a9a99f7b9fd061013c'}
    r = requests.get('https://airport.api.aero/airport', params=params)
    result = r.text.replace("callback(", "").replace(")", "")
    result_json = json.loads(result)
    with open('airports.json', 'w') as f:
        json.dump(result_json, f)
    return result_json


def parse_airport_api_locally():
    with open('airports.json') as data:
        result = json.load(data)
    return result


def init_city_list(filename):
    res_dict = {}
    f = open(filename)
    for line in f:
        res_dict[line.replace("\n", "")] = []
    return res_dict


def init_city_names(filename):
    res_list = []
    f = open(filename)
    for line in f:
        res_list.append(line.replace("\n", ""))
    res_list.sort()
    return res_list


def map_airports_to_cities(res_dict, api_lookup):
    for airport in api_lookup['airports']:
        if airport['city'] in res_dict:
            if airport['code'] not in res_dict[airport['city']] and airport['code'] is not None:
                res_dict[airport['city']].append(airport['code'])
    return res_dict


def get_passengers_between_cities(city1, city2):
    return city_matrix[city_list.index(city1)][city_list.index(city2)] + city_matrix[city_list.index(city2)][
        city_list.index(city1)]


def init_city_travel_matrix(airports, data):
    for row in data:
        for key in airports:
            if row[0] in airports[key]:
                for key2 in airports:
                    if row[1] in airports[key2] and key != key2:
                        city_matrix[city_list.index(key)][city_list.index(key2)] = row[2]

city_list = init_city_names('cities.txt')
city_matrix = [[0] * 52 for x in range(52)]


def __main__():
    airports = map_airports_to_cities(init_city_list('cities.txt'), parse_airport_api_locally())
    data = read_air_travel_data()
    init_city_travel_matrix(airports, data)

    print(get_passengers_between_cities('Los Angeles', 'Atlanta'))

if __name__ == '__main__':
    __main__()
