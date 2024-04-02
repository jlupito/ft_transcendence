from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, logout
from .models import UserProfile, Match, Friend, User
from django.contrib.auth.decorators import login_required
import requests
import os



def home(request):
	context = {}
	if (request.user.is_authenticated):
		matches = match_history(request.user)
		context = {
			'matches': matches,
		}
	return render(request, 'page.html', context)

@login_required
def logout_view(request):
	logout(request)
	return redirect('home')

def match_history(user):
	matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
	ret = []
	for match in matches:
		if match.player1 == user:
			user_score = match.player1_score
			opponent_score = match.player2_score
			opponent = match.player2
		else:
			user_score = match.player2_score
			opponent_score = match.player1_score
			opponent = match.player1
		if (user_score > opponent_score):
			ret.append("Win vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ")")
		elif (user_score < opponent_score):
			ret.append("Loss vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ")")
		else:
			ret.append("Draw vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ")")
	return ret

def auth(request):
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
	intra_login = response.json()['login']
	user = User.objects.filter(username=intra_login).first()
	if user is None:
		print('Creating user')
		user = User.objects.create_user(username=intra_login, first_name=intra_login)
		UserProfile.objects.create(user=user)
	login(request, user)
	return redirect('home')
