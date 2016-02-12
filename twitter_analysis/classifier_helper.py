import re


class ClassifierHelper:

    def strip_extra_characters(self, s):
        # pattern to look for three or more repetitions of any character, including
        # newlines.
        pattern = re.compile(r"(.)\1+", re.DOTALL)
        return pattern.sub(r"\1\1", s)

    def process_tweet(self, tweet):
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
        tweet = tweet.strip('\'?!,.')
        tweet = self.strip_extra_characters(tweet)
        return tweet
