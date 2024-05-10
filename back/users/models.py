from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	#elo = models.IntegerField(default=1000)
	avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
	#USERNAME_FIELD = "user.get(username)"
	#REQUIRED_FIELDS = ['username', 'email', 'password']

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
		return self.user.first_name


#class UserProfile(AbstractBaseUser):
#	user = models.OneToOneField(User, on_delete=models.CASCADE)
#	#elo = models.IntegerField(default=1000)
#	username = models.CharField(max_length = 25)
#	avatar = models.ImageField(upload_to='avatars/', default='avatars/default2.png')
#	USERNAME_FIELD = 'username'
#	#REQUIRED_FIELDS = ['email', 'password']

#	def __str__(self):
#		return self.user.first_name
