import csv
import nltk
import codecs
from classifier_helper import ClassifierHelper

helper = ClassifierHelper("data")
feature_list = []


def extract_features(document):
    document_words = set(document)
    features = {}
    for word in feature_list:
        word = helper.replace_two_or_more(word)
        word = word.strip('\'"?,.')
        features['contains(%s)' % word] = (word in document_words)
    return features


stop_words = ['AT_USER', 'URL']
fp = open('stopwords.txt', 'r')
line = fp.readline()
while line:
    word = line.strip()
    stop_words.append(word)
    line = fp.readline()
fp.close()
tweets = []
inpTweets = csv.reader(codecs.open('data/RelatedVsNotRelated2012Tweets.csv', encoding='utf-8'), delimiter=',',
                       quotechar='|')
for row in inpTweets:
    sentiment = row[0]
    tweet = row[1]
    processedTweet = helper.process_tweet(tweet)
    feature_vector = helper.get_feature_vector(tweet, stop_words)
    feature_list.extend(feature_vector)
    tweets.append((feature_vector, sentiment))
feature_list = list(set(feature_list))
training_set = nltk.classify.util.apply_features(extract_features, tweets)
classifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3, labels=None,
                                                         gaussian_prior_sigma=0, max_iter=10)
test = 'completely healthy never been better'
processedTweet = helper.process_tweet(test)
sentiment = classifier.classify(helper.extract_features(helper.get_feature_vector(processedTweet, stop_words)))
print(classifier.show_most_informative_features(20))
print(sentiment)
