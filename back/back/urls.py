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
# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('', include('pong.urls')),
#     path('admin/', admin.site.urls),
# ]
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from users.views import signup, login_user, logout_user, edit_profile, auth
from doubleAuth.views import verify_view
from pong.views import home, create_local_game
from friends.views import handle_invite, send_invite

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', home, name='home'),
	path('oauth/', auth, name='auth'),
	path('users/edit_profile/', edit_profile, name='edit_profile'),
	path('signup/', signup, name="signup"),
	path('logout/', logout_user, name="logout"),
	path('login/', login_user, name="login"),
	path('verify/', verify_view, name="verify-view"),
	path('handle_invite', handle_invite, name='handle_invite'),
	path('send_invite', send_invite, name='send_invite'),
	path('create_local_game', create_local_game, name='create_local_game')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)