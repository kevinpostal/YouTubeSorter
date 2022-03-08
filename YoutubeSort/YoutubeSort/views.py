from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.shortcuts import redirect
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def list_videos(request):
    #del request.session['credentials']
    credentials = request.session.get('credentials', False)

    if not credentials:
        return redirect(reverse('auth'))

    credentials = google.oauth2.credentials.Credentials(**credentials)
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    results = youtube.videos().list(myRating='like', part='snippet',maxResults=500).execute()
    token = results.get('nextPageToken', None)   
    data = []
    
    while token!=None:
        for item in results["items"]:
            data.append(item.get("snippet").get("channelTitle"))
        results = youtube.videos().list(myRating='like', part='snippet', pageToken=token).execute()
        token = results.get('nextPageToken', None)

    return HttpResponse(data)
