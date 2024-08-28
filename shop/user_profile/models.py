"""App db models."""

from typing import Optional

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from common.custom_logger import app_logger

unavailable_profile_image = "Your profile photo is currently unavailable."
unavailable_file = "Your '{file_name}' is currently unavailable!"
several_profiles_error = "{total} profile found for user.id: {user_id}!"


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, null=False)
    unique_email = models.EmailField(unique=True, null=True)
    unique_phone = models.CharField(unique=True, null=True, max_length=12)

    def __str__(self) -> str:
        """String representation of Profile object.

        Returns:
            str: String representation of Profile object.

        """
        return f"Profile # {self.id} of user: {self.user.username}"

    def set_new_avatar(self, avatar_file: InMemoryUploadedFile) -> None:
        """Save or update avatar for profile.

        Args:
            avatar_file (InMemoryUploadedFile): Avatar image
        """

        alt = unavailable_file.format(file_name=avatar_file.name)
        if hasattr(self, "avatar"):
            self.avatar.custom_update(avatar_file, alt)
        else:
            Avatar.objects.create(profile=self, src=avatar_file, alt=alt)

    @classmethod
    def get_by_user_id_with_avatar(cls, user_id: int) -> Optional['Profile']:
        """Get profile with select related Avatar object.

        Args:
            user_id(int): User id to fetch Profile

        Returns:
            Optional[Profile]: User's profile

        """
        profile_with_avatar = (
            cls.objects.filter(user_id=user_id).
            select_related("avatar")
        )
        if len(profile_with_avatar) > 1:
            app_logger.error(
                several_profiles_error.format(
                    total=len(profile_with_avatar), user_id=user_id
                )
            )
            return None
        return profile_with_avatar[0]


def get_avatar_path(instance: "Avatar", filename: str) -> str:
    """Create avatar image saving path.

    Args:
        instance (Avatar): Avatar object
        filename (str): Avatar image filename

    Returns:
        str: Avatar image saving path

    """
    return "users/user_{user_id}/avatar/{filename}".format(
        user_id=instance.profile.user.id, filename=filename,
    )


class Avatar(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    src = models.ImageField(
        upload_to=get_avatar_path,
        max_length=150,
        blank=False,
        null=False,
    )
    alt = models.CharField(
        default=unavailable_profile_image,
        max_length=150,
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        """String representation of Avatar object.

        Returns:
            str: String representation of Avatar object.

        """
        return f"Avatar url: {self.src} of user: {self.profile.user.username}"

    def custom_update(self, src: InMemoryUploadedFile, alt: str) -> None:
        """Updating avatar image with saving new image in sys.

        Essential to save exactly avatar instance for saving image in sys.
        Avatar.objects.filter.update is not saving the above.

        Args:
            src (InMemoryUploadedFile): Avatar image
            alt (str): text representation in case can not access avatar image

        """
        self.src = src
        self.alt = alt
        self.save()

def update_user_password(user: User, new_password: str) -> None:
    """Update User password.

    Args:
        user (User): User object
        new_password (str): New password

    """
    user.set_password(new_password)
    user.save()
