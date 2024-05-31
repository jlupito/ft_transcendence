from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
# from .views import StatsAPI

urlpatterns = [
	path('', views.home_view, name='home'),
	path('edit_profile', views.edit_profile_view, name='edit_profile'),
	path('oauth/', views.auth, name='auth'),
	path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view, name='sign_in'),
	path('handle_invite', views.handle_invite, name='handle_invite'),
	path('send_invite', views.send_invite, name='send_invite'),
	path('create_account', views.send_invite, name='send_invite'),
	path('signup', views.signup_view, name='register'),
    path('login', views.login_view, name='sign_in'),
	path('create_local_game', views.create_local_game, name='create_local_game'),
    path('friend_match/<str:friend_username>/', views.friend_match, name='friend_match'),
    # path('api/stats', StatsAPI.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
