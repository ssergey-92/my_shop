"""Module contains endpoints for app."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from .services import ProfileHandler


class FullProfileView(APIView):
    """Class FullProfileView. Require that user was signed in."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Get Profile details for user from request."""

        return ProfileHandler.get_own_profile(request.user.id)

    def post(self, request: Request) -> Response:
        """Update Profile details for user from request."""

        return ProfileHandler.update_own_profile(request.data, request.user)


class ProfilePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Update password for user from request."""

        response = ProfileHandler.update_own_password(
            request.data, request.user,
        )
        ProfileHandler.reset_user_session(request, request.user.id)
        return response


class ProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Update avatar image for user from request."""

        return ProfileHandler.update_own_avatar(
            request.FILES["avatar"], request.user.id,
        )
