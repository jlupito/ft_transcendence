from django.db import models
from django.contrib.auth.models import User

class Friend(models.Model):
	STATUS_CHOICES = (
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('rejected', 'Rejected'),
	)
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	USERNAME_FIELD = "username"
	REQUIRED_FIELDS = ['email', 'password']

	@property
	def is_anonymous(self):
		"""
		Always return False. This is a way of comparing User objects to
		anonymous users.
		"""
		return False

	@property
	def is_authenticated(self):
		"""
		Always return False. This is a way of comparing User objects to
		anonymous users.
		"""
		return True

	def __str__(self):
		return self.sender.username + ' -> ' + self.receiver.username + ' (' + self.status + ')'