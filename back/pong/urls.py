from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from . import views
from . import consumers
# from .views import StatsAPI

urlpatterns = [
	path('', views.home, name='home'),
	path('update_profile', views.update_profile, name='test'),
	path('oauth/', views.auth, name='auth'),
	path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.sign_in, name='sign_in'),
	path('handle_invite', views.handle_invite, name='handle_invite'),
	path('send_invite', views.send_invite, name='send_invite'),
	path('create_account', views.send_invite, name='send_invite'),
	path('register', views.register, name='register'),
    path('sign_in', views.sign_in, name='sign_in'),
	# path('create_local_game', views.create_local_game, name='create_local_game'),
    path('match_stats_friends/', views.match_stats_friends, name='match_stats_friends'),
    re_path(r'ws/socket-pong-local/', consumers.PongLocal.as_asgi()),
    re_path(r'ws/socket-pong-online/', consumers.PongOnline.as_asgi()),
    re_path(r'ws/socket-pong-tournament-online/', consumers.PongOnlineTournament.as_asgi()),
    re_path(r'ws/stats/', consumers.StatsConsumer.as_asgi()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
