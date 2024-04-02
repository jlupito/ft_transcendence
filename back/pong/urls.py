from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('oauth/', views.auth, name='auth'),
	path('logout/', views.logout_view, name='logout'),
]
