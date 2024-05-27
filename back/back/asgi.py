"""
ASGI config for back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

from .wsgi import *  # add this line to top of your code
import os, django
from django.urls import re_path
from pong import consumers
from django.core.asgi import get_asgi_application

# DockerDjangoNginx is my project name
# your routing.py file should be in this location where the wsgi.py file is placed
# DockerDjangoNginx/DockerDjangoNginx/routing.py

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
django_asgi_app = get_asgi_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'https': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
            re_path(r'ws/socket-pong-local/', consumers.PongLocal.as_asgi()),
            re_path(r'ws/socket-pong-online/', consumers.PongOnline.as_asgi()),
            re_path(r'ws/socket-pong-tournament-online/', consumers.PongOnlineTournament.as_asgi())
            ]
        )
    ),
})
