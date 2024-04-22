from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    elo = models.IntegerField(default=1000)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    def __str__(self):
        return self.user.first_name

# methode de classe pour avoir juste directement le nom du vainqueur ? superflu?
class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.player1.username + ' vs ' + self.player2.username

# classmethod pour accepter / rejeter les demandes d'ami ?
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

#  ********************************** AJOUTS **********************************

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
class Tournament(models.Model):

    tournament_name = models.fields.CharField(max_length=30, blank=True)
    players_number = models.fields.IntegerField(validators=[MinValueValidator(3), MaxValueValidator(8)])
    players_info = models.JSONField(default=dict)

    start_datetime = models.DateTimeField(default=timezone.now, editable=False)
    duration_time = models.DurationField(default=timedelta(minutes=4))
    end_datetime = models.DateTimeField(null=True, blank=True)

    registration_starttime = models.DateTimeField(default=timezone.now, editable=False)
    registration_duration = models.DurationField(default=timedelta(minutes=20))
    registration_deadline = models.DateTimeField(null=True, blank=True)

    @classmethod
    def generate_default_tournament_name(cls):
        last_tournament_number = cls.objects.count() + 1
        return f"Tournament {last_tournament_number}"
    @classmethod
    def calculate_default_endtime(cls):
        duration_time = cls.duration_time
        default_endtime = cls.start_datetime + duration_time
        return default_endtime
    @classmethod
    def calculate_tournament_registration_time(cls):
        registration_duration = cls.registration_duration
        registration_deadline = cls.registration_starttime + registration_duration
        return registration_deadline

    def save(self, *args, **kwargs):
        if not self.tournament_name:
            self.tournament_name = self.generate_default_tournament_name()
        if not self.end_datetime:
            self.end_datetime = self.calculate_default_endtime()
        if not self.end_datetime:
            self.registration_deadline = self.calculate_tournament_registration_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tournament_name
