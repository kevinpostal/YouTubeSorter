from django.contrib import admin
from YoutubeSort.models import YoutubeVideo


class YoutubeVideodmin(admin.ModelAdmin):
    list_display = ["title", "artist", "track", "user"]


admin.site.register(YoutubeVideo, YoutubeVideodmin)
