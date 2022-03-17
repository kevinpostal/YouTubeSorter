import google.oauth2.credentials
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from YoutubeSort.models import YoutubeVideo


@user_passes_test(
    lambda u: not u.is_superuser,
    login_url="/admin/",
)
@login_required(login_url="/auth/")
def index(request):
    videos = YoutubeVideo.objects.filter(user=request.user).order_by("created_at", "updated_at")
    video_list = [item.model_to_dict() for item in videos]

    return render(request, "index.html", context={"video_list": video_list})


def get_videos(request):
    credentials_dict = request.session.get("credentials", False)
    credentials = google.oauth2.credentials.Credentials(**credentials_dict)

    if credentials:
        return HttpResponse("GOOD")
    else:
        return redirect(reverse("auth"))
