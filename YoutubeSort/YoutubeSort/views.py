from asgiref.sync import async_to_sync
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse

from .util import get_youtube_liked_videos


async def index(request):
    return render(request, "index.html", {})


def get_videos(request):
    # del request.session['credentials']
    credentials = request.session.get("credentials", False)

    if credentials:
        # await get_youtube_liked_videos(credentials)
        return HttpResponse("GOOD")
    else:
        return redirect(reverse("auth"))
