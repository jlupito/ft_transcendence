from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import UserProfile, Match, Friend, Tournament
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from .forms import RegisterForm, localMatchForm
from django.contrib.auth.forms import AuthenticationForm
from .consumers import Game
from tempfile import NamedTemporaryFile
from django.core.files.base import ContentFile
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

#User = get_user_model()

def home(request):
	context = {}
	user = request.user
	if (request.user.is_authenticated):
		context['id'] = user.id
		context['user'] = user
		context['username'] = user.username
		if user.avatar:
			context['avatar'] = user.avatar.url
		else:
			context['avatar'] = "avatars/default2.png"
		context['users'] = UserProfile.objects.all().exclude(username=user.username)
		context['matches'] = match_history(user)
		context['invites'] = invites_list(user)
		context['friends'] = friends_list(user)
		context['stats'] = match_stats(user)
		context['invitees'] = invitees_list(user)
	return render(request, 'page.html', context)

# *********************************** LOGIN ***********************************

# Utilisation des fonctions is_valide(), authenticate() avec "is not None"
# fonctions et outils de Python/Django
def sign_in(request):
	#loginform = AuthenticationForm()
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			request.session['user_id'] = user.id
			return redirect('verify-view')
			#login(request, user)
			#messages.success(request, 'You are now logged in!')
		else:
			messages.error(request, 'Invalid username or password')
	#else:
		#loginform=LoginForm()
	return redirect('home')

# Lancer la creation d'un compte
def register(request):
	#registerform = RegisterForm(request.POST)
	if request.method == 'POST':
		#if registerform.is_valid():
			#username=registerform.cleaned_data['username']
			username = request.POST.get('username')
			if UserProfile.objects.filter(username=username).exists():
				messages.error(request, 'This username is already used!') # Modifier la posiiton du message de front
				# registerform = RegisterForm() # ne change rien == maintenir le form ?
				return redirect('home')
			mdp = request.POST.get('password')
			email = request.POST.get('email')
			if UserProfile.objects.filter(email=email).exists():
				messages.error(request, 'This email is already in use...')
				return redirect('home')
			new_user = UserProfile.objects.create_user(username=username, password=mdp, email=email, first_name=username)
			login(request, new_user)
			messages.success(request, 'Account created successfully!')
			#return redirect('home')
		#else:
			#messages.error(request, 'Invalid form data')
	#else:
		#registerform = RegisterForm()
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
	if (UserProfile.objects.filter(username=username).exists() and username != request.user.username):
		messages.error(request, 'Username already taken')
		return redirect('home')
	user = request.user
	user.username = username
	if (profile_picture is not None):
		user.avatar.delete()
		profile_picture.name = user.username
		user.avatar = profile_picture
	user.save()
	return redirect('home')


@login_required
def logout_view(request):
	logout(request)
	return redirect('home')

# class StatsAPI(APIView):
#     def get(self, request):
#         if request.user.is_authenticated:
#             stats = match_stats(request.user)
#             return Response(stats, status=status.HTTP_200_OK)
#         else:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
		
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

def friend_match(request, friend_name):
    friend_user = UserProfile.objects.get(username=friend_name)
    fmatches = match_history(friend_user)
    return render(request, 'friend_match', {'matches': fmatches})

#@login_required
def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(friend.receiver)
		else:
			profiles.append(friend.sender)
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

def handle_invite(request):
	if request.method == 'GET':
		return redirect('home')
	sender = request.POST.get('invite')
	receiver = request.user
	status = request.POST.get('status')
	inv = Friend.objects.filter(sender=UserProfile.objects.get(username=sender), receiver=receiver).first()
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
	token_url = 'https://api.intra.42.fr/oauth/token'
	data = {
		'grant_type': 'authorization_code',
		'client_id': uid,
		'client_secret': secret,
		'code': code,
		'redirect_uri': 'https://localhost:8000/oauth',
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
			picture.name = user.username
			user.avatar.save('intra_img.jpg', picture, save=True)
	login(request, user)
	messages.success(request, 'You are now logged in!')
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
