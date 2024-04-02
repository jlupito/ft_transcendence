from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, logout
from .models import UserProfile, Match, Friend, User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os

def home(request):
	context = {}
	if (request.user.is_authenticated):
		avatar_url = UserProfile.objects.get(user=request.user).avatar.url
		print (avatar_url)
		matches = match_history(request.user)
		friends = friends_list(request.user)
		invites = invites_list(request.user)
		context = {
			'avatar_url': avatar_url,
			'invites': invites,
			'friends': friends,
			'matches': matches,
		}
	return render(request, 'page.html', context)

@login_required
def logout_view(request):
	logout(request)
	return redirect('home')

def match_history(user):
	matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
	l = []
	for match in matches:
		time = match.timestamp.strftime('%d/%m/%Y %H:%M')
		if match.player1 == user:
			user_score = match.player1_score
			opponent_score = match.player2_score
			opponent = match.player2
		else:
			user_score = match.player2_score
			opponent_score = match.player1_score
			opponent = match.player1
		if (user_score > opponent_score):
			l.append("Win vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ") played on " + time)
		elif (user_score < opponent_score):
			l.append("Loss vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ") played on " + time)
		else:
			l.append("Draw vs " + opponent.username + " (" + str(user_score) + " - " + str(opponent_score) + ") played on " + time)
	return l

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	l = []
	for friend in friends:
		if friend.sender == user:
			l.append(friend.receiver)
		else:
			l.append(friend.sender)
	return l

def invites_list(user):
	invites = Friend.objects.filter(receiver=user, status='pending')
	l = []
	for invite in invites:
		l.append(invite.sender)
	return l

def update_profile(request):
	if request.method == 'GET':
		return redirect('home')
	username = request.POST.get('username')
	profile_picture = request.FILES.get('profile_picture')
	if (profile_picture is not None):
		validate = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
		try:
			validate(profile_picture)
		except ValidationError as e:
			messages.error(request, 'Invalid file type')
			return redirect('home')
	if (User.objects.filter(first_name=username).exists() and username != request.user.first_name):
		messages.error(request, 'Username already taken')
		return redirect('home')
	user = request.user
	user.first_name = username
	if (profile_picture is not None):
		user_profile = UserProfile.objects.get(user=user)
		if user_profile.avatar.url != "/media/avatars/default.png":
			user_profile.avatar.delete()
		profile_picture.name = user.username
		user_profile.avatar = profile_picture
		user_profile.save()
	user.save()
	return redirect('home')

def accept_invite(request):
	if request.method == 'GET':
		return redirect('home')
	#Do something with the request.POST
	return redirect('home')

def decline_invite(request):
	if request.method == 'GET':
		return redirect('home')
	#Do something with the request.POST
	return redirect('home')

def send_invite(request):
	if request.method == 'GET':
		return redirect('home')
	#Do something with the request.POST
	return redirect('home')

@never_cache
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
		user = User.objects.create_user(username=intra_login, first_name=intra_login)
		UserProfile.objects.create(user=user)
	login(request, user)
	return redirect('home')
