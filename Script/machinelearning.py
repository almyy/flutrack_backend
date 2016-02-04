import csv
import re
import nltk


class MachineLearning:
    stop_words = ['AT_USER', 'URL']
    NBClassifier = None
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
            if w in self.stopWords or val is None:
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
        self.classifier.classify(self.extract_features(self.get_feature_vector(tweet)))

    def __init__(self):
        # Read the tweets one by one and process it
        inp_tweets = csv.reader(open('sampleTweets.csv', 'r', encoding='utf-8'), delimiter=',', quotechar='|')
        tweets = []
        for row in inp_tweets:
            if row[0] == '+':
                sentiment = 'positive'
                # print(row[1].encode('utf-8'))
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
