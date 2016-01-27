from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tweets.models import Tweet
from tweets.serializers import TweetSerializer


@csrf_exempt
@api_view(['GET'])
def tweets(request):
    client = MongoClient()
    db = client.flutrack_db
    collection = db.tweets
    cursor = collection.find()

    if request.method == 'GET':
        returned_tweets = []
        for t in cursor:
            tweet = Tweet(t['_id'], t['lat'], t['lng'], t['username'], t['text'])
            returned_tweets.append(tweet)
        serialized_list = TweetSerializer(returned_tweets, many=True)
        return Response(serialized_list.data)
