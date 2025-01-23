from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import YouTubeURLSerializer
from .service import YoutubeService


class YouTubeTransCriptView(APIView):
    def post(self, request):
        serializer = YouTubeURLSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        youtube_url = serializer.validated_data['url']
        try:
            service = YoutubeService()
            transcript = service.get_video_transcript(youtube_url)
            return Response({"transcribed_text": transcript}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)