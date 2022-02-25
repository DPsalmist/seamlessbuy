from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
#from store.models import Customer
from .models import Profile

#We want a user profile to be created for each new user rather than going through the admin
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

#saves the new user profile
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	instance.profile.save() 


