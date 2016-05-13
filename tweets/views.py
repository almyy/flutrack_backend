from rest_framework.decorators import api_view
from rest_framework.response import Response

from prediction import twitter_epidemic


@api_view(['GET'])
def tweets(request):
    if request.method == 'GET':
        return Response(twitter_epidemic.get_tweets_per_week())
