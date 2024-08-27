from os import getenv as os_getenv
from re import match
from typing import Optional

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from common.custom_logger import app_logger

invalid_phone_number_error = "Invalid phone number format! ex. +79876543210"
full_name_error = (
    "Full name should contain only letters and space! "
    "Min word len is 2 letters!"
)
image_missing_error = "File is not attached!"
image_size_error = "Image size is bigger than 2 MB!"
image_unsupported_error = (
    f"Your image extension is unsupported! Supported formats "
    f"{settings.SUPPORTED_IMAGE_EXTENSIONS}"
)
image_extension_error = f"Image name should contain extension! "


def validate_profile_full_name(full_name: str) -> Optional[str]:
    full_name_pattern = "^[a-zA-ZА-Яа-я ]{2,}$"
    if not match(full_name_pattern, full_name) or full_name.isspace():
        return full_name_error
    app_logger.debug(f"{full_name} has supported format")


def validate_profile_unique_phone(phone: str) -> Optional[str]:
    if not (
        (phone.startswith("+") and len(phone) == 12 and phone[1:].isdigit())
    ):
        return invalid_phone_number_error
    app_logger.debug(f"{phone} has supported format")


def validate_avatar_src(
        image_file: Optional[InMemoryUploadedFile],
) -> Optional[str]:
    if not image_file:
        return image_missing_error
    elif image_file.size > int(os_getenv("SHOP_MEDIA_FILE_MAX_SIZE")):
        return image_size_error
    try:
        extension = image_file.name.rsplit(".", 1)
        if (
                extension == 0 or
                extension[1] not in settings.SUPPORTED_IMAGE_EXTENSIONS
        ):
            return image_unsupported_error
    except IndexError:
        return image_extension_error

    app_logger.debug(f"{image_file.name} has supported format and size")