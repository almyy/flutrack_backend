import configparser
import codecs

import tweepy


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

    id_data_file = 'data/AwarenessVsInfection2009TweetIDs.txt'
    status_dump_file = 'data/training_data_awareness_v2.csv'
    with open(id_data_file, 'r') as fr:
        with codecs.open(status_dump_file, 'w', encoding='utf-8') as fw:
            found_tweet = 0
            for row in fr:
                row = row.split(sep='\t')
                try:
                    tweet = api.get_status(row[0])
                    found_tweet += 1
                    fw.write('|' + row[1].strip('\n') + '|,|' + tweet.text + '|\n')
                    print("Found tweet no. " + str(found_tweet) + ": " + str(tweet.text.encode('utf-8')))
                except tweepy.TweepError as e:
                    if e.api_code == 144:
                        print("Couldn't find a tweet with id " + row[0])
                    else:
                        print(e.reason)


if __name__ == '__main__':
    fetch_from_id()
