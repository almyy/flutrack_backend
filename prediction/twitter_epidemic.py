import calendar
import os
import time

from pymongo import MongoClient

from prediction import distribute_city_population as dcp

mongo_uri = os.environ.get('MONGOLAB_URI')

week = 604800
now = calendar.timegm(time.gmtime())
epidemic_constant = 1.2

if mongo_uri:
    client = MongoClient(mongo_uri)
    print('Connected to MongoDB')
    db = client.heroku_k99m6wnb
    tweets = db.tweets
    test_tweets = db.test_tweets2012
else:
    tweets = 0
    test_tweets = 0
    print('Couldnt connect to DB')

dcp.initiate_validation_results(0)

weeks = [
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
    [0] * len(dcp.city_list),
]

cities_epidemic = []



city_names = []
for city in dcp.city_list:
    city_names.append(city.name)

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

        # if int(doc['date']) < now - (week * 3):
        #     weeks[0][city_names.index(doc['city'])] += 1
        # elif int(doc['date']) < (now - (week * 2)):
        #     weeks[1][city_names.index(doc['city'])] += 1
        # elif int(doc['date']) < now - (week * 1):
        #     weeks[2][city_names.index(doc['city'])] += 1
        # else:
        #     weeks[3][city_names.index(doc['city'])] += 1


def is_epidemic(city):
    last_mu = 0
    epidemic = True
    for u in range(0, 3):
        if weeks[7 - u][city] != 0:
            mu = (weeks[7 - (u + 1)][city] / weeks[7 - u][city]) ** (1 / 7)
            if mu < last_mu:
                epidemic = False
            last_mu = mu
        else:
            epidemic = False
    if last_mu < epidemic_constant:
        epidemic = False
    return epidemic


def is_increasing(city):
    for i in range(0, 2):
        if weeks[7-i][city] < weeks[7-(i+1)][city]:
            return False
        if weeks[7-(i+1)][city] == 0:
            return False
    # print("Increasing: " + city)
    return True


db_cities = list(db.cities.find())


def lookup_coords(city):
    for db_city in db_cities:
        if city == db_city['city']:
            return db_city['location']


# Ultimate quickfix. Shouldn't have to do this!
def invert_weeks(in_weeks):
    out_cities = []
    for i in range(0, len(in_weeks[0])):
        out_city_list = []
        for in_week in in_weeks:
            out_city_list.append(in_week[i])
        out_cities.append(out_city_list)
    return out_cities


def get_tweets_per_week():
    returned_cities = []
    inverted_weeks = invert_weeks(weeks)
    city_index = 0
    for i in inverted_weeks:
        returned_cities.append(
                {'location': lookup_coords(city_names[city_index]), 'weeks': i, 'city': city_names[city_index],
                 'epidemic': is_epidemic(city_index), 'increasing': is_increasing(city_index)})
        city_index += 1
    print(returned_cities)
    return returned_cities


print(count)

# dt = datetime.fromordinal(1461606148)
