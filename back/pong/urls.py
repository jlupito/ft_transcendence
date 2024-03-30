from django.urls import path
from . import views

urlpatterns = [
	path('home/', views.home, name='home'),
	path('oauth/', views.login, name='login'),
]
