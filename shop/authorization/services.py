from json import JSONDecodeError, loads as json_loads
from traceback import print_exception as tb_print_exception
from typing import Optional

from django.contrib.auth import authenticate, login, logout
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from .models import create_new_user
from .serializers import SignInSerializer, SignUpSerializer
from common.custom_logger import app_logger
from common.utils import server_error

class HandleAuthorization:
    """Class for authorization related endpoints"""

    _authentication_error = {"error": "Username or password is incorrect!"}
    _existed_user_error = {"error": "Username is selected by other user!"}
    _parsing_error = {
        "error": "Parsing error while parsing query string from POST request!",
    }
    _sign_out_error = {"error": "Login first before logout!"}
    _sign_in_error = {"error": "Logout first before login!"}
    _sign_up_error = {"error": "Logout first to create new account!"}

    _successful_sign_in = {"msg": "Successfully logged in!"}
    _successful_sign_out = {"msg": "Successful logout!"}
    _successful_sign_up = {"msg": "New account was successfully created!"}

    _http_success = HTTP_200_OK
    _http_unsuccess = HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def sign_in(cls, request: Request) -> Response:
        """Handle logic for signing in user.

        Check that user is not authenticates, parse and validate data from
        request and check user's credential. Sign in user if all checks are
        passes. Return corresponding response.

        """
        try:
            if request.user.is_authenticated:
                return Response(cls._sign_in_error, cls._http_unsuccess)

            data = cls._get_query_params_from_post_request(request)
            if not data:
                return Response(cls._parsing_error, cls._http_unsuccess)

            sign_in_data = SignInSerializer(data=data)
            if not sign_in_data.is_valid():
                validation_error = {"error": sign_in_data.errors}
                return Response(validation_error, cls._http_unsuccess)


            user = authenticate(
                    request, username=data["username"], password=data["password"],
            )

            if not user or not user.is_active:
                return Response(cls._authentication_error, cls._http_unsuccess)
            login(request, user)
            return Response(cls._successful_sign_in, cls._http_success)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, cls._http_unsuccess)

    @classmethod
    def sign_out(cls, request: Request) -> Response:
        """Handle logic for signing out user.

        Check that user is authenticates and then sign out.
        Return corresponding response.

        """
        try:
            if request.user.is_authenticated:
                user_basket = request.session.get("basket", {})
                logout(request)
                request.session["basket"] = user_basket
                request.session.save()
                return Response(cls._successful_sign_out, cls._http_success)
            else:
                return Response(cls._sign_out_error, cls._http_unsuccess)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, cls._http_unsuccess)

    @classmethod
    def sign_up(cls, request: Request) -> Response:
        """Handle logic for signing up user.

        Check that user is not authenticates, parse and validate data from
        request. Sign up and sign in user if all checks are passes.
        Return corresponding response.

        """
        try:
            if request.user.is_authenticated:
                return Response(cls._sign_up_error, cls._http_unsuccess)

            data = cls._get_query_params_from_post_request(request)
            if not data:
                return Response(cls._parsing_error, cls._http_unsuccess)

            sign_up_data = SignUpSerializer(data=data)
            if not sign_up_data.is_valid():
                validation_error = {"error": sign_up_data.errors}
                return Response(validation_error, cls._http_unsuccess)

            sign_up_data.validated_data["first_name"] = (
                sign_up_data.validated_data.pop("name")
            )
            user = create_new_user(sign_up_data.validated_data)
            if not user:
                return Response(cls._existed_user_error, cls._http_unsuccess)
            login(request, user)
            return Response(cls._successful_sign_up, cls._http_success)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, cls._http_unsuccess)

    @staticmethod
    def _get_query_params_from_post_request(request: Request) -> Optional[dict]:
        """Get query string params from POST request."""

        try:
            parsed_data = json_loads(request.body)
            app_logger.debug(f"{parsed_data=}")
            return parsed_data
        except (TypeError, JSONDecodeError) as exc:
            app_logger.error(tb_print_exception(exc))
