from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/socket-pong-local/', consumers.PongLocal.as_asgi()),
    re_path(r'ws/socket-pong-online/', consumers.PongOnline.as_asgi()),
    re_path(r'ws/socket-pong-tournament-online/', consumers.PongOnlineTournament.as_asgi()),
    re_path(r'ws/socket-pong-tournament-local/', consumers.PongLocalTournament.as_asgi()),
    re_path(r'ws/stats/', consumers.StatsConsumer.as_asgi())
]