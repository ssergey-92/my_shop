"""Module contains endpoints for app."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from .services import HandleProfile

class FullProfileView(APIView):
    """Class FullProfileView. Require that user was signed in."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Get Profile details for user from request."""

        return HandleProfile.get_own_profile(request)

    def post(self, request: Request) -> Response:
        """Update Profile details for user from request."""

        return HandleProfile.update_own_profile(request)

class ProfilePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Update password for user from request."""

        return HandleProfile.update_own_password(request)

class ProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Update avatar image for user from request."""

        return HandleProfile.update_own_avatar(request)