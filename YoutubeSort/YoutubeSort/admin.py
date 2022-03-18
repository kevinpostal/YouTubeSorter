from django.contrib import admin
from YoutubeSort.models import YoutubePlaylist, YoutubeVideo


class YoutubeVideoAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "track", "user"]


class YoutubePlaylistAdmin(admin.ModelAdmin):
    list_display = ["yt_playlist_id", "title", "description", "user"]


admin.site.register(YoutubeVideo, YoutubeVideoAdmin)
admin.site.register(YoutubePlaylist, YoutubePlaylistAdmin)
