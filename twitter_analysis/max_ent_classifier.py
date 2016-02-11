from classifier_helper import ClassifierHelper
import nltk
import codecs
import csv
import re
import pickle


class MaxEntClassifier:
    def extract_features(self, document):
        document_words = set(document)
        features = {}
        for word in self.feature_list:
            features['contains(%s)' % word] = (word in document_words)
        return features

    def get_feature_vector(self, tweet):
        words = tweet.split()
        features = []
        for word in words:
            word = word.strip('\'"?!,.')
            valid = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", word)
            if word in self.stop_words or valid is None:
                continue
            else:
                features.append(word.lower())
        for gram in nltk.bigrams(words):
            x, y = gram
            valid_x = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", x)
            valid_y = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", y)
            if x in self.stop_words or y in self.stop_words or valid_x is None or valid_y is None:
                continue
            else:
                features.append(gram[0] + " " + gram[1])
        return features

    def __init__(self, stop_words_file, training_data_file, needs_training, classifier_dump_file, feature_list_file,
                 classifier_type='nb'):
        self.helper = ClassifierHelper()
        self.stop_words = self.init_stop_words(stop_words_file)
        self.feature_list = []
        if needs_training:
            self.classifier = self.train_classifier(training_data_file, classifier_dump_file, feature_list_file,
                                                    classifier_type)
        else:
            with open(classifier_dump_file, 'rb') as f:
                self.classifier = pickle.load(f)
            with open(feature_list_file, 'r') as f:
                for token in f:
                    self.feature_list.append(token.strip())

    def classify(self, tweet):
        processed_tweet = self.helper.process_tweet(tweet)
        return self.classifier.classify(self.extract_features(self.get_feature_vector(processed_tweet)))

    def show_informative_features(self, n):
        return self.classifier.show_most_informative_features(n)

    def train_classifier(self, training_data_file, classifier_dump_file, feature_list_file, classifier_type):
        training_data = csv.reader(codecs.open(training_data_file, 'r', encoding='UTF-8'), delimiter=',', quotechar='|')
        tweets = []
        for row in training_data:
            sentiment = row[0]
            tweet = row[1]
            processed_tweet = self.helper.process_tweet(tweet)
            feature_vector = self.get_feature_vector(processed_tweet)
            self.feature_list.extend(feature_vector)
            tweets.append((feature_vector, sentiment))
        self.feature_list = list(set(self.feature_list))
        training_set = nltk.apply_features(self.extract_features, tweets)

        if classifier_type == 'nb':
            out_classifier = nltk.classify.NaiveBayesClassifier.train(training_set)
            with open(classifier_dump_file, 'wb') as f:
                pickle.dump(out_classifier, f)
        elif classifier_type == 'maxent':
            out_classifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3, labels=None,
                                                                         gaussian_prior_sigma=0, max_iter=10)
            with open(classifier_dump_file, 'wb') as f:
                pickle.dump(out_classifier, f)

        with open(feature_list_file, 'w') as f:
            for token in self.feature_list:
                f.write(token + '\n')
        return out_classifier

    def init_stop_words(self, stop_words_file):
        stop_words = ['AT_USER', 'URL']
        with open(stop_words_file, 'r') as file:
            for word in file:
                stop_words.append(word.strip())
        return stop_words


if __name__ == '__main__':
    classifier = MaxEntClassifier(stop_words_file='data/stopwords.txt', training_data_file='data/training_data.csv',
                                  needs_training=False, classifier_dump_file='data/maxent_classifier_dump.pickle',
                                  feature_list_file='data/feature_list.txt', classifier_type='maxent')
    negative_test_tweet = "throat flu spreading guide pregnant woman"
    positive_test_tweet = "feeling im getting flu spreading guide"

    print(classifier.classify(negative_test_tweet))
    print(classifier.classify(positive_test_tweet))
    print(classifier.show_informative_features(20))
