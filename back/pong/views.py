from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile, Match, Friend, Tournoi
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from .forms import RegisterForm, LoginForm, localMatchForm
from .consumers import Game, Tournament, StatsConsumer
from tempfile import NamedTemporaryFile
from django.core.files.base import ContentFile

def home(request):
	context = {}
	if (request.user.is_authenticated):
		avatar_url = UserProfile.objects.get(user=request.user).avatar.url
		users = UserProfile.objects.exclude(user=request.user)
		matches = match_history(request.user)
		stats = match_stats(request.user)
		friends = friends_list(request.user)
		tournament = current_tournament(request.user)
		context = {
			'users': users,
			'avatar_url': avatar_url,
			'friends': friends,
			'matches': matches,
			'stats' : stats,
			'matches_all': match_history_all(),
			'current_tourn' : tournament,
		}
	return render(request, 'page.html', context)

# *********************************** LOGIN ***********************************

@login_required
def logout_view(request):
	logout(request)
	messages.success(request, 'You are logged out!')
	return redirect('home')

def sign_in(request):
	if request.method == 'POST':
		loginform = LoginForm(request.POST)

		if loginform.is_valid():
			# verifier avec le mail ou avec le username ???? Plus complexe avec un mail mais faisable
			user=authenticate(
				username=loginform.cleaned_data['username'],
				password=loginform.cleaned_data['password']
				)
			if user is not None:
				login(request, user)
				messages.success(request, 'You are now logged in!')
			else:
				messages.error(request, 'Invalid username or password')
	else:
		loginform=LoginForm()
	return redirect('home')

# Lancer la creation d'un compte
def register(request):
	if request.method == 'POST':
		registerform = RegisterForm(request.POST)
		if registerform.is_valid():
			username=registerform.cleaned_data['username']
			if User.objects.filter(username=username).exists():
				messages.error(request, 'This username is already used!') # Modifier la posiiton du message de front
				# registerform = RegisterForm() # ne change rien == maintenir le form ?
				return redirect('home')
			mdp=registerform.cleaned_data['password']
			email=registerform.cleaned_data['email']
			if User.objects.filter(email=email).exists():
				messages.error(request, 'This email is already in use...')
				return redirect('home')
			new_user = User.objects.create_user(username=username, password=mdp, email=email, first_name=username)
			UserProfile.objects.create(user=new_user)
			login(request, new_user)
			messages.success(request, 'Account created successfully!')
			return redirect('home')
		else:
			messages.error(request, 'Invalid form data')
	else:
		registerform = RegisterForm()
	return redirect('home')

# *********************************** PROFILE ***********************************

def save_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return ContentFile(response.content)
    else:
        return None
	
@never_cache
def auth(request):
	code = request.GET.get('code')
	uid = os.environ.get('UID')
	secret = os.environ.get('SECRET')
	token_url = 'http://api.intra.42.fr/oauth/token'
	data = {
		'grant_type': 'authorization_code',
		'client_id': uid,
		'client_secret': secret,
		'code': code,
		'redirect_uri': 'https://localhost:8001/oauth',
	}
	response = requests.post(token_url, data=data)
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get access token</h1>')
	access_token = response.json()['access_token']
	response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + access_token})
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get user info</h1>')
	intra_login = response.json()['login']
	intra_email = response.json()['email']
	intra_picture = response.json()['image']['link']
	picture = save_image(intra_picture)
	user = User.objects.filter(username=intra_login).first()
	if user is None:
		user = User.objects.create_user(username=intra_login, first_name=intra_login, email=intra_email)
		UserProfile.objects.create(user=user)
		if (picture is not None):
			user_profile = UserProfile.objects.get(user=user)
			if user_profile.avatar.url != "/media/avatars/default2.png":
				user_profile.avatar.delete()
			picture.name = user.username
			user_profile.avatar.save('intra_img.jpg', picture, save=True)
	login(request, user)
	messages.success(request, 'You are now logged in!')
	return redirect('home')

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
		if user_profile.avatar.url != "/media/avatars/default2.png":
			user_profile.avatar.delete()
		profile_picture.name = user.username
		user_profile.avatar = profile_picture
		user_profile.save()
	user.save()
	return redirect('home')


