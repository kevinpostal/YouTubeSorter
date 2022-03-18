import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from YoutubeSort.tasks import import_youtube_liked_videos_task

User = get_user_model()


class IndexConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        def _get_scope():
            self.credentials = self.scope["session"].get("credentials")
            return  # self.scope["session"]["credentials"]

        self.room_name = "test"
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await sync_to_async(_get_scope, thread_sensitive=True)()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message == "get_videos":
            # user = await sync_to_async(User.objects.get)(id=self.scope["session"]["_auth_user_id"])
            import_youtube_liked_videos_task.delay(self.scope["session"]["_auth_user_id"])
        else:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_name, {
                    "type": "chat_message",
                    "message": message
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
