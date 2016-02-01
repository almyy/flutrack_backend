import tweepy


def filter_location(t):
    # if t.
    pass

def get_tweets():
    auth = tweepy.OAuthHandler('bQGknrESsRgoYlpHDVbza50RY', 'kloN6dBHcWMcgQQ7gCCsuw93YhyNtjxU1COsiO0vIyiJu4Pw7R')
    auth.set_access_token('3523682849-WeHuK2sGZueH1CWLPEWpzIi8swHtWo9ZQ3pDrsa', 'ZcWPBW0akqdFJVuB4v3VvVcXbozUsFbmQPbMRGxiv3QPr')
    api = tweepy.API(auth)
    search_query = "coughing, fever"
    cursor = tweepy.Cursor(api.search, q=search_query)
    for t in cursor.items():

        print()

get_tweets()
