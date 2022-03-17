from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from google.auth.transport.requests import Request as GoogleAuthTransportRequest
from google.oauth2.credentials import Credentials as GoogleOauth2Credentials
from googleapiclient.discovery import build as googleapiclient_discovery_build
from youtube_dl import YoutubeDL
from YoutubeSort.models import YoutubeVideo

logger = get_task_logger(__name__)

User = get_user_model()

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


@shared_task
def set_artist_and_track(video_id: int) -> dict:
    """Scrape artist and track name by using youtube-dl.

    Args:
        video_id (int): Id for youtube video

    Returns:
        dict: Contains Artist name and Track title.

    """
    video_obj = YoutubeVideo.objects.get(id=video_id)
    ydl = YoutubeDL({"cookiefile": "youtube.com_cookies.txt"})
    with ydl:
        video = ydl.extract_info(video_obj.url, download=False)
        video_obj.artist = video.get("artist")
        video_obj.track = video.get("track")
        video_obj.save()
        return


@shared_task
def import_youtube_liked_videos_task(user_id):
    """Grab all youtube liked videos using google[youtube] api.

    Args:
        user_id (int): Credentials / `django user` id.

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

    while token is not None:
        for item in results["items"]:
            title = item.get("snippet", {}).get("title")
            image_url = item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url")
            obj_dict = {"title": title, "user": user, "image_url": image_url}
            obj, _ = YoutubeVideo.objects.update_or_create(yid=item.get("id"), defaults=obj_dict)

        results = youtube.videos().list(myRating="like", part="snippet", pageToken=token).execute()
        token = results.get("nextPageToken", None)


@shared_task
def import_youtube_playlists(user_id):
    """import_youtube_playlists

    Args:
        user_id (_type_): _description_
    """
    User.objects.get(id=user_id).import_youtube_liked_videos()
