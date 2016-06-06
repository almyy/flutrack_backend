import calendar
import os
import time

from pymongo import MongoClient

mongo_uri = os.environ.get('MONGOLAB_URI')

week = 604800
now = calendar.timegm(time.gmtime())
epidemic_constant = 0.9


client = MongoClient(mongo_uri)
print('Connected to MongoDB')
db = client.heroku_k99m6wnb
tweets = db.tweets
test_tweets = db.test_tweets2012
db_cities = list(db.cities.find())

city_length = len(db_cities)
weeks = [
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
    [0] * city_length,
]

cities_epidemic = []
city_names = []
for city in db_cities:
    city_names.append(city['city'])

count = 0
for doc in tweets.find():
    if doc['city'] in city_names:
        count += 1
        c_week = -1
        for i in range(0, 8):
            if int(doc['date']) < (now - (week * (7 - i))):
                c_week = 7 - i
                break
        weeks[c_week][city_names.index(doc['city'])] += 1

count = 0
for doc in tweets.find():
    if doc['city'] in city_names:
        count += 1
        c_week = -1
        for i in range(0, 8):
            if int(doc['date']) < (now - (week * (7 - i))):
                c_week = 7 - i
                break
        weeks[c_week][city_names.index(doc['city'])] += 1


def is_epidemic(city):
    last_mu = 0
    epidemic = True
    for u in range(0, 3):
        if weeks[7 - u][city] != 0:
            mu = (weeks[7 - (u + 1)][city] / weeks[7 - u][city]) ** (1 / 7)
            if mu < last_mu or mu < epidemic_constant:
                epidemic = False
            last_mu = mu
        else:
            epidemic = False
    if last_mu < epidemic_constant:
        epidemic = False
    return epidemic


def is_increasing(city):
    for i in range(0, 2):
        if weeks[7 - i][city] < weeks[7 - (i + 1)][city]:
            return False
        if weeks[7 - (i + 1)][city] == 0:
            return False
    return True


def lookup_coords(city):
    for db_city in db_cities:
        if city == db_city['city']:
            return db_city['location']


def invert_weeks(in_weeks):
    out_cities = []
    for i in range(0, len(in_weeks[0])):
        out_city_list = []
        for in_week in in_weeks:
            out_city_list.append(in_week[i])
        out_cities.append(out_city_list)
    return out_cities


def update_forecast():
    for index in range(0, len(invert_weeks(weeks))):
        print(str(is_epidemic(index)) + ", " + str(index))
        if is_epidemic(index):
            return index
    return -1


def get_tweets_per_week():
    returned_cities = []
    inverted_weeks = invert_weeks(weeks)
    city_index = 0
    epidemic_city = update_forecast()
    for i in inverted_weeks:
        if epidemic_city >= 0:
            if epidemic_city == city_index:
                returned_cities.append(
                        {'location': lookup_coords(city_names[city_index]), 'weeks': i, 'city': city_names[city_index],
                         'epidemic': True, 'increasing': is_increasing(city_index)})
            else:
                returned_cities.append(
                        {'location': lookup_coords(city_names[city_index]), 'weeks': i, 'city': city_names[city_index],
                         'epidemic': False, 'increasing': is_increasing(city_index)})
        else:
            returned_cities.append(
                    {'location': lookup_coords(city_names[city_index]), 'weeks': i, 'city': city_names[city_index],
                     'epidemic': False, 'increasing': is_increasing(city_index)})
        city_index += 1
    return returned_cities
