# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.http import AsgiHandler
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from consumer import IndexConsumer

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YoutubeSort.settings')
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     'websocket': AuthMiddlewareStack(URLRouter([
#         path('index/', IndexConsumer)
#     ]))
# })

# mysite/asgi.py
import os
import signal
import sys
import time
import traceback

import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

from YoutubeSort.consumer import IndexConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YoutubeSort.settings")

try:
    django.setup()
    application = ProtocolTypeRouter(
        {
            "http": get_asgi_application(),
            "websocket": SessionMiddlewareStack(
                URLRouter([path("ws/list-videos", IndexConsumer.as_asgi())])
            ),
        }
    )
    print("WSGI without exception")
except Exception:
    print("handling WSGI exception")
    # Error loading applications
    if "mod_wsgi" in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
