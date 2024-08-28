"""Handle business logic for app endpoints"""

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.db import IntegrityError
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
from .validators import validate_avatar_src
from common.custom_logger import app_logger
from common.utils import delete_file_from_sys


class HandleProfile:
    """Class for handling logic for Profile related endpoints"""

    _invalid_password_error = {"error": "Invalid user password!"}
    _profile_error = {"error": "User profile is not found!"}
    _successful_psw_update = {"msg": "Password was successfully changed."}
    _successful_avatar_update = {"msg": "Avatar was successfully changed."}
    _http_bad_request = HTTP_400_BAD_REQUEST
    _http_success = HTTP_200_OK
    _http_internal_error = HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def get_own_profile(cls, request: Request) -> Response:
        """ Handle logic for getting user's details.

        Check that profile is existed for user from request and return
        corresponding response.

        Args:
            request (Request): Http request object.

        Returns:
            response (Response): Http response object.

        """

        profile = Profile.get_by_user_id_with_avatar(request.user.id)
        if profile:
            try:
                return Response(
                    OutProfileSerializer(profile).data, cls._http_success,
                )
            except AttributeError as exc:
                app_logger.error(f"Error while serializing Profile: {exc}")
        else:
            app_logger.error(cls._profile_error)
        return Response(cls._profile_error, cls._http_internal_error)

    @classmethod
    def update_own_avatar(cls, request: Request) -> Response:
        """ Handle logic for updating user's avatar.

        Validate request data, check that profile is existed for user from
        request and update user's avatar in case all checks passed.
        Return corresponding response.

        Args:
            request (Request): Http request object.

        Returns:
            response (Response): Http response object.

        """
        validation_error = validate_avatar_src(request.FILES["avatar"])
        if validation_error:
            return Response(validation_error, cls._http_bad_request)

        profile = Profile.get_by_user_id_with_avatar(request.user.id)
        if not profile:
            app_logger.error(cls._profile_error)
            Response(cls._profile_error, cls._http_internal_error)

        if hasattr(profile, "avatar"):
            delete_file_from_sys(profile.avatar.src.path)
        profile.set_new_avatar(request.FILES["avatar"])
        return Response(cls._successful_avatar_update, cls._http_success)

    @classmethod
    def update_own_profile(cls, request: Request) -> Response:
        """ Handle logic for updating user profile details.

        Validate request data, check that profile is existed for user from
        request and update profile in case all checks passed.
        Return corresponding response.

        Args:
            request (Request): Http request object.

        Returns:
            response (Response): Http response object.

        """
        request.data.pop("avatar")
        profile_data = InProfileSerializer(data=request.data)
        if not profile_data.is_valid():
            return Response(
                {"error": profile_data.errors}, cls._http_bad_request,
            )

        profile = Profile.objects.get(user_id=request.user.id)
        if not profile:
            Response(cls._profile_error, cls._http_internal_error)

        try:
            profile.full_name = profile_data.validated_data["fullName"]
            profile.unique_email = profile_data.validated_data["email"]
            profile.unique_phone = profile_data.validated_data["phone"]
            profile.save()
        except IntegrityError as exc:
            return Response({"error": exc.args}, cls._http_bad_request)

        return Response(OutProfileSerializer(profile).data, cls._http_success)

    @classmethod
    def update_own_password(cls, request: Request) -> Response:
        """ Handle logic for updating user password.

        Validate request data, check current password for user from request
        and update password and session in case all checks passed.
        Return corresponding response.

        Args:
            request (Request): Http request object.

        Returns:
            response (Response): Http response object.

        """
        password_details = ChangePasswordSerializer(data=request.data)
        if not password_details.is_valid():
            return Response(
                {"error": password_details.errors}, cls._http_bad_request,
            )

        user = authenticate(
            username=request.user.username,
            password=password_details.validated_data["currentPassword"]
        )
        if not user:
            return Response(cls._invalid_password_error, cls._http_bad_request)

        update_user_password(
            user, password_details.validated_data["newPassword"],
        )
        cls._reset_user_session(request, user)
        return Response(cls._successful_psw_update, cls._http_success)

    @staticmethod
    def _reset_user_session(request: Request, user: User) -> None:
        """Reset session details for user.

        Args:
            request (Request): Http request object.
            user (User): User instance.

        """
        logout(request)
        login(request, user)
        app_logger.info(f"Session was reset for {user.id=}")
