import csv
import re
import nltk


def process_tweet(tweet_text):
    tweet_text = tweet_text.lower()
    tweet_text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet_text)
    tweet_text = re.sub('@[^\s]+', 'AT_USER', tweet_text)
    tweet_text = re.sub('[\s]+', ' ', tweet_text)
    tweet_text = re.sub(r'#([^\s]+)', r'\1', tweet_text)
    tweet_text = tweet_text.strip('\'"')
    return tweet_text


stop_words = ['AT_USER', 'URL']


def replace_two_or_more(s):
    pattern = re.compile(r"(.)\1+", re.DOTALL)
    return pattern.sub(r"\1\1", s)


def get_stop_word_list(stop_word_list_filename):
    fp = open(stop_word_list_filename, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stop_words.append(word)
        line = fp.readline()
    fp.close()
    return stop_words


def get_feature_vector(tweet, stopWords):
    featureVector = []
    words = tweet.split()
    for w in words:
        w = replace_two_or_more(w)
        w = w.strip('\'"?,.')
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
        if w in stopWords or val is None:
            continue
        else:
            featureVector.append(w.lower())
    return featureVector


def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features


# Read the tweets one by one and process it
inpTweets = csv.reader(open('sampleTweets1.csv', 'r'), delimiter=',', quotechar='|')
tweets = []
featureList = []
for row in inpTweets:
    if row[0] == '+':
        sentiment = 'positive'
    else:
        sentiment = 'negative'
    tweet = row[1]
    processedTweet = process_tweet(tweet)
    featureVector = get_feature_vector(processedTweet, stop_words)
    tweets.append((featureVector, sentiment))
    featureList.extend(featureVector)

featureList = list(set(featureList))
training_set = nltk.classify.util.apply_features(extract_features, tweets)

NBClassifier = nltk.NaiveBayesClassifier.train(training_set)

test_tweet = 'It\'s a hard day today. The feeling of head spinning, headache, body ache and with no appetite. Need a warm bath, dinner and a quiet rest.'
processedTweet = process_tweet(test_tweet)
print(NBClassifier.classify(extract_features(get_feature_vector(processedTweet, stop_words))))
