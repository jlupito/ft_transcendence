from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, logout
from .models import UserProfile, Match, Friend, User, Tournament
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from forms import RegularLogin

def home(request):
	context = {}
	if (request.user.is_authenticated):
		avatar_url = UserProfile.objects.get(user=request.user).avatar.url
		users = UserProfile.objects.exclude(user=request.user)
		matches = match_history(request.user)
		friends = friends_list(request.user)
		invites = invites_list(request.user)
		context = {
			'users': users,
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
# Ajouter une limitation de nombre de joueurs dans cette fonction cas échéant
# Ai-je besoin de prendre en parametre le tournament_name si un seul tournoi
# autorisé en cours ?
# Et la limite de temps ? A quel moment ?

# *********************************** MATCHS ***********************************

def create_match(request):
	if request.method == 'GET':
		return redirect ('home')
	player1_name = request.POST.get("player1_name")
	player2_name = request.POST.get("player2_name")

	player_1 = UserProfile.objects.get(username = player1_name)
	player_2 = UserProfile.objects.get(username = player2_name)
	new_match = Match.objects.create(
		player_1=player_1,
		player_2=player_2
		)
	new_match.save()
	return redirect ('home')

# *********************************** LOGIN ***********************************

def login_view(request):
	if request.method == 'GET':
		return redirect ('home')
	else:
		loginform = RegularLogin(request.POST)
		if loginform.is_valid():
			# deux cas, new_account ou login
			username=loginform.cleaned_data['username']
			email=loginform.cleaned_data['email']
			mdp=loginform.cleaned_data['mdp']
			# Ajout de code pour enregistrer les infos dans la DB et parser
			# les infos de connexion
	return render(request, 'home', {'loginform': loginform})
