"""App signal functions."""

from django.db.models.base import ModelBase
from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, Avatar
from common.custom_logger import app_logger
from common.utils import delete_file_from_sys


@receiver(post_save, sender=User)
def create_user_profile(
    sender: ModelBase, instance: User, created: bool, **kwargs,
) -> None:
    """Create Profile instance for user when received signal User post_save."""

    if kwargs.get('raw', False):
        app_logger.info(
            f"\n'create_user_profile' is disabled for loading fixture\n",
        )
        return

    if created:
        Profile.objects.create(user=instance, full_name=instance.first_name)


@receiver([pre_save, pre_delete], sender=Avatar)
def delete_avatar_image_from_sys(
    sender: ModelBase, instance: Avatar, *args, **kwargs,
) -> None:
    """Delete image of Avatar from sys.

    Delete image if signal is pre_delete or pre_save in case field "src" is
    updated or instance is deleted.

    """

    if kwargs.get('raw', False):
        app_logger.info(
            f"\n'delete_avatar_image_from_sys' is disabled for "
            f"loading fixture\n"
        )
        return

    app_logger.info(f"Caught signal {kwargs.get("signal")} for {instance}")

    # if new instance is created
    if not instance.id:
        return

    avatar = Avatar.objects.filter(id=instance.id).first()
    if not avatar:
        return

    if kwargs.get("signal") == pre_save:
        image_path = avatar.src.path
        if avatar.src.path == instance.src.path:
            return
    else:
         image_path = instance.src.path

    app_logger.info(f"Deleting old image for {instance}")
    delete_file_from_sys(image_path)