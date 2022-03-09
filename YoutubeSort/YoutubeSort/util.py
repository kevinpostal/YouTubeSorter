import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

channel_layer = get_channel_layer()


async def get_youtube_liked_videos(credentials):
    credentials = google.oauth2.credentials.Credentials(**credentials)
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )
    results = youtube.videos().list(myRating="like", part="snippet", maxResults=500).execute()
    token = results.get("nextPageToken", None)
    data = []

    while token != None:
        for item in results["items"]:
            title = item.get("snippet").get("title")
            data.append(title)

            async_to_sync(channel_layer.group_send)(
                "test",
                {
                    "type": "chat.message",
                    "message": title,
                },
            )

        results = youtube.videos().list(myRating="like", part="snippet", pageToken=token).execute()
        token = results.get("nextPageToken", None)
