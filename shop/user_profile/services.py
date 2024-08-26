from logging import error
from os import getenv as os_getenv, remove as os_remove
from typing import Optional, Any

from django.conf import settings
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from .custom_log import app_logger
from .models import update_user_password, Profile, Avatar
from .serializers import (
    OutAvatarSerializer,
    ChangePasswordSerializer,
    OutProfileSerializer,
)

class HandleProfile:
    _invalid_password_error = {"error": "Invalid user password!"}
    _profile_error = {"error": "User profile is not found!"}
    _avatar_image_missing_error = {
        "error": "File is not attached under key 'avatar'"
    }
    _avatar_image_size_error = {"error": "Image size is bigger than 2 MB!"}
    _successful_psw_update = {"msg": "Password was successfully changed."}
    _successful_avatar_update = {"msg": "Avatar was successfully changed."}
    _http_bad_request = HTTP_400_BAD_REQUEST
    _http_success = HTTP_200_OK
    _http_internal_error = HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def get_own_profile(cls, request: Request) -> Response:
        profile = Profile.get_by_user_id_with_avatar(request.user.id)
        if profile:
            try:
                return Response(
                    OutProfileSerializer(profile).data, status=HTTP_200_OK,
                )
            except AttributeError as exc:
                app_logger.error(f"Error while serializing Profile: {exc}")

        return Response(cls._profile_error, cls._http_internal_error)

    @classmethod
    def update_own_avatar(cls, request: Request) -> Response:
        image_error = cls._check_avatar_image(request.FILES)
        if image_error:
            return Response(image_error, cls._http_bad_request)

        profile = Profile.get_by_user_id_with_avatar(request.user.id)
        if not profile:
            Response(cls._profile_error, cls._http_internal_error)

        if hasattr(profile, "avatar"):
            cls._delete_file_from_sys(profile.avatar.src.path)
        profile.set_new_avatar(request.FILES["avatar"])
        return Response(cls._successful_avatar_update, cls._http_success)

    @classmethod
    def update_own_profile(cls, request: Request) -> Response:
        profile_data = InProfileSerializer
        print(111111111111111111111111111111111, request.data)

        return Response()

    @classmethod
    def update_own_password(cls, request: Request) -> Response:
        password_details = ChangePasswordSerializer(data=request.data)
        if not password_details.is_valid():
            validation_error = {"error": password_details.errors}
            return Response(validation_error, cls._http_bad_request)
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
        app_logger.info(f"Password was changed for {user.id=}")
        return Response(cls._successful_psw_update, cls._http_success)

    @classmethod
    def _check_avatar_image(
            cls, request_files: Optional[MultiValueDict],
    ) -> Optional[dict]:
        error_msg = None
        if not request_files["avatar"]:
            error_msg =  cls._avatar_image_missing_error
        elif (
                request_files["avatar"].size >
                int(os_getenv("SHOP_MEDIA_FILE_MAX_SIZE"))
        ):
            error_msg = cls._avatar_image_size_error

        return error_msg

    @staticmethod
    def _delete_file_from_sys(file_path: str) -> None:
        try:
            os_remove(file_path)
            app_logger.debug(f"file as {file_path=} was deleted!")
        except FileNotFoundError:
            app_logger.error(f"{file_path=} is not existed in sys!")

    @staticmethod
    def _reset_user_session(request: Request, user: User) -> None:
        logout(request)
        login(request, user)
