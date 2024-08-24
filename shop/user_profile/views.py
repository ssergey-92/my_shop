from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from .services import HandleProfile
from .custom_log import app_logger

class FullProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.data=}")
        response = HandleProfile.get_own_profile(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response

    def post(self, request: Request) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.data=}")
        response = HandleProfile.update_own_profile(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response

class ProfilePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.data=}")
        response = HandleProfile.update_own_password(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response

class ProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.data=}")
        response = HandleProfile.update_own_avatar(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response