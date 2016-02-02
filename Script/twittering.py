import tweepy


def filter_location(t):
    # if t.
    pass


class FluStreamListener(tweepy.StreamListener):
    status_count = 0

    def on_status(self, status):
        self.status_count += 1
        self.filter(status)
        print(str(self.status_count) + " " + str(status.text.encode("utf-8")))

    def filter(self, status):
        if status.retweeted:
            print("Retweet")
        else:
            print("Retweet")


def stream_tweets():
    auth = tweepy.OAuthHandler('eGH2C9cpRIvYRbYudAJN7Vf2c', 'vt2D0TXrEsNSvBDl5BERGIUyCgSsFjX3hIj1jAVbCOKInpKQAi')
    auth.set_access_token('3523253362-YmQDEpGx4YeAMhny1XDiS9ycnBJz6pRtWL2rKOI', 'GEHu7VTG3oFap1lPFBPLpTED5Hz8APB7oreGdwoLIwEZ6')
    stream_listener = FluStreamListener()
    stream = tweepy.Stream(auth=auth, listener=stream_listener)
    stream.filter(track=['flu', 'cough', 'headache'])

# get_tweets()
stream_tweets()

