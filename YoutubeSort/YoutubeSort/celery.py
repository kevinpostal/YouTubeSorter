from __future__ import absolute_import, unicode_literals

import os

import django
from django.apps import apps
from django.conf import settings

from celery import Celery
from celery._state import _set_current_app

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YoutubeSort.settings")

django.setup()  # This is key

app = Celery("YoutubeSort")
app.config_from_object(settings)
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

redis_host = "redis://127.0.0.1:6379/0"

app.conf.broker_url = redis_host
app.conf.result_backend = redis_host

_set_current_app(app)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
