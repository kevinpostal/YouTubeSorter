from channels.layers import get_channel_layer
from google.auth.transport.requests import Request as GoogleAuthTransportRequest
from google.oauth2.credentials import Credentials as GoogleOauth2Credentials
from googleapiclient.discovery import build as googleapiclient_discovery_build
from YoutubeAuth.models import Credentials
from YoutubeSort.models import YoutubeVideo

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

channel_layer = get_channel_layer()

# def import_youtube_liked_videos(credentials_obj: Credentials):
#     """Grab all youtube liked videos using google[youtube] api.

#     Args:
#         credentials_obj (Credentials): Credentials / `django user` object.

#     """

#     credentials = GoogleOauth2Credentials(**credentials_obj.credentials_to_dict())
#     youtube = googleapiclient_discovery_build(
#         API_SERVICE_NAME,
#         API_VERSION,
#         credentials=credentials,
#     )

#     try:
#         results = youtube.videos().list(myRating="like", part="snippet", maxResults=50).execute()
#     except Exception:
#         request = GoogleAuthTransportRequest()
#         credentials.refresh(request)
#         youtube = googleapiclient_discovery_build(
#             API_SERVICE_NAME,
#             API_VERSION,
#             credentials=credentials,
#         )
#         results = youtube.videos().list(myRating="like", part="snippet", maxResults=50).execute()

#     token = results.get("nextPageToken", None)

#     while token is not None:
#         for item in results["items"]:
#             title = item.get("snippet", {}).get("title")
#             image_url = item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url")
#             obj_dict = {"title": title, "user": credentials_obj, "image_url": image_url}
#             obj, _ = YoutubeVideo.objects.update_or_create(yid=item.get("id"), defaults=obj_dict)
#             item["obj_id"] = obj.id

#         results = youtube.videos().list(myRating="like", part="snippet", pageToken=token).execute()
#         token = results.get("nextPageToken", None)
