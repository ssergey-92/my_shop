"""App signal functions."""

from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(
    sender: ModelBase, instance: User, created: bool, **kwargs,
) -> None:
    """Create Profile instance for user when received signal User post_save.

    Args:
        sender (ModelBase): User model
        instance (User): User instance
        created (bool): True if instance was created

    """
    if created:
        Profile.objects.create(user=instance, full_name=instance.first_name)
