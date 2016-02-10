from sklearn.svm import libsvm as svm
import re, pickle, csv
from .classifier_helper import ClassifierHelper


# start class
class SVMClassifier:
    """ SVM Classifier """

    # variables
    # start __init__
    def __init__(self, data, training_data_file, classifier_dump_file, training_required=False):
        # Instantiate classifier helper
        self.helper = ClassifierHelper('data/feature_list.txt')

        self.lenTweets = len(data)
        self.origTweets = self.get_unique_data(data)
        self.tweets = self.get_processed_tweets(self.origTweets)

        self.results = {}
        self.neut_count = [0] * self.lenTweets
        self.pos_count = [0] * self.lenTweets
        self.neg_count = [0] * self.lenTweets
        self.trainingDataFile = training_data_file

        # self.html = html_helper.HTMLHelper()

        # call training model
        if training_required:
            self.classifier = self.get_svm_trained_classifier(training_data_file, classifier_dump_file)
        else:
            fp = open(classifier_dump_file, 'r')
            if fp:
                self.classifier = svm.svm_load_model(classifier_dump_file)
            else:
                self.classifier = self.get_svm_trained_classifier(training_data_file, classifier_dump_file)

    # end

    # start getUniqData
    @staticmethod
    def get_unique_data(data):
        unique_data = {}
        for i in range(len(data)):
            d = data[i]
            u = []
            for element in d:
                if element not in u:
                    u.append(element)
            # end inner loop
            unique_data[i] = u
        # end outer loop
        return unique_data

    # end

    # start getProcessedTweets
    def get_processed_tweets(self, data):
        tweets = {}
        for i in data:
            d = data[i]
            tw = []
            for t in d:
                tw.append(self.helper.process_tweet(t))
            tweets[i] = tw
            # end loop
        return tweets

    # end

    # start getNBTrainedClassifier
    def get_svm_trained_classifier(self, training_data_file, classifier_dump_file):
        # read all tweets and labels
        tweet_items = self.get_filtered_training_data(training_data_file)

        tweets = []
        for (words, sentiment) in tweet_items:
            words_filtered = [e.lower() for e in words.split() if (self.helper.is_ascii(e))]
            tweets.append((words_filtered, sentiment))

        results = self.helper.get_svm_feature_vector_and_labels(tweets)
        self.feature_vectors = results['feature_vector']
        self.labels = results['labels']
        # SVM Trainer
        problem = svm.svm_problem(self.labels, self.feature_vectors)
        # '-q' option suppress console output
        param = svm.svm_parameter('-q')
        param.kernel_type = svm.LINEAR
        # param.show()
        classifier = svm.svm_train(problem, param)
        svm.svm_save_model(classifier_dump_file, classifier)
        return classifier

    # end

    # start getFilteredTrainingData
    def get_filtered_training_data(self, training_data_file):
        fp = open(training_data_file, 'rb')
        min_count = self.get_min_count(training_data_file)
        # min_count = 40000
        neg_count, pos_count, neut_count = 0, 0, 0

        reader = csv.reader(fp, delimiter=',', quotechar='|', escapechar='\\')
        tweet_items = []
        count = 1
        for row in reader:
            # processed_tweet = self.helper.process_tweet(row[4])
            processed_tweet = self.helper.process_tweet(row[1])
            sentiment = row[0]

            if sentiment == '1':
                if pos_count == min_count:
                    continue
                pos_count += 1
            elif sentiment == '0':
                if neg_count == int(min_count):
                    continue
                neg_count += 1

            tweet_item = processed_tweet, sentiment
            tweet_items.append(tweet_item)
            count += 1
        # end loop
        return tweet_items

    # end

    # start getMinCount
    @staticmethod
    def get_min_count(training_data_file):
        fp = open(training_data_file, 'rb')
        reader = csv.reader(fp, delimiter=',', quotechar='"', escapechar='\\')
        neg_count, pos_count = 0, 0
        for row in reader:
            sentiment = row[0]
            if sentiment == '1':
                pos_count += 1
            elif sentiment == '0':
                neg_count += 1
        # end loop
        return min(neg_count, pos_count)

    # end

    # start classify
    def classify(self):
        for i in self.tweets:
            tw = self.tweets[i]
            test_tweets = []
            res = {}
            for words in tw:
                words_filtered = [e.lower() for e in words.split() if (self.helper.is_ascii(e))]
                test_tweets.append(words_filtered)
            test_feature_vector = self.helper.get_svm_feature_vector(test_tweets)
            p_labels, p_accs, p_vals = svm.svm_predict([0] * len(test_feature_vector), test_feature_vector,
                                                       self.classifier)
            count = 0
            for t in tw:
                label = p_labels[count]
                if label == 0:
                    label = '1'
                    self.pos_count[i] += 1
                else:
                    label = '0'
                    self.neg_count[i] += 1
                result = {'text': t, 'tweet': self.origTweets[i][count], 'label': label}
                res[count] = result
                count += 1
            # end inner loop
            self.results[i] = res
            # end outer loop

    # end

    # start writeOutput
    def write_output(self, filename, write_option='w'):
        fp = open(filename, write_option)
        for i in self.results:
            res = self.results[i]
            for j in res:
                item = res[j]
                text = item['text'].strip()
                label = item['label']
                write_str = text + " | " + label + "\n"
                fp.write(write_str)
                # end inner loop
                # end outer loop

    # end writeOutput

    # start accuracy
    def accuracy(self):
        tweets = self.get_filtered_training_data(self.trainingDataFile)
        test_tweets = []
        for (t, l) in tweets:
            words_filtered = [e.lower() for e in t.split() if (self.helper.is_ascii(e))]
            test_tweets.append(words_filtered)

        test_feature_vector = self.helper.get_svm_feature_vector(test_tweets)
        p_labels, p_accs, p_vals = svm.svm_predict([0] * len(test_feature_vector), test_feature_vector, self.classifier)
        count = 0
        total, correct, wrong = 0, 0, 0
        self.accuracy = 0.0
        for (t, l) in tweets:
            label = p_labels[count]
            if label == 0:
                label = 'positive'
            elif label == 1:
                label = 'negative'

            if label == l:
                correct += 1
            else:
                wrong += 1
            total += 1
            count += 1
        # end loop
        self.accuracy = (float(correct) / total) * 100
        print(
                'Total = ' + total + ', Correct = ' + correct + ', Wrong = ' + wrong + ', Accuracy = ' + str(
                        self.accuracy))
        # end


if __name__ == '__main__':
    # training_data_file = 'data/RelatedVsNotRelated2012Tweets.csv'
    # classifier_dump_file = 'data/classifierDump.pickle'
    # test_tweet = ['Send help. Im getting sick with the flu. High fever, cough, sore throat, sneezing.']
    # classifier = SVMClassifier(data=test_tweet, training_data_file=training_data_file,
    #                            classifier_dump_file=classifier_dump_file, training_required=True)
    helper = ClassifierHelper("data/feature_list.txt")
    # MaxEntClassifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3, \
    #                 encoding=None, labels=None, sparse=True, gaussian_prior_sigma=0, max_iter = 10)
    # testTweet = 'Congrats @ravikiranj, i heard you wrote a new tech post on sentiment analysis'
    # processedTestTweet = helper.processTweet(testTweet)
    # print MaxEntClassifier.classify(helperextract_features(getFeatureVector(processedTestTweet)))