# *********************************** MATCHES HISTORY ***********************************

# def match_history_friends(request):
# 	username = request.GET.get('username')
# 	user = User.objects.get(username=username)
# 	stats = match_history(user)
# 	return JsonResponse(stats, safe=False)

def match_history_all():
	matches = Match.objects.all()
	l = list(matches)
	return l

def match_stats(user):
	user = User.objects.filter(username=user).first()
	matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
	won = 0
	lost = 0
	for match in matches:
		if match.player1 == user:
			if match.player1_score > match.player2_score:
				won += 1
			else:
				lost += 1
		else:
			if match.player1_score < match.player2_score:
				won += 1
			else:
				lost += 1
	total = matches.count()
	if total == 0:
		won_perc = 0
		lost_perc = 0
	else:
		won_perc = round(won / total * 100)
		lost_perc = round(lost / total * 100)

	tournaments = Tournoi.objects.all()
	tourn = 0
	for tournament in tournaments:
		if tournament.tourn_winner == user.username:
			tourn += 1
	stats = {
        'won': won,
        'lost': lost,
        'wp': won_perc,
        'lp': lost_perc,
        'tourn': tourn,
    }
	
	return stats

def current_tournament(user):
	tournament = Tournoi.objects.filter(tourn_winner__isnull=True, l_players__contains=user.username).first()
	if tournament:
		return tournament
	else:
		return None

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
		match_result = {
        "opponent_name": opponent.username,
        "opponent_score": opponent_score,
        "user_score": user_score,
        "time": time,
		}
		if (user_score > opponent_score):
			match_result["result"] = "Win"
		elif (user_score < opponent_score):
			match_result["result"] = "Loss"
		l.append(match_result)
	return l

# *********************************** FRIENDS ***********************************

def friend_match(request, friend_name):
    friend_user = User.objects.get(username=friend_name)
    fmatches = match_history(friend_user)
    return render(request, 'friend_match', {'matches': fmatches})

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(UserProfile.objects.get(user=friend.receiver))
		else:
			profiles.append(UserProfile.objects.get(user=friend.sender))
	friends_l = []
	for profile in profiles:
		friends_l.append(profile)

	invites = Friend.objects.filter(receiver=user, status='pending')
	invites_l = []
	for invite in invites:
		invites_l.append(invite.sender.username)
	
	invitees = Friend.objects.filter(sender=user, status='pending')
	invitees_l = []
	for invitee in invitees:
		invitees_l.append(invitee.receiver.username)
	
	friends_all_status = {
        "friends": friends_l,
        "invitees": invitees_l,
        "invites": invites_l,
		}

	return friends_all_status

@login_required
def handle_invite(request):
	if request.method == 'GET':
		return redirect('home')
	sender = request.POST.get('invite')
	receiver = request.user
	status = request.POST.get('status')
	inv = Friend.objects.filter(sender=User.objects.get(username=sender), receiver=receiver).first()
	if inv:
		inv.status = status
		inv.save()
	return redirect('home')

def send_invite(request):
	if request.method == 'GET':
		return redirect('home')
	receiver = request.POST.get('receiver')
	sender = request.user
	friends_l = friends_list(sender)
	request.session.set_expiry(4)
	for friend in friends_l['friends']:
		if friend.user.username == receiver:
			messages.error(request, 'User is already your friend')
			return redirect('home')
	invite = Friend.objects.filter(sender=sender, receiver=User.objects.get(username=receiver), status='pending')
	if invite.exists():
		messages.error(request, 'Invite already sent')
		return redirect('home')
	invite = Friend.objects.filter(sender=User.objects.get(username=receiver), receiver=sender, status='pending')
	if invite.exists():
		messages.error(request, 'You already have an invite from this user')
		return redirect('home')

	Friend.objects.create(sender=sender, receiver=User.objects.get(username=receiver), status='pending')
	return redirect('home')


import logging

# Obtenez un objet logger
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Ceci est un message de débogage')
    logger.info('Ceci est un message d\'information')
    logger.warning('Ceci est un message d\'avertissement')
    logger.error('Ceci est un message d\'erreur')
    logger.critical('Ceci est un message critique')