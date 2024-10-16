"""Handle business logic for app endpoints"""

from traceback import format_exc as tb_format_exc

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .models import update_user_password, Profile
from .serializers import (
    ChangePasswordSerializer,
    InProfileSerializer,
    OutProfileSerializer,
)

from common.custom_logger import app_logger
from common.validators import validate_image_src
from common.utils import server_error


class ProfileHandler:
    """Class for handling logic for Profile related endpoints"""

    _invalid_password_error = "Invalid user password!"
    _successful_psw_update = {"msg": "Password was successfully changed."}
    _successful_avatar_update = {"msg": "Avatar was successfully changed."}
    _http_bad_request = HTTP_400_BAD_REQUEST
    _http_success = HTTP_200_OK
    _http_internal_error = HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def get_own_profile(cls, user_id: int) -> Response:
        """Handle logic for getting user's details.

        Check that profile is existed for user from request and return
        corresponding response.

        """
        try:
            profile = Profile.get_by_user_id_with_prefetch(user_id)
            return Response(
                OutProfileSerializer(profile).data, cls._http_success,
            )
        except Profile.DoesNotExist as exc:
            return Response({"error": str(exc)}, cls._http_bad_request)
        except (Profile.MultipleObjectsReturned, Exception) as exc:
            app_logger.error(tb_format_exc())
            return Response(server_error, cls._http_internal_error)

    @classmethod
    def update_own_avatar(
        cls, avatar_file: InMemoryUploadedFile, user_id: int,
    ) -> Response:
        """Handle logic for updating user's avatar.

        Validate request data, check that profile is existed for user from
        request and update user's avatar in case all checks passed.
        Return corresponding response.

        """
        try:
            validation_error = validate_image_src(avatar_file)
            if validation_error:
                return Response(validation_error, cls._http_bad_request)

            profile = Profile.get_by_user_id_with_prefetch(user_id)
            profile.set_new_avatar(avatar_file)
            return Response(cls._successful_avatar_update, cls._http_success)
        except Profile.DoesNotExist as exc:
            return Response({"error": str(exc)}, cls._http_bad_request)
        except (Profile.MultipleObjectsReturned, Exception) as exc:
            app_logger.error(tb_format_exc())
            return Response(server_error, cls._http_internal_error)

    @classmethod
    def update_own_profile(
        cls, profile_details: dict, user_id: int
    ) -> Response:
        """Handle logic for updating user profile details.

        Validate request data, check that profile is existed for user from
        request and update profile in case all checks passed.
        Return corresponding response.

        """
        try:
            profile_details.pop("avatar")
            profile_data = InProfileSerializer(data=profile_details)
            profile_data.is_valid(raise_exception=True)
            profile = Profile.custom_update(profile_data.data, user_id)
            return Response(
                OutProfileSerializer(profile).data, cls._http_success,
            )
        except (ValidationError, IntegrityError, Profile.DoesNotExist) as exc:
            app_logger.debug(tb_format_exc())
            return Response({"error": str(exc)}, cls._http_bad_request)
        except (Profile.MultipleObjectsReturned, Exception) as exc:
            app_logger.error(tb_format_exc())
            return Response({"error": exc}, cls._http_internal_error)

    @classmethod
    def update_own_password(
        cls, password_details: dict, user: User,
    ) -> Response:
        """Handle logic for updating user password.

        Validate request data, check current password for user from request
        and update password and session in case all checks passed.
        Return corresponding response.

        """
        try:
            password_data = ChangePasswordSerializer(data=password_details)
            password_data.is_valid(raise_exception=True)
            user = authenticate(
                username=user.username,
                password=password_data.data["current_password"],
            )
            if not user:
                raise ValidationError(cls._invalid_password_error)
            update_user_password(user, password_data.data["new_password"])
            return Response(cls._successful_psw_update, cls._http_success)
        except ValidationError as exc:
            app_logger.debug(tb_format_exc())
            return Response({"error": str(exc)}, cls._http_bad_request)
        except Exception as exc:
            app_logger.error(exc)
            return Response(server_error, cls._http_internal_error)

    @staticmethod
    def reset_user_session(request: Request, user_id: int) -> None:
        """Reset session details for user.

        Get updated User for login and move bucket from old to new session.
        """

        user_basket = request.session.get("basket", {})
        logout(request)
        login(request, User.objects.get(id=user_id))
        request.session["basket"] = user_basket
        app_logger.info(f"Session was reset for {user_id=}")
