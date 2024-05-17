from django.shortcuts import redirect, render
from users.models import UserProfile
from friends.views import friends_list, invites_list, invitees_list
from .models import Match, Tournament
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LocalMatchForm
from .consumers import Game

@login_required
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
	return render(request, 'pong/home.html', context)

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

import logging

# Obtenez un objet logger
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Ceci est un message de débogage')
    logger.info('Ceci est un message d\'information')
    logger.warning('Ceci est un message d\'avertissement')
    logger.error('Ceci est un message d\'erreur')
    logger.critical('Ceci est un message critique')

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
