from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Match, Friend, User
import requests
import os

# Create your views here.
def home(request):
	template = loader.get_template('page.html')
	return HttpResponse(template.render())

def login(request):
	code = request.GET.get('code')
	uid = os.environ.get('UID')
	secret = os.environ.get('SECRET')
	token_url = 'https://api.intra.42.fr/oauth/token'
	data = {
		'grant_type': 'authorization_code',
		'client_id': uid,
		'client_secret': secret,
		'code': code,
		'redirect_uri': 'http://localhost:8000/oauth',
	}
	response = requests.post(token_url, data=data)
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get access token</h1>')
	access_token = response.json()['access_token']
	response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + access_token})
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get user info</h1>')
	name = response.json()['login']
	if (User.objects.filter(username=name).exists()):
		return HttpResponse('<h1>Already registered</h1><h2>Info\n: ' + name + str(response.json()) + '</h2>')
	else :
		user = User.objects.create_user(username=name)
		return HttpResponse('<h1>First connection</h1><h2>Username: ' + name + '</h2>')
