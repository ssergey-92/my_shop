"""App configuration module."""

from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_profile"

    def ready(self) -> None:
        """Activate signals for app."""

        from . import signals
