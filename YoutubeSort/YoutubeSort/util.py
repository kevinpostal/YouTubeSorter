import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import youtube_dl
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

channel_layer = get_channel_layer()

ydl = youtube_dl.YoutubeDL({"cookiefile": "youtube.com_cookies.txt"})


async def get_artist_and_track(url):
    with ydl:
        video = ydl.extract_info(url, download=False)
        artist = video.get("artist")
        track = video.get(
            "track",
        )
        return {"artist": artist, "track": track}


def get_youtube_liked_videos(credentials):
    print("Running task")
    credentials = google.oauth2.credentials.Credentials(**credentials)
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )
    results = youtube.videos().list(myRating="like", part="snippet", maxResults=500).execute()
    token = results.get("nextPageToken", None)

    while token != None:
        for item in results["items"]:
            url = "https://www.youtube.com/watch?v={}".format(item.get("id"))
            title = item.get("snippet").get("title")
            artist, track = async_to_sync(get_artist_and_track)(url).values()
            # artist, track = get_artist_and_track(url).values()

            if artist and track and url:
                item["artist"] = artist
                item["track"] = track
                item["url"] = url
                async_to_sync(channel_layer.group_send)(
                    "test",
                    {
                        "type": "chat.message",
                        "message": item,
                    },
                )
                # return

        results = youtube.videos().list(myRating="like", part="snippet", pageToken=token).execute()
        token = results.get("nextPageToken", None)

    return
