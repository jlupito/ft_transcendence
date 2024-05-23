from django.db import models
from users.models import UserProfile
import random

class DoubleAuth(models.Model):
	user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
	number = models.CharField(max_length=5, blank=True)
	
	def __str__(self):
		return str(self.number)
	
	#creer des code aleatoire a 5 chiffres pour la 2FA
	#code attribuer a une connection d'un utilisateur
	def save(self, *args, **kwargs):
		num_list = [x for x in range(10)]
		code_items = []
		for i in range(5):
			num = random.choice(num_list)
			code_items.append(num)
		code_string = ''.join(str(item) for item in code_items)
		self.number = code_string
		super().save(*args, **kwargs)