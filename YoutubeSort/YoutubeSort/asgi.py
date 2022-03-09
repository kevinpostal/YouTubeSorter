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

import django
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from YoutubeSort.consumer import IndexConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YoutubeSort.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': URLRouter([
        path('ws/list-videos', IndexConsumer.as_asgi())
    ])
})