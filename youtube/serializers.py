from rest_framework import serializers


class YouTubeURLSerializer(serializers.Serializer):
    url = serializers.URLField()