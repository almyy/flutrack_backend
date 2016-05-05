import calendar
import os
import time

from pymongo import MongoClient

from prediction import distribute_city_population as dcp

mongo_uri = os.environ.get('MONGOLAB_URI')

week = 604800
now = calendar.timegm(time.gmtime())

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
]

city_names = []
for city in dcp.city_list:
    city_names.append(city.name)

for doc in tweets.find():

    if doc['city'] in city_names:
        if int(doc['date']) < now - (week * 3):
            weeks[0][city_names.index(doc['city'])] += 1
        elif int(doc['date']) < (now - (week * 2)):
            weeks[1][city_names.index(doc['city'])] += 1
        elif int(doc['date']) < now - (week * 1):
            weeks[2][city_names.index(doc['city'])] += 1
        else:
            weeks[3][city_names.index(doc['city'])] += 1

for i in range(0, len(city_names)):
    print(city_names[i])
    for u in range(0, 3):
        if weeks[u][i] != 0:
            mu = (weeks[u + 1][i] / weeks[u][i]) ** (1 / 7)
            print(" Mu: \t" + str(mu))
    # print("Week1: " + str(str(weeks[0][i]) + " \tWeek2: " + str(weeks[1][i]) + "\tWeek 3: " +
    #                       str(weeks[2][i]) + " \tWeek4: " + str(weeks[3][i]) + "\tCity: " + str(city_names[i])))

# dt = datetime.fromordinal(1461606148)

print((1150 / 250) ** (1 / 7))
