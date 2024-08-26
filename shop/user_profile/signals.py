from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(
        sender: ModelBase, instance: User, created: bool, **kwargs,
) -> None:
    if created:
        Profile.objects.create(user=instance, full_name=instance.first_name)