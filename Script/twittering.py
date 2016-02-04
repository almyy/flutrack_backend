import codecs
import tweepy
import csv
import re
import nltk


class MachineLearning:
    stop_words = ['AT_USER', 'URL']
    classifier = None
    feature_list = []

    @staticmethod
    def process_tweet(tweet_text):
        tweet_text = tweet_text.lower()
        tweet_text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet_text)
        tweet_text = re.sub('@[^\s]+', 'AT_USER', tweet_text)
        tweet_text = re.sub('[\s]+', ' ', tweet_text)
        tweet_text = re.sub(r'#([^\s]+)', r'\1', tweet_text)
        tweet_text = tweet_text.strip('\'"')
        return tweet_text

    @staticmethod
    def replace_two_or_more(s):
        pattern = re.compile(r"(.)\1+", re.DOTALL)
        return pattern.sub(r"\1\1", s)

    def get_stop_word_list(self, stop_word_list_filename):
        fp = open(stop_word_list_filename, 'r')
        line = fp.readline()
        while line:
            word = line.strip()
            self.stop_words.append(word)
            line = fp.readline()
        fp.close()

    def get_feature_vector(self, tweet):
        featureVector = []
        words = tweet.split()
        for w in words:
            w = self.replace_two_or_more(w)
            w = w.strip('\'"?,.')
            val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
            if w in self.stop_words or val is None:
                continue
            else:
                featureVector.append(w.lower())
        return featureVector

    def extract_features(self, tweet):
        tweet_words = set(tweet)
        features = {}
        for word in self.feature_list:
            features['contains(%s)' % word] = (word in tweet_words)
        return features

    def classify(self, tweet):
        return self.classifier.classify(self.extract_features(self.get_feature_vector(tweet)))

    def __init__(self):
        # Read the tweets one by one and process it
        inp_tweets = csv.reader(open('sampleTweets.csv', 'r', encoding='utf-8'), delimiter=',', quotechar='|')
        tweets = []
        for row in inp_tweets:
            if row[0] == '+':
                sentiment = 'positive'
                print(row[1].encode('utf-8'))
            else:
                sentiment = 'negative'
            tweet = row[1]
            processed_tweet = self.process_tweet(tweet)
            feature_vector = self.get_feature_vector(processed_tweet)
            tweets.append((feature_vector, sentiment))
            self.feature_list.extend(feature_vector)

        self.feature_list = list(set(self.feature_list))
        training_set = nltk.classify.util.apply_features(self.extract_features, tweets)
        self.classifier = nltk.NaiveBayesClassifier.train(training_set)


        # test_tweet = 'fever headache'
        # processedTweet = process_tweet(test_tweet)
        # print(NBClassifier.classify(extract_features(get_feature_vector(processedTweet, stop_words))))


def filter_tweet(status):
    if hasattr(status, 'retweeted_status'):
        return False
    else:
        return True


# def store_status_ml(status):
#     f.write(",|" + status.text + '|\n')


class FluStreamListener(tweepy.StreamListener):
    status_count_original = 0
    status_count_retweet = 0
    previous_status_text = ""
    status_history = []
    learner = MachineLearning()

    def on_status(self, status):
        if filter_tweet(status):
            self.status_count_original += 1
            # self.previous_status_text = re.sub(r"https?:\/\/(t\.co\/[a-zA-z]+)", "", status.text)
            # store_status_ml(status)

            test_tweet = status.text
            processed_tweet = self.learner.process_tweet(test_tweet)
            print(str(processed_tweet.encode('utf-8')) + ", " + self.learner.classify(processed_tweet))
        else:
            self.status_count_retweet += 1
            # print("Retweet count: " + str(self.status_count_retweet) + str(status.text.encode("utf-8")))

    def on_error(self, status_code):
        print(str(status_code))

    # def store_status(self, status):
    #     self.status_history.append(
    #             str(self.status_count_original) + " User: " + str(status.user.screen_name) +
    #             " Text: " + str(status.text.encode("utf-8")))
    #
    # def save_history(self):
    #     with codecs.open("status_dump.csv", "w", encoding='utf-8') as text_file:
    #         for status in self.status_history:
    #             text_file.write("\n" + str(status))


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


if __name__ == '__main__':
    stream_tweets()
