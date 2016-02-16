import codecs
import tweepy
import re
import configparser
from max_ent_classifier import MaxEntClassifier
from classifier_helper import ClassifierHelper

f = codecs.open('sampleTweets.csv', 'w', encoding='utf-8')
classifier = MaxEntClassifier(stop_words_file='data/stopwords.txt', related_training_data_file='data/training_data.csv', awareness_training_data_file='data/training_data_awareness_v2.csv',
                              needs_training=False, related_classifier_dump_file='data/classifier_dump.pickle',
                              awareness_classifier_dump_file='data/awareness_nb_classifier_dump.pickle',
                              feature_list_file='data/feature_list.txt')
helper = ClassifierHelper()


def filter_tweet(status):
    if hasattr(status, 'retweeted_status'):
        return False
    else:
        return True


def store_status_ml(status):
    f.write(",|" + status.text + '|\n')


class FluStreamListener(tweepy.StreamListener):
    status_count_original = 0
    status_count_retweet = 0
    previous_status_text = ""
    status_history = []

    def on_status(self, status):
        print("awareness: " + str(classifier.classify_awareness(status.text)) + ", related: " + str(
            classifier.classify_related(status.text)) + '\t' + str(helper.process_tweet(status.text).encode('utf-8')))

    def on_error(self, status_code):
        print(str(status_code))

    def store_status(self, status):
        self.status_history.append(
                str(self.status_count_original) + " User: " + str(status.user.screen_name) +
                " Text: " + str(status.text.encode("utf-8")))

    def save_history(self):
        with codecs.open("status_dump.csv", "w", encoding='utf-8') as text_file:
            for status in self.status_history:
                text_file.write("\n" + str(status))


def stream_tweets():
    config = configparser.RawConfigParser()
    config.read_file((open('../config.ini')))

    consumer_key = config.get("Twitter", 'ConsumerKey')
    consumer_secret = config.get("Twitter", 'ConsumerSecret')
    access_token = config.get("Twitter", 'AccessToken')
    access_token_secret = config.get("Twitter", 'AccessTokenSecret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream_listener = FluStreamListener()
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    machine_learning_data = ['fever', 'sick', 'cough', 'flu', 'influenza', 'runny nose', 'stuffed nose', 'sore throat',
                             'chills', 'shivering', 'headache', 'fatigued', 'vomiting']
    data = ['fever sick', 'fever cough', 'flu sick', 'flu fever', 'runny nose', 'stuffed nose',
            'sick cough', 'fever cough', 'sore throat', 'headache fever', 'fatigued sick', 'fever tired',
            'vomiting flu', 'chills flu']

    stream.filter(track=machine_learning_data)


if __name__ == '__main__':
    stream_tweets()
