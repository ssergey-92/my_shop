from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .custom_log import app_logger
from .services import HandleAuth

class SignInView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.body=}")
        response = HandleAuth.sign_in(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response

class SignOutView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.body=}")
        response = HandleAuth.sign_out(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response

class SignUpView(APIView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        app_logger.info(f"{request.method}, {request.path}, {request.body=}")
        response = HandleAuth.sign_up(request)
        app_logger.info(f"{response.status_code}, {response.data}")
        return response