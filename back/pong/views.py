from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Match, Friend
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from .forms import RegisterForm, LoginForm
from django.core.files.base import ContentFile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

def home(request):
	context = {}
	user = request.user
	if (request.user.is_authenticated):
		context['id'] = user.id
		context['user'] = user
		context['username'] = user.username
		context['avatar'] = user.avatar.url
		context['users'] = UserProfile.objects.all().exclude(username=user.username)
		context['matches'] = match_history(user)
		context['friends'] = friends_list(user)
		context['stats'] = match_stats(user)
		# context['invites'] = invites_list(user)
		# context['invitees'] = invitees_list(user)
	return render(request, 'page.html', context)


# *********************************** LOGIN ***********************************

# Utilisation des fonctions is_valide(), authenticate() avec "is not None"
# fonctions et outils de Python/Django
def sign_in(request):
	if request.method == 'POST':
		loginform = LoginForm(request.POST)

		if loginform.is_valid():
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

def register(request):
	if request.method == 'POST':
		registerform = RegisterForm(request.POST)
		if registerform.is_valid():
			username=registerform.cleaned_data['username']
			if UserProfile.objects.filter(username=username).exists():
				messages.error(request, 'This username is already used!')
				return redirect('home')
			mdp=registerform.cleaned_data['password']
			email=registerform.cleaned_data['email']
			if UserProfile.objects.filter(email=email).exists():
				messages.error(request, 'This email is already in use...')
				return redirect('home')
			new_user = UserProfile.objects.create_user(username=username, password=mdp, email=email)
			login(request, new_user)
			messages.success(request, 'Account created successfully!')
			return redirect('home')
		else:
			messages.error(request, 'Invalid form data')
	else:
		registerform = RegisterForm()
	return redirect('home')

def update_profile(request):
	if request.method == 'GET':
		return redirect('home')
	username = request.POST.get('username')
	profile_picture = request.FILES.get('profile_picture')
	if (UserProfile.objects.filter(username=username).exists() and username != request.user.username):
		messages.error(request, 'Username already taken')
		return redirect('home')
	user = request.user
	user.username = username
	if (profile_picture is not None):
		validate = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
		try:
			validate(profile_picture)
		except ValidationError as e:
			messages.error(request, 'Invalid file type')
			return redirect('home')
		if user.avatar.url != "/media/avatars/default2.png":
			user.avatar.delete()
		profile_picture.name = user.username
		user.avatar = profile_picture
	user.save()
	return redirect('home')

@login_required
def logout_view(request):
	logout(request)
	messages.success(request, 'You are logged out!')
	return redirect('home')

def save_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return ContentFile(response.content)
    else:
        return None

# never_cache est un décorateur qui indique au navigateur de ne pas mettre en cache la reponse
# à cette view, a chaque fois que la view est appelee, la verification aura lieu.
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
	user = UserProfile.objects.filter(username=intra_login).first()
	if user is None:
		user = UserProfile.objects.create_user(username=intra_login, email=intra_email)
		if (picture is not None):
			if user.avatar.url != "/media/avatars/default2.png":
				user.avatar.delete()
			picture.name = user.username
			user.avatar.save('intra_img.jpg', picture, save=True)
	login(request, user)
	messages.success(request, 'You are now logged in!')
	return redirect('home')

# *********************************** MATCHS ***********************************

def match_history(user):
	user = user.username
	matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
	l = []
	for match in matches:
		time = match.timestamp.strftime('%d/%m/%Y %H:%M')
		if match.player1 == user:
			user_score = match.player1_score
			opponent_score = match.player2_score
			opponent_name = match.player2
		else:
			user_score = match.player2_score
			opponent_score = match.player1_score
			opponent_name = match.player1
		match_result = {
        "opponent_name": opponent_name,
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

def match_stats(user):
	profiles = UserProfile.objects.filter(username=user)
	userProfile = None
	if profiles.exists():
		userProfile = profiles.first()
	else:
		return None
	won = userProfile.matches_won
	lost = userProfile.matches_lost
	total = won + lost
	tourn = userProfile.tourn_won
	if total == 0:
		won_perc = 0
		lost_perc = 0
	else:
		won_perc = round(won / total * 100)
		lost_perc = round(lost / total * 100)
	matches_hist = match_history(user)
	stats = {
		'won': won,
		'lost': lost,
		'wp': won_perc,
		'lp': lost_perc,
		'tourn': tourn,
		'id': userProfile.id,
		'matches': matches_hist,
    }
	return stats

# *********************************** FRIENDS ***********************************

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(UserProfile.objects.get(username=friend.receiver))
		else:
			profiles.append(UserProfile.objects.get(username=friend.sender))
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
	status = request.POST.get('friend_status')
	print('Status from frnt is :', status)
	inv = Friend.objects.filter(sender=UserProfile.objects.get(username=sender), receiver=receiver).first()
	print("inv:", inv)
	if inv:
		inv.status = status
		print('COUCOU', inv.status)
		inv.save()
	userpro_receiver = UserProfile.objects.get(username=receiver.username)
	channel_layer = get_channel_layer()
	data = {
			'type': 'friends_requests_update',
			'friend_id': userpro_receiver.id,
			'friend_avatar': userpro_receiver.avatar.url,
			'friend_is_online': userpro_receiver.is_online,
			'friend_username': userpro_receiver.username,
		}
	async_to_sync(channel_layer.group_send)(
		"friends_requests", data
		)
	return redirect('home')

@login_required
def send_invite(request):
	if request.method == 'GET':
		return redirect('home')
	receiver = request.POST.get('receiver')
	sender = request.user
	friends_l = friends_list(sender)
	request.session.set_expiry(4)
	for friend in friends_l['friends']:
		if friend.username == receiver:
			messages.error(request, 'User is already your friend')
			return redirect('home')
	invite = Friend.objects.filter(sender=sender, receiver=UserProfile.objects.get(username=receiver), status='pending')
	if invite.exists():
		messages.error(request, 'Invite already sent')
		return redirect('home')
	invite = Friend.objects.filter(sender=UserProfile.objects.get(username=receiver), receiver=sender, status='pending')
	if invite.exists():
		messages.error(request, 'You already have an invite from this user')
		return redirect('home')
	Friend.objects.create(sender=sender, receiver=UserProfile.objects.get(username=receiver), status='pending')
	friend_request_sender_profile=UserProfile.objects.get(username=sender)
	channel_layer = get_channel_layer()
	data =	{
			'type': 'new_friend_request',
			'friend_id': friend_request_sender_profile.id,
			'friend_avatar': friend_request_sender_profile.avatar.url,
			'friend_is_online': friend_request_sender_profile.is_online,
			'friend_username': friend_request_sender_profile.username
		}
	async_to_sync(channel_layer.group_send)(
		"friends_requests", data
	)
	return redirect('home')

logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Ceci est un message de débogage')
    logger.info('Ceci est un message d\'information')
    logger.warning('Ceci est un message d\'avertissement')
    logger.error('Ceci est un message d\'erreur')
    logger.critical('Ceci est un message critique')
