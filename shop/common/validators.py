"""Module with validators for different apps."""

from os import getenv as os_getenv
from re import match as re_match
from typing import Optional

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from .custom_logger import app_logger

image_missing_error = "File is not attached!"
image_size_error = "Image size is bigger than 2 MB!"
image_unsupported_error = (
    f"Your image extension is unsupported! Supported formats"
    f"{settings.SUPPORTED_IMAGE_EXTENSIONS}"
)
image_extension_error = f"Image name should contain extension!"
invalid_phone_number_error = "Invalid phone number format! ex. +79876543210"
full_name_error = (
    "Full name should contain only letters and space! "
    "Min word len is 2 letters!"
)


def validate_image_src(
    image: Optional[InMemoryUploadedFile],
) -> Optional[str]:
    """Check that image has valid format and size.

    Args:
        image (str): avatar image

    Returns
        Optional[str]: validation error details

    """

    if not image:
        return image_missing_error
    elif image.size > int(os_getenv("SHOP_MEDIA_FILE_MAX_SIZE")):
        return image_size_error
    try:
        extension = image.name.rsplit(".", 1)
        if (
            extension == 0
            or extension[1] not in settings.SUPPORTED_IMAGE_EXTENSIONS
        ):
            return image_unsupported_error
    except IndexError:
        return image_extension_error

    app_logger.debug(f"{image.name} has supported format and size")


def validate_full_name(full_name: str) -> Optional[str]:
    """Check that full_name has correct format."""

    full_name_pattern = "^[a-zA-ZА-Яа-я ]{2,}$"
    if not re_match(full_name_pattern, full_name) or full_name.isspace():
        return full_name_error

    app_logger.debug(f"{full_name} has supported format")


def validate_phone_number(phone: str) -> Optional[str]:
    """Check that phone has correct format."""

    correct_phone_pattern = r"^\+\d{11}$"
    if not re_match(correct_phone_pattern, phone):
        return invalid_phone_number_error

    app_logger.debug(f"{phone} has supported format")
