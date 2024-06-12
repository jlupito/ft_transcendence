from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
import math
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # elo = models.IntegerField(default=1000)
    tourn_won = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    matches_lost = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default2.png')
    def __str__(self):
        return self.user.first_name

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_match_from_game(cls, game_instance):
        player1_user=User.objects.get(username=game_instance.player1)
        player2_username = game_instance.player2
        player2_user, created = User.objects.get_or_create(username=player2_username)

        match = Match.objects.create(
            player1=player1_user,
            player2=player2_user,
            player1_score=game_instance.p1_score,
            player2_score=game_instance.p2_score
            )
        user1 = UserProfile.objects.get(user=player1_user)
        user2 = UserProfile.objects.get(user=player2_user)
        if game_instance.p1_score > game_instance.p2_score:
                user1.matches_won += 1
                user2.matches_lost += 1
        elif game_instance.p1_score < game_instance.p2_score:
                user1.matches_lost += 1
                user2.matches_won += 1
        print("nombre de wins", user1.matches_won)
        print("nombre de wins", user1.matches_won)
        user1.save()
        user2.save()
        match.save()
        return match

    def __str__(self):
        return self.player1.username + ' vs ' + self.player2.username
    
@receiver(post_save, sender=Match)
def update_stats(sender, instance, created, **kwargs):
    if created:
        for user in [instance.player1, instance.player2]:
            from .consumers import StatsConsumer
            consumer = StatsConsumer.instances.get(user.id)
            if consumer:
                from .views import match_stats
                stats = match_stats(user)  # replace with your function to calculate stats
                async_to_sync(consumer.send_stats)(stats)

class Friend(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
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
    tourn_winner = models.fields.CharField(max_length=30, blank=True)
    nb_players = models.fields.IntegerField(default=0)
    nb_rounds = models.fields.IntegerField(default=0)
    l_players = models.JSONField(default=list)
    l_matches = models.JSONField(default=dict)

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

    @classmethod
    def add_matches_in_tournament(cls, round, game_instance):
        if round not in cls.l_matches:
            cls.l_matches[round] = []
        cls.l_matches[round].append({
            'player1': game_instance.player1,
            'player2': game_instance.player2,
            'p1_score': game_instance.p1_score,
            'p2_score': game_instance.p2_score
        })
        cls.save()

    def __str__(self):
        return self.tourn_name
