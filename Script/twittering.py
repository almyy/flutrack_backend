import tweepy
import re
import json


def filter_location(t):
    # if t.
    pass


def get_tweets():
    auth = tweepy.OAuthHandler('eGH2C9cpRIvYRbYudAJN7Vf2c', 'vt2D0TXrEsNSvBDl5BERGIUyCgSsFjX3hIj1jAVbCOKInpKQAi')
    auth.set_access_token('3523253362-YmQDEpGx4YeAMhny1XDiS9ycnBJz6pRtWL2rKOI',
                          'GEHu7VTG3oFap1lPFBPLpTED5Hz8APB7oreGdwoLIwEZ6')
    api = tweepy.API(auth)
    search_query = "flu OR cough OR sore OR throat OR headache"
    cursor = tweepy.Cursor(api.search, q=search_query)
    n = 0
    for t in cursor.items(10000):
        n += 1
        print(str(n) + " " + str(t.text.encode("utf-8")))


def filter_tweet(status):
    if hasattr(status, 'retweeted_status'):
        return False
    else:
        return True


class FluStreamListener(tweepy.StreamListener):
    status_count_original = 0
    status_count_retweet = 0
    previous_status_text = ""
    status_history = []

    def on_status(self, status):
        if filter_tweet(status):
            self.status_count_original += 1
            print(str(self.status_count_original) + " " + str(status.text.encode("utf-8")))
            # if self.previous_status_text == re.sub(r"https?:\/\/(t\.co\/[a-zA-z]+)", "URL", status.text):
            self.previous_status_text = re.sub(r"https?:\/\/(t\.co\/[a-zA-z]+)", "URL", status.text)
            self.store_status(status)
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
        with open("status_dump.txt", "w") as text_file:
            for status in self.status_history:
                text_file.write("\n" + str(status))


def stream_tweets():
    auth = tweepy.OAuthHandler('eGH2C9cpRIvYRbYudAJN7Vf2c', 'vt2D0TXrEsNSvBDl5BERGIUyCgSsFjX3hIj1jAVbCOKInpKQAi')
    auth.set_access_token('3523253362-YmQDEpGx4YeAMhny1XDiS9ycnBJz6pRtWL2rKOI',
                          'GEHu7VTG3oFap1lPFBPLpTED5Hz8APB7oreGdwoLIwEZ6')
    stream_listener = FluStreamListener()
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    machine_learning_data = ['fever', 'sick', 'cough', 'flu', 'influenza', 'runny nose', 'stuffed nose', 'sore throat',
                             'chills', 'shivering', 'headache', 'fatigued', 'vomiting']
    data = ['fever sick', 'fever cough', 'flu sick', 'flu fever', 'runny nose', 'stuffed nose',
            'sick cough', 'fever cough', 'sore throat', 'headache fever', 'fatigued sick', 'fever tired',
            'vomiting flu', 'chills flu']
    try:
        stream.filter(track=data)
    except KeyboardInterrupt:
        stream_listener.save_history()


# get_tweets()
stream_tweets()
