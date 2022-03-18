import json
from typing import Optional

from asgiref.sync import async_to_sync
from celery import current_app
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

channel_layer = get_channel_layer()

# class YoutubePlaylist(models.Model):
#     pass


class YoutubeVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)
    track = models.CharField(max_length=255, blank=True, null=True)
    yid = models.CharField(max_length=255, unique=True)
    image_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def url(self) -> str:
        """Return Youtube url.

        Returns:
            str: Youtube Url.

        """
        return "https://www.youtube.com/watch?v={0}".format(self.yid)

    def model_to_dict(self, include: Optional[dict] = None, exclude: Optional[dict] = None) -> dict:
        """Convert YoutubeVideo model to a dictonary using DjangoJSONEncoder.

        Args:
            include (Optional[dict], optional): fields to include. Defaults to None.
            exclude (Optional[dict], optional): fields to exclude. Defaults to None.

        Returns:
            dict: Model as dictonary.

        """
        fields = self._meta.concrete_fields
        if include is not None:
            data_dict = {
                item.attname: getattr(self, item.attname) for item in fields if item.name in include
            }
        if exclude is not None:
            data_dict = {
                item.attname: getattr(self, item.attname)
                for item in fields
                if item.name not in exclude
            }
        else:
            data_dict = {
                item.attname:
                getattr(self, item.attname) if getattr(self, item.attname) is not None else ""
                for item in fields
            }

        return json.loads(json.dumps(data_dict, cls=DjangoJSONEncoder))

    def set_artist_and_track(self):
        """Grab and save the "artist" name & "track" title if found."""
        current_app.send_task("YoutubeSort.tasks.set_artist_and_track", (self.id, self.url))


@receiver(post_save, sender=YoutubeVideo, dispatch_uid="scrape_artist_and_track_signal")
def import_youtube_artist_and_track_signal(sender: YoutubeVideo, instance, created, **kwargs):
    """Signal on `YoutubeVideo` post_save for scraping youtube liked videos.

    Args:
        sender (YoutubeVideo): _description_
        instance: _description_
        created: _description_
        kwargs: kwargs

    """
    if created:
        instance.set_artist_and_track()
    else:
        pass
        # async_to_sync(channel_layer.group_send
        #               )("test", {
        #                   'type': 'chat.message',
        #                   'message': instance.model_to_dict(),
        #               })
