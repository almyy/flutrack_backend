import tweepy
import re
import codecs

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
    auth = tweepy.OAuthHandler('bQGknrESsRgoYlpHDVbza50RY', 'kloN6dBHcWMcgQQ7gCCsuw93YhyNtjxU1COsiO0vIyiJu4Pw7R')
    auth.set_access_token('3523682849-WeHuK2sGZueH1CWLPEWpzIi8swHtWo9ZQ3pDrsa',
                          'ZcWPBW0akqdFJVuB4v3VvVcXbozUsFbmQPbMRGxiv3QPr')
    stream_listener = FluStreamListener()
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    machine_learning_data = ['fever', 'sick', 'cough', 'flu', 'influenza', 'runny nose', 'stuffed nose', 'sore throat',
                             'chills', 'shivering', 'headache', 'fatigued', 'vomiting']
    data = ['fever sick', 'fever cough', 'flu sick', 'flu fever', 'runny nose', 'stuffed nose',
            'sick cough', 'fever cough', 'sore throat', 'headache fever', 'fatigued sick', 'fever tired',
            'vomiting flu', 'chills flu']
    try:
        stream.filter(track=data)
    except (KeyboardInterrupt, AttributeError) as e:
        print(e)


stream_tweets()
