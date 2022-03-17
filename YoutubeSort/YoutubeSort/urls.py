from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from YoutubeSort import api, views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("list-videos/", api.GetVideos.as_view(), name="list-videos"),
    path("get-videos/", views.get_videos, name="get-videos"),
    path("", include("YoutubeAuth.urls")),
    path("", views.index, name="index"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
