from django.urls import path

from youtube.views import YouTubeTransCriptView

urlpatterns = [
    path('get-transcript/', YouTubeTransCriptView.as_view(), name='get_transcript'),
]