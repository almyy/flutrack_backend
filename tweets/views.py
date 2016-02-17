from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tweets.models import Tweet
from tweets.serializers import TweetSerializer


@csrf_exempt
@api_view(['GET'])
def tweets(request):
    client = MongoClient(
        'mongodb://heroku_k99m6wnb:slu38scru44f1c5s2v4h60ig72@ds011238.mongolab.com:11238/heroku_k99m6wnb')
    db = client.heroku_k99m6wnb
    collection = db.tweets
    cursor = collection.find()

    if request.method == 'GET':
        returned_tweets = []
        for t in cursor:
            tweet = Tweet(username=t['username'], lat=t['lat'], lng=t['lng'], text=t['text'])
            returned_tweets.append(tweet)
        serialized_list = TweetSerializer(returned_tweets, many=True)
        return Response(serialized_list.data)
