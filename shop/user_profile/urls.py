"""App URl configuration module."""

from django.urls import path

from .apps import UserProfileConfig
from .views import FullProfileView, ProfileAvatarView, ProfilePasswordView


app_name = UserProfileConfig.name

urlpatterns = [
    path(
        "profile/password",
        ProfilePasswordView.as_view(),
        name="profile_password"
    ),
    path(
        "profile/avatar",
        ProfileAvatarView.as_view(),
        name="profile_avatar"
    ),
    path("profile", FullProfileView.as_view(), name="profile_full"),
]
