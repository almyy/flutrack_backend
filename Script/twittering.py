import tweepy


def filter_location(t):
    # if t.
    pass


class MyStreamListener(tweepy.StreamListener):

    f = open('sampleTweets.txt', 'w')

    def on_status(self, status):
        if hasattr(status, "retweeted_status"):
            print("retweet: " + str(status.text.encode('utf-8')))
        else:
            self.f.write(str(status.text)+'\n')
            print('Wrote line')

    def on_error(self, status_code):
        print(status_code)


def get_tweets():
    auth = tweepy.OAuthHandler('bQGknrESsRgoYlpHDVbza50RY', 'kloN6dBHcWMcgQQ7gCCsuw93YhyNtjxU1COsiO0vIyiJu4Pw7R')
    auth.set_access_token('3523682849-WeHuK2sGZueH1CWLPEWpzIi8swHtWo9ZQ3pDrsa',
                          'ZcWPBW0akqdFJVuB4v3VvVcXbozUsFbmQPbMRGxiv3QPr')
    api = tweepy.API(auth)

    sl = MyStreamListener()
    stream = tweepy.Stream(auth=auth, listener=sl)
    stream.filter(
            track=['fever', 'sick', 'cough', 'flu', 'influenza', 'runny nose', 'stuffed nose', 'sore throat',
                   'chills', 'shivering', 'headache', 'fatigued', 'vomiting'])



get_tweets()

