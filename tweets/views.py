from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tweets.models import Tweet
from tweets.serializers import TweetSerializer
import os


@csrf_exempt
@api_view(['GET'])
def tweets(request):
    mongo_uri = os.environ.get('MONGOLAB_URI')
    if mongo_uri is not None:
        client = MongoClient(mongo_uri)
        print('client connected')
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
