import calendar
import os
import time

from pymongo import MongoClient

from prediction import distribute_city_population as dcp

mongo_uri = os.environ.get('MONGOLAB_URI')

week = 604800
now = calendar.timegm(time.gmtime())
epidemic_constant = 0.3

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

for i in range(0, len(city_names)):
    last_mu = 0
    epidemic = True
    # print(city_names[i])
    for u in range(0, 3):
        if weeks[7 - u][i] != 0:
            mu = (weeks[7 - (u + 1)][i] / weeks[7 - u][i]) ** (1 / 7)
            if mu < last_mu:
                epidemic = False
            last_mu = mu
        else:
            epidemic = False
            # if city_names[i] == 'Chicago':
            #     print(last_mu)
        print(last_mu)
    if last_mu < epidemic_constant:
        epidemic = False
    if epidemic:
        print(" Mu: \t" + str(last_mu) + " City: " + city_names[i])

    # print("Week1: " + str(weeks[0][i]) + " \tWeek2: " + str(weeks[1][i]) + "\tWeek 3: " +
    #       str(weeks[2][i]) + " \tWeek4: " + str(weeks[3][i]) + "\tWeek 5: " + str(weeks[4][i]) +
    #       " \tWeek6: " + str(weeks[5][i]) + "\tWeek 7: " + str(weeks[6][i]) + " \tWeek7: "
    #       + str(weeks[7][i]) + " \tCity: " + str(city_names[i]))

print(count)

# dt = datetime.fromordinal(1461606148)
