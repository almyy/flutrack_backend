import configparser
import json
import os

import requests
import tweepy
from pymongo import MongoClient

geo_api_key = os.environ.get('GEOLOCATION_KEY')
mongo_uri = os.environ.get('MONGOLAB_URI')

if mongo_uri:
    client = MongoClient(mongo_uri)
    print('client connected')
    db = client.heroku_k99m6wnb
    cities = db.cities
    tweets = db.tweets
    test_tweets = db.test_tweets
    test_tweets2012 = db.test_tweets2012

else:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.flutrack
    cities = db.cities
    tweets = db.tweets
    test_tweets = db.test_tweets
    test_tweets2012 = db.test_tweets2012



def fetch_from_id():
    config = configparser.RawConfigParser()
    config.read_file((open('../config.ini')))

    consumer_key = config.get("Twitter", 'ConsumerKey')
    consumer_secret = config.get("Twitter", 'ConsumerSecret')
    access_token = config.get("Twitter", 'AccessToken')
    access_token_secret = config.get("Twitter", 'AccessTokenSecret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    id_data_file = 'data/AwarenessVsInfection2012TweetIDs.txt'
    with open(id_data_file, 'r') as fr:
        id_list = []
        for row in fr:
            row = row.split(sep='\t')
            id_list.append(row[0])
            if len(id_list) == 99:
                try:
                    tweet_results = api.statuses_lookup(id_list)
                    for tweet in tweet_results:
                        if tweet.user.location is not None:
                            tmp = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                                               {'key': os.environ.get('GEOLOCATION_KEY'), 'address': tweet.user.location,
                                                'result_type': 'locality'}).json()
                            if len(tmp['results']) > 0:
                                for component in tmp['results'][0]['address_components']:
                                    if 'locality' in component['types']:
                                        test_tweets2012.insert({
                                            'text': 'Swine Flu',
                                            'city': component['long_name']
                                        })
                    id_list = []
                except tweepy.TweepError as e:
                    if e.api_code == 144:
                        print("Couldn't find a tweet with id " + row[0])
                    else:
                        print(e.reason)

fetch_from_id()
