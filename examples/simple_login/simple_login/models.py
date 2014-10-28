from django.db import models
from django.contrib.auth.models import User
import tauth.models

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.ForeignKey(tauth.models.Role, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

models.signals.post_save.connect(create_user_profile, sender=User)

