import os

from pymongo import MongoClient
from prediction import distribute_city_population as dcp

mongo_uri = os.environ.get('MONGOLAB_URI')

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
tweet_list = [0] * len(dcp.city_list)
city_names = []
for city in dcp.city_list:
    city_names.append(city.name)

for doc in test_tweets.find():
    if doc['city'] in city_names:
        tweet_list[city_names.index(doc['city'])] += 1

for i in range(0, len(city_names)):
    print(str(city_names[i]) + ": \t" + str(tweet_list[i]))

