from __future__ import absolute_import, unicode_literals

import os

# celery_pool_asyncio importing is optional
# It imports when you run worker or beat if you define pool or scheduler
# but it does not imports when you open REPL or when you run web application.
# If you want to apply monkey patches anyway to make identical environment
# when you use REPL or run web application app it's good idea to import
# celery_pool_asyncio module
# import celery_pool_asyncio  # noqa
import django
from celery import Celery
from celery._state import _set_current_app
from django.apps import apps
from django.conf import settings

# # Sometimes noqa does not disable linter (Spyder IDE)
# celery_pool_asyncio.__package__

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YoutubeSort.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()  # This is key

app = Celery("YoutubeSort")
app.config_from_object(settings)
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
app.conf.broker_url = os.environ.get("BROKER_URL", "redis://redis:6379/0")
app.conf.result_backend = os.environ.get("RESULT_BACKEND", "redis://redis:6379/0")
app.conf.task_send_sent_event = True

_set_current_app(app)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
