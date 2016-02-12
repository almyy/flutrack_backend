import codecs
import tweepy
import re
import configparser

f = codecs.open('sampleTweets.csv', 'w', encoding='utf-8')


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
        if filter_tweet(status):
            self.status_count_original += 1
            print(str(self.status_count_original) + " " + str(status.text.encode("utf-8")))
            # self.previous_status_text = re.sub(r"https?:\/\/(t\.co\/[a-zA-z]+)", "", status.text)
            store_status_ml(status)
        else:
            self.status_count_retweet += 1
            # print("Retweet count: " + str(self.status_count_retweet) + str(status.text.encode("utf-8")))

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
    try:
        stream.filter(track=machine_learning_data)
    except KeyboardInterrupt:
        stream_listener.save_history()
        stream.filter(track=data)
    except AttributeError as e:
        print(e)


# get_tweets()
stream_tweets()
