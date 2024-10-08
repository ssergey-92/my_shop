"""App db models."""

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

unavailable_profile_image = "Your profile photo is currently unavailable."


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, null=False)
    unique_email = models.EmailField(unique=True, null=True)
    unique_phone = models.CharField(unique=True, null=True, max_length=12)

    def __str__(self) -> str:
        """String representation of Profile object."""

        return f"Profile # {self.id} of user: {self.user.username}"

    def set_new_avatar(self, avatar_file: InMemoryUploadedFile) -> None:
        """Save or update avatar for profile."""

        if hasattr(self, "avatar"):
            self.avatar.custom_update(avatar_file, unavailable_profile_image)
        else:
            Avatar.objects.create(
                profile=self, src=avatar_file, alt=unavailable_profile_image,
            )

    @classmethod
    def get_by_user_id_with_prefetch(cls, user_id: int) -> "Profile":
        """Get profile with select related Avatar object."""

        return (
            cls.objects.
            select_related("avatar").
            get(user_id=user_id)
        )

    @classmethod
    def custom_update(cls, update_details: dict, user_id) -> "Profile":
        """Update Profile as per update_details and return it."""

        profile = cls.objects.get(user_id=user_id)
        for field, value in update_details.items():
            setattr(profile, field, value)
        profile.save()
        return profile


def get_avatar_path(instance: "Avatar", filename: str) -> str:
    """Create avatar image saving path."""

    return "users/user_{user_id}/avatar/{filename}".format(
        user_id=instance.profile.user.id, filename=filename,
    )


class Avatar(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="avatar",
    )
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
        """String representation of Avatar object."""

        return f"Avatar url: {self.src} of user: {self.profile.user.username}"

    def custom_update(self, src: InMemoryUploadedFile, alt: str) -> None:
        """Updating avatar image with saving new image in sys.

        Essential to save exactly avatar instance for saving image in sys.
        Avatar.objects.filter.update is not saving the above.

        """
        self.src = src
        self.alt = alt
        self.save()


def update_user_password(user: User, new_password: str) -> None:
    """Update User password."""

    user.set_password(new_password)
    user.save()
