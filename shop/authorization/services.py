from json import JSONDecodeError, loads as json_loads
from traceback import format_exc as tb_format_exc

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from .serializers import SignInSerializer, SignUpSerializer
from common.custom_logger import app_logger
from common.utils import server_error

class HandleAuthorization:
    """Class for authorization related endpoints"""

    _authentication_error = {"error": "Username or password is incorrect!"}
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

            auth_details = json_loads(request.body)
            auth_data = SignInSerializer(data=auth_details)
            auth_data.is_valid(raise_exception=True)
            user = authenticate(
                request,
                username=auth_data.data["username"],
                password=auth_data.data["password"],
            )
            if not user or not user.is_active:
                return Response(cls._authentication_error, cls._http_unsuccess)

            login(request, user)
            return Response(cls._successful_sign_in, cls._http_success)
        except (ValidationError, TypeError, JSONDecodeError) as exc:
            app_logger.debug(tb_format_exc())
            return Response({"error": str(exc)}, cls._http_unsuccess)
        except Exception:
            app_logger.error(tb_format_exc())
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
        except Exception:
            app_logger.error(tb_format_exc())
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

            sign_up_details = json_loads(request.body)
            sign_up_data = SignUpSerializer(data=sign_up_details)
            sign_up_data.is_valid(raise_exception=True)
            user = User.objects.create_user(**sign_up_data.data)
            login(request, user)
            return Response(cls._successful_sign_up, cls._http_success)
        except (
                ValidationError, TypeError, JSONDecodeError, IntegrityError
        ) as exc:
            app_logger.debug(tb_format_exc())
            return Response({"error": str(exc)}, cls._http_unsuccess)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, cls._http_unsuccess)
