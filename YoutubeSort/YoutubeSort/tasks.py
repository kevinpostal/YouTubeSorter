from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

from .util import get_youtube_liked_videos


@shared_task
def get_youtube_liked_videos_task(credentials):
    get_youtube_liked_videos(credentials)
    return
