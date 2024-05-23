from users.models import UserProfile
from .models import DoubleAuth
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=UserProfile)
def post_save_generate_code(sender, instance, created, **kwargs):
	if created:
		DoubleAuth.objects.create(user=instance)