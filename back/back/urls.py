"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from doubleFa.views import verify_view
from django.conf import settings
from django.conf.urls.static import static
from pong.views import signup, login_view, logout_view, edit_profile, main_view, home_view, \
	auth, handle_invite, send_invite, create_local_game, friend_match

urlpatterns = [
    path('admin/', admin.site.urls),
	path('verify/', verify_view, name="verify-view"),
	path('', home_view, name='home'),
	path('main/', main_view, name='main'),
	path('update_profile/', edit_profile, name='update_profile'),
	path('oauth/', auth, name='auth'),
	path('logout/', logout_view, name='logout'),
    path('accounts/login/', login_view, name='login'),
	path('handle_invite', handle_invite, name='handle_invite'),
	path('send_invite', send_invite, name='send_invite'),
	path('create_account/', send_invite, name='send_invite'),
	path('signup', signup, name='signup'),
    path('login/', login_view, name='login'),
	path('create_local_game', create_local_game, name='create_local_game'),
    path('friend_match/<str:friend_username>/', friend_match, name='friend_match'),
    # path('api/stats', StatsAPI.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#if settings.DEBUG:
#	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	#urlpatterns += static(settings.IMAGE_URL, document_root=settings.IMAGE_ROOT)