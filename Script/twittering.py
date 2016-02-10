import codecs
import tweepy
import csv
import re
from time import sleep
from sklearn.svm import libsvm


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

    def get_svm_feature_vector_and_labels(self, tweets):
        sorted_features = sorted(self.feature_list)
        map = {}
        feature_vector = []
        labels = []
        for t in tweets:
            label = 0
            map = {}
            for w in sorted_features:
                map[w] = 0
            tweet_words = t[1]
            tweet_opinion = t[0]
            for word in tweet_words:
                word = self.replace_two_or_more(word)
                word = word.strip('\'"?,.')
                if word in map:
                    map[word] = 1
            values = map.values()
            feature_vector.append(values)
            if tweet_opinion == 'positive':
                label = 0
            else:
                label = 1
            labels.append(label)
        return {'feature_vector': feature_vector, 'labels': labels}

    def classify(self, tweet):
        return self.classifier.classify(self.extract_features(self.get_feature_vector(tweet)))

    def train_svm_classifier(self, tweets):
        result = self.get_svm_feature_vector_and_labels(tweets)
        problem = libsvm.svm_problem(result['labels'], result['feature_vector'])
        #'-q' option suppress console output
        param = libsvm.svm_parameter('-q')
        param.kernel_type = libsvm.LINEAR
        self.classifier = libsvm.svm_train(problem, param)
        libsvm.svm_save_model(libsvm.classifierDumpFile, self.classifier)

    def __init__(self):
        # Read the tweets one by one and process it
        inp_tweets = csv.reader(open('data/RelatedVsNotRelated2012Tweets.csv', 'r', encoding='utf-8'),
                                delimiter=',', quotechar='|')
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
        # training_set = nltk.classify.util.apply_features(self.extract_features, tweets)
        # self.classifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3,
        #                                                               labels=None,
        #                                                               gaussian_prior_sigma=0, max_iter=10)
        # self.classifier.show_most_informative_features(n=20)
        #
        # test_tweet = 'fever headache flu. Body hurts. Fuck!'
        # processed_tweet = self.process_tweet(test_tweet)
        # print(self.classifier.classify(self.extract_features(self.get_feature_vector(processed_tweet))))
        self.train_svm_classifier(tweets)
        # test_feature_vector =


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
    # learner = MachineLearning()

    # processed_tweet = learner.process_tweet('yummy vitamins. Gief smoothie. Possibly pounding body catch. Care')

    # print(str(processed_tweet.encode('utf-8')) + ", " + learner.classify(processed_tweet))

    def on_status(self, status):
        if filter_tweet(status):
            self.status_count_original += 1
            # self.previous_status_text = re.sub(r"https?:\/\/(t\.co\/[a-zA-z]+)", "", status.text)
            # store_status_ml(status)

            test_tweet = status.text
            processed_tweet = self.learner.process_tweet(test_tweet)
            print(self.learner.classify(processed_tweet) + ", " + str(processed_tweet.encode('utf-8')))
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


def replace_ids_with_tweets():
    auth = tweepy.OAuthHandler('bQGknrESsRgoYlpHDVbza50RY', 'kloN6dBHcWMcgQQ7gCCsuw93YhyNtjxU1COsiO0vIyiJu4Pw7R')
    auth.set_access_token('3523682849-WeHuK2sGZueH1CWLPEWpzIi8swHtWo9ZQ3pDrsa',
                          'ZcWPBW0akqdFJVuB4v3VvVcXbozUsFbmQPbMRGxiv3QPr')
    api = tweepy.API(auth)
    failed_tweet_counter = 0
    request_counter = 0
    with codecs.open("data/RelatedVsNotRelated2012TweetIDs.txt", "r") as read_file:
        with codecs.open("data/RelatedVsNotRelated2012Tweets.csv", "w", encoding='UTF-8') as write_file:
            for line in read_file:
                values = line.split('\t')
                id = values[0]
                sentiment = values[1].rstrip()
                try:
                    request_counter += 1
                    status = api.get_status(id=id)
                except tweepy.error.TweepError as e:
                    # if e.status
                    # print("Couldn't find tweet with id " + id)
                    if e.response.status_code == 429:
                        print("Exceeded rate limit. Sleeping for 15 minutes")
                        sleep(901)
                        try:
                            status = api.get_status(id=id)
                        except tweepy.error.TweepError:
                            failed_tweet_counter += 1
                            print("Couldnt find tweet with id " + id)
                            continue
                    print("Couldnt find tweet with id " + id)
                    failed_tweet_counter += 1
                    continue
                write_file.write('|' + sentiment + '|,|' + status.text + '|\n')
                print("Wrote tweet no. " + str(request_counter - failed_tweet_counter))
            write_file.close()
        read_file.close()


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
        stream.filter(track=machine_learning_data)
    except (KeyboardInterrupt, AttributeError) as e:
        print(e)


if __name__ == '__main__':
    # stream_tweets()
    print("")
