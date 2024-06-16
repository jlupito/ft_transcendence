from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
import random
import math

# on vient creer un modele UserProfile qui surcharge le modele User préconçu.
# Il est recommandé de créer ce modele en debut de projet (pour le SQL), meme si
# on ne surcharge pas ce dernier.
class UserProfile(AbstractUser):
    elo = models.IntegerField(default=1000)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default2.png')
    def __str__(self):
        return self.username

class Match(models.Model):
    player1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='player2')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_match_from_game(cls, game_instance):
        player1_user=UserProfile.objects.get(username=game_instance.player1)
        player2_username = game_instance.player2
        player2_user, created = UserProfile.objects.get_or_create(username=player2_username)

        match = Match.objects.create(
            player1=player1_user,
            player2=player2_user,
            player1_score=game_instance.p1_score,
            player2_score=game_instance.p2_score
            )
        match.save()
        return match

    def __str__(self):
        return self.player1.username + ' vs ' + self.player2.username

class Friend(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.sender.username + ' -> ' + self.receiver.username + ' (' + self.status + ')'

#  ********************************** TOURNOIS **********************************

# classmethod est une methode de la classe, un peu comme static en c++ sur les objets
# on cree donc des methodes propres a la classe Tournament, a l' interieur de la def
# de la classe.
# On introduit ces fonctions internes avec @classmethod
# "cls" est comme "this" en C++ mais désigne la classe plutôt qu'un objet instancié
# La methode save() n' est pas une classe methode, on ne met donc pas @classmethod devant
# en revanche, elle s'applique a la classe elle-meme (cls), en capturant les arguments de
# type tuples et dictionnaire (*args et **kwargs), et vient enregistrer ce qui doit l'etre.
# Les * sont des conventions de Python.
# Il ne peut y avoir qu'une seule methode save() dans la classe, tout mettre dedans.

class Tournoi(models.Model):
    tourn_name = models.fields.CharField(max_length=30, blank=True)
    nb_players = models.fields.IntegerField(default=0)
    nb_matches = models.fields.IntegerField(default=0)
    nb_rounds = models.fields.IntegerField(default=0)
    l_matches = models.JSONField(default=dict)
    tourn_winner = models.fields.CharField(max_length=30, blank=True)

    @staticmethod
    def get_default_l_players():
        return []
    l_players = models.JSONField(default=dict)
    #l_players = models.JSONField(default=get_default_l_players)

    def get_default_l_matches_p_round():
        return {}
    l_matches = models.JSONField(default=get_default_l_matches_p_round)

    @classmethod
    def create_tournoi_from_tournament(cls, tourn_instance):
        def calculate_rounds(players):
            log2_nb_players = math.log2(players) # calcul log en base 2 de nb de joueurs
            rounds = math.ceil(log2_nb_players) # ceil arrondi au nb sup pour le nb de rounds
            return rounds
        
        tournament = Tournoi.objects.create(
            nb_players=len(tourn_instance.players),
            nb_rounds=calculate_rounds(cls.nb_players),
        )
        tournament.save()
        return tournament

    #def add_matches_in_tournament(cls, tourn_instance, game_instance):
    #    self.l_players.append(username)
    #    self.save()

    def add_match_tournament(self, round, match):
        if round not in self.l_matches:
            self.l_matches[round] = []
        self.l_matches[round].append(match)
        self.save()

    def __str__(self):
        return self.tourn_name
