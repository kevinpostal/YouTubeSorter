import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .tasks import get_youtube_liked_videos_task


class IndexConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        def _get_scope():
            session = self.scope.get("session", {}).get("credentials")
            self.credentials = session
            return  # self.scope["session"]["credentials"]

        self.room_name = "test"
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await sync_to_async(_get_scope, thread_sensitive=True)()
        print("Connected {}".format(self.room_name))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # print("Receive: {}".format(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message == "get_videos":
            get_youtube_liked_videos_task.delay(self.credentials)
        else:
            pass
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_name, {"type": "chat_message", "message": message}
            )

    # Receive message from room group
    async def chat_message(self, event):
        # print("Receive: {}".format(event))
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
