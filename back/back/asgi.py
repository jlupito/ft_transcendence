"""
ASGI config for back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.urls import re_path
from pong import consumers
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pong.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(
        URLRouter(
            # pong.routing.websocket_urlpatterns
            [
            re_path(r'ws/socket-pong-local/', consumers.PongLocal.as_asgi()),
            re_path(r'ws/socket-pong-online/', consumers.PongOnline.as_asgi()),
            re_path(r'ws/socket-pong-tournament-online/', consumers.PongOnlineTournament.as_asgi()),
            re_path(r'ws/stats/$', consumers.StatsConsumer.as_asgi()),
            ]
        )
    )
})
