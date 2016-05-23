from rest_framework.decorators import api_view
from rest_framework.response import Response

from prediction import distribute_city_population


@api_view(['GET'])
def prediction(request):
    if request.method == 'GET':
        return Response(distribute_city_population.forecast(False))


