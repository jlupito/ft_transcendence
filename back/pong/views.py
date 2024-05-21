from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile, Match, Friend, Tournament
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from .forms import RegisterForm, LoginForm, localMatchForm
from .consumers import Game
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

def home(request):
	context = {}
	if (request.user.is_authenticated):
		avatar_url = UserProfile.objects.get(user=request.user).avatar.url
		users = UserProfile.objects.exclude(user=request.user)
		matches = match_history(request.user)
		stats = match_stats(request.user)
		friends = friends_list(request.user)
		invites = invites_list(request.user)
		invitees = invitees_list(request.user)
		context = {
			'users': users,
			'avatar_url': avatar_url,
			'invites': invites,
			'friends': friends,
			'matches': matches,
			'invitees': invitees,
			'stats' : stats
		}
	return render(request, 'page.html', context)

@login_required
def logout_view(request):
	logout(request)
	return redirect('home')

def match_stats(user):
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
    return {
        'won': won,
        'lost': lost,
        'wp': won_perc,
        'lp': lost_perc,
    }

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

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(UserProfile.objects.get(user=friend.receiver))
		else:
			profiles.append(UserProfile.objects.get(user=friend.sender))
	l = []
	for profile in profiles:
		l.append(profile)
	return l

def invites_list(user):
	invites = Friend.objects.filter(receiver=user, status='pending')
	l = []
	for invite in invites:
		l.append(invite.sender.username)
	return l

def invitees_list(user):
    invitees = Friend.objects.filter(sender=user, status='pending')
    l = []
    for invitee in invitees:
        l.append(invitee.receiver.username)
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
		if user_profile.avatar.url != "/media/avatars/default2.png":
			user_profile.avatar.delete()
		profile_picture.name = user.username
		user_profile.avatar = profile_picture
		user_profile.save()
	user.save()
	return redirect('home')

def handle_invite(request):
	if request.method == 'GET':
		return redirect('home')
	sender = request.POST.get('invite')
	receiver = request.user
	status = request.POST.get('status')
	inv = Friend.objects.filter(sender=User.objects.get(username=sender), receiver=receiver).first()
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
	for friend in friends_l:
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

def friend_profile(request, friend_id):
    friend = User.objects.get(id=friend_id)
    if friend:
        avatar_url = UserProfile.objects.get(user=friend).avatar.url
        users = UserProfile.objects.exclude(user=friend)
        matches = match_history(friend)
        stats = match_stats(friend)
        friends = friends_list(friend)
        invites = invites_list(friend)
        invitees = invitees_list(friend)
        context = {
            'users': users,
            'avatar_url': avatar_url,
            'invites': invites,
            'friends': friends,
            'matches': matches,
            'invitees': invitees,
            'stats' : stats
        }
        return render(request, 'friend_profile.html', context)
    else:
        return HttpResponse('<h1>Friend not found</h1>')

# never_cache est un décorateur qui indique au navigateur de ne pas mettre en cache la reponse
# à cette view, a chaque fois que la view est appelee, la verification aura lieu.
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
	intra_email = response.json()['email']
	# intra_picture = response.json()['image']['link']
	intra_url = response.json()['image']['link']
	user = User.objects.filter(username=intra_login).first()
	if user is None:
		user = User.objects.create_user(username=intra_login, first_name=intra_login, email=intra_email)
		UserProfile.objects.create(user=user)
	response_pic = requests.get(intra_url)
	img_temp = NamedTemporaryFile(delete=True)
	img_temp.write(response_pic.content)
	img_temp.flush()
	user_profile = UserProfile.objects.get(user=user)
	if user_profile.avatar.url != "/media/avatars/default2.png":
		user_profile.avatar.delete()
	intra_url.name = user.username
	user_profile.avatar = intra_url
	user_profile.save()
	user.save()
	login(request, user)
	return redirect('home')

# *********************************** MATCHS ***********************************

def create_local_game(request):
	if request.method == 'POST':
		localform = localMatchForm(request.POST)

		if localform.is_valid():
			player1 = request.user
			player2 = localform.cleaned_data['local_player2_name']

			if player2:
				new_game = Game.objects.create(player1=player1, player2=player2)
				new_game.save()
				return redirect('home')
			else:
				messages.error(request, "Player 2 name cannot be empty.")
				localform=localMatchForm()
	return redirect('home')

# *********************************** LOGIN ***********************************

# Utilisation des fonctions is_valide(), authenticate() avec "is not None"
# fonctions et outils de Python/Django
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
				messages.success(request, 'Connected!')
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

import logging

# Obtenez un objet logger
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Ceci est un message de débogage')
    logger.info('Ceci est un message d\'information')
    logger.warning('Ceci est un message d\'avertissement')
    logger.error('Ceci est un message d\'erreur')
    logger.critical('Ceci est un message critique')


# *********************************** TOURNOIS ***********************************

# Dans cette fonction on créée un nouvel objet de type Tournament, en appelant la
# classe, et esnuite le gestionnaire d' objets associé a celle-ci. Les objets ont
# comme classmethod la fontion create() deja fournie par Django, elle prend en
# argument les champs attributs de la classe et renvoie un nouvel objet.
# on retourne ensuite au home, car SPA.

#  ajouter l'info de player1 qui lance ?
def create_tournament(request):
	if request.method == 'GET':
		return redirect('home')
	new_tournament = Tournament.objects.create()
	initiating_player = request.user.username
	new_tournament.players_info[0] = initiating_player
	new_tournament.save()
	return redirect('home')

# Dans ce code :
# Nous récupérons le nom du nouveau joueur à partir de la requête POST.
# Ensuite, nous récupérons l'instance du tournoi à l'aide de :
# Tournament.objects.get(tournament_name=tournament_name).
# Nous accédons au dictionnaire players_info de ce tournoi.
# Nous ajoutons le nouveau joueur au dictionnaire en utilisant une nouvelle
# clé qui est la longueur actuelle du dictionnaire plus un.
# Nous sauvegardons ensuite le tournoi pour enregistrer les modifications.
# ATTENTION aux infos contenues dans la requete POST (playername doit exister)
def add_player_in_tournament(request, tournament_name):
	if request.method == 'GET':
		return redirect('home')
	elif request.method == 'POST':
		newplayer_name = request.POST.get("playername")
		tournament = Tournament.objects.get(tournament_name=tournament_name)
		players_info = tournament.players_info
		players_info[newplayer_name] = len(players_info) + 1
		tournament.save()
	return redirect('home')
