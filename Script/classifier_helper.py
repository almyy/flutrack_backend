import re


class ClassifierHelper:
    # start __init__
    def __init__(self, feature_list_file):
        self.wordFeatures = feature_list_file
        # Read feature list
        # inpfile = open(feature_list_file, 'r')
        # line = inpfile.readline()
        # while line:
        #     self.wordFeatures.append(line.strip())
        #     line = inpfile.readline()

    # end

    # start extract_features
    def extract_features(self, document):
        document_words = set(document)
        features = {}
        for word in self.wordFeatures:
            word = word.strip('\'"?,.')
            features['contains(%s)' % word] = (word in document_words)
        return features

    # end

    # start replaceTwoOrMore
    @staticmethod
    def replace_two_or_more(s):
        # pattern to look for three or more repetitions of any character, including
        # newlines.
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", s)

    # end

    #start getfeatureVector
    def get_feature_vector(self, tweet, stop_words):
        featureVector = []
        #split tweet into words
        words = tweet.split()
        for w in words:
            #replace two or more with two occurrences
            w = self.replace_two_or_more(w)
            #strip punctuation
            w = w.strip('\'"?,.')
            #check if the word stats with an alphabet
            val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
            #ignore if it is a stop word
            if w in stop_words or val is None:
                continue
            else:
                featureVector.append(w.lower())
        return featureVector
    #end

    def get_svm_feature_vector_and_labels(self, tweets):
        sorted_features = sorted(self.wordFeatures)
        feature_vector = []
        labels = []
        for t in tweets:
            label = 0
            map = {}
            # Initialize empty map
            for w in sorted_features:
                map[w] = 0

            tweet_words = t[0]
            tweet_opinion = t[1]
            # Fill the map
            for word in tweet_words:
                word = self.replace_two_or_more(word)
                word = word.strip('\'"?,.')
                if word in map:
                    map[word] = 1
            # end for loop
            values = map.values()
            feature_vector.append(values)
            if tweet_opinion == 'positive':
                label = 0
            elif tweet_opinion == 'negative':
                label = 1
            elif tweet_opinion == 'neutral':
                label = 2
            labels.append(label)
        return {'feature_vector': feature_vector, 'labels': labels}

    # end

    # start getSVMFeatureVector
    def get_svm_feature_vector(self, tweets):
        sorted_features = sorted(self.wordFeatures)
        feature_vector = []
        for t in tweets:
            map = {}
            # Initialize empty map
            for w in sorted_features:
                map[w] = 0
            # Fill the map
            for word in t:
                if word in map:
                    map[word] = 1
            # end for loop
            values = map.values()
            feature_vector.append(values)
        return feature_vector

    # end

    # start process_tweet
    @staticmethod
    def process_tweet(tweet):
        # Convert to lower case
        tweet = tweet.lower()
        # Convert https?://* to URL
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        # Convert @username to AT_USER
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
        # Remove additional white spaces
        tweet = re.sub('[\s]+', ' ', tweet)
        # Replace #word with word
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        # trim
        tweet = tweet.strip()
        # remove first/last " or 'at string end
        tweet = tweet.rstrip('\'"')
        tweet = tweet.lstrip('\'"')
        return tweet

    # end

    # start is_ascii
    @staticmethod
    def is_ascii(word):
        return all(ord(c) < 128 for c in word)
        # end
        # end class


if __name__ == '__main__':
    ClassifierHelper('data/feature_list.txt')
