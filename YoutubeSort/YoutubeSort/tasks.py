from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from google.auth.transport.requests import Request as GoogleAuthTransportRequest
from google.oauth2.credentials import Credentials as GoogleOauth2Credentials
from googleapiclient.discovery import build as googleapiclient_discovery_build
from youtube_dl import YoutubeDL
from YoutubeSort.models import YoutubePlaylist, YoutubeVideo

logger = get_task_logger(__name__)

User = get_user_model()

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

channel_layer = get_channel_layer()


@shared_task(ignore_result=True)
def set_artist_and_track(video_id: int, video_url: str) -> dict:
    """Scrape artist and track name by using youtube-dl.

    Args:
        video_id (int): Id for youtube video

    Returns:
        dict: Contains Artist name and Track title.

    """

    ydl = YoutubeDL({"cookiefile": "youtube.com_cookies.txt"})

    with ydl:
        video = ydl.extract_info(video_url, download=False)

        data_dict = {
            "artist": video.get("artist", ""),
            "track": video.get("track", ""),
        }

        YoutubeVideo.objects.filter(pk=video_id).update(**data_dict)

        # video_obj.artist = data_dict.get("artist", "")
        # video_obj.track = data_dict.get("track", "")
        # video_obj.save()

        video_dict = video_obj.model_to_dict()
        async_to_sync(channel_layer.group_send
                      )("test", {
                          'type': 'chat.message',
                          'message': video_dict,
                      })


@shared_task(ignore_result=True)
def import_youtube_liked_videos_task(user_id):
    """Grab all youtube liked videos using google[youtube] api.

    Args:
        user_id (int): Credentials / `django user` id.

    Returns:
        list: id + created list result.

    """
    user = User.objects.get(id=user_id)
    credentials = GoogleOauth2Credentials(**user.credentials_to_dict())
    youtube = googleapiclient_discovery_build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials,
    )

    try:
        results = youtube.videos().list(myRating="like", part="snippet", maxResults=50).execute()
    except Exception:
        request = GoogleAuthTransportRequest()
        credentials.refresh(request)
        youtube = googleapiclient_discovery_build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
        )
        results = youtube.videos().list(myRating="like", part="snippet", maxResults=50).execute()

    token = results.get("nextPageToken", None)
    return_data = []
    while token is not None:
        for item in results["items"]:
            title = item.get("snippet", {}).get("title")
            image_url = item.get("snippet", {}).get("thumbnails", {}).get("default",
                                                                          {}).get("url", "")
            obj_dict = {"title": title, "user": user, "image_url": image_url}
            obj, created = YoutubeVideo.objects.update_or_create(
                yid=item.get("id"),
                defaults=obj_dict,
            )
            return_data.append((obj.id, created))
        results = youtube.videos().list(myRating="like", part="snippet", pageToken=token).execute()
        token = results.get("nextPageToken", None)
    return return_data


@shared_task
def import_youtube_playlist_videos(playlist_pk):
    """_summary_

    Args:
        playlist_pk (_type_): _description_

    Returns:
        _type_: _description_
    """
    playlist_obj = YoutubePlaylist.objects.get(pk=playlist_pk)
    credentials = GoogleOauth2Credentials(**playlist_obj.user.credentials_to_dict())
    youtube = googleapiclient_discovery_build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials,
    )
    try:
        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id,
            part="snippet",
        ).execute()
    except Exception:
        request = GoogleAuthTransportRequest()
        credentials.refresh(request)
        youtube = googleapiclient_discovery_build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
        )
        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id,
            part="snippet",
            maxResults=50,
        ).execute()

    token = results.get("nextPageToken", True)
    return_data = []
    while token is not None:
        for item in results["items"]:
            title = item.get("snippet", {}).get("title")
            image_url = item.get("snippet", {}).get("thumbnails", {}).get("default",
                                                                          {}).get("url", "")
            obj_dict = {
                "title": title,
                "user": playlist_obj.user,
                "playlist": playlist_obj,
                "image_url": image_url,
            }
            obj, created = YoutubeVideo.objects.update_or_create(
                yid=item.get("id"),
                defaults=obj_dict,
            )
            return_data.append((obj.id, created))
        results = youtube.playlistItems().list(
            playlistId=playlist_obj.yt_playlist_id, part="snippet", maxResults=50, pageToken=token
        ).execute()
        token = results.get("nextPageToken", None)
    return return_data


@shared_task
def import_youtube_playlists(user_id):
    """import_youtube_playlists.

    Args:
        user_id (_type_): _description_.

    """
    user = User.objects.get(id=user_id)
    credentials = GoogleOauth2Credentials(**user.credentials_to_dict())
    youtube = googleapiclient_discovery_build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials,
    )

    try:
        results = youtube.playlists().list(mine=True, part="snippet").execute()
    except Exception:
        request = GoogleAuthTransportRequest()
        credentials.refresh(request)
        youtube = googleapiclient_discovery_build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
        )
        results = youtube.playlists().list(mine=True, part="snippet").execute()

    return_data = []

    for item in results["items"]:
        title = item.get("snippet", {}).get("title")
        playlist_id = item.get("id")
        description = item.get("snippet", {}).get("description")
        image_url = item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url", "")
        obj_dict = {
            "title": title,
            "description": description,
            "user": user,
            "image_url": image_url
        }
        obj, created = YoutubePlaylist.objects.update_or_create(
            yt_playlist_id=playlist_id,
            defaults=obj_dict,
        )
        return_data.append((obj.id, created))

    obj_dict = {
        "title": "Liked Videos",
        "description": "Liked Videos",
        "user": user,
        "image_url": "BLANK",
    }
    obj, created = YoutubePlaylist.objects.update_or_create(
        yt_playlist_id="LL",
        defaults=obj_dict,
    )
    return_data.append((obj.id, created))

    return return_data
