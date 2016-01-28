from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    lat = serializers.CharField(required=False, max_length=50)
    lng = serializers.CharField(required=False, max_length=50)
    username = serializers.CharField(required=True, max_length=50)
    text = serializers.CharField(required=False, max_length=100)

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.lat = attrs.get('lat', instance.lat)
            instance.lng = attrs.get('lng', instance.lng)
            instance.username = attrs.get('username', instance.username)
            instance.text = attrs.get('text', instance.text)
            return instance

        return Tweet(attrs.get('lat'), attrs.get('lng'), attrs.get('username'), attrs.get('text'))
