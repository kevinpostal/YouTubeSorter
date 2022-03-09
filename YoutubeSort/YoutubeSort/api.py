from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import permissions
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GetVideos(APIView):
    """
    View to get all youtube videos
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        channel_layer = get_channel_layer()
        text = "123"

        async_to_sync(channel_layer.group_send)(
            'index', {
                'type': 'websocket.ingest',
                'text': text
                }
        )
        return Response([])