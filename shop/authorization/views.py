"""Module contains endpoints for app."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .services import HandleAuthorization

class SignInView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Sign ip user."""
        return HandleAuthorization.sign_in(request)

class SignOutView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Sign out user from request."""

        return HandleAuthorization.sign_out(request)

class SignUpView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Sign up user."""

        return HandleAuthorization.sign_up(request)
