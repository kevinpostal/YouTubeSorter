import google.oauth2.credentials
import googleapiclient.discovery
from asgiref.sync import async_to_sync
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse

from .tasks import get_youtube_liked_videos_task


async def index(request):
    return render(request, "index.html", {})


def get_videos(request):
    # del request.session['credentials']
    credentials_dict = request.session.get("credentials", False)
    credentials = google.oauth2.credentials.Credentials(**credentials_dict)

    if credentials:
        # get_youtube_liked_videos_task.delay(credentials)

        return HttpResponse("GOOD")
    else:
        return redirect(reverse("auth"))
