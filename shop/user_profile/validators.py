"""Module with additional validators."""

from os import getenv as os_getenv
from re import match as re_match
from typing import Optional

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from common.custom_logger import app_logger

invalid_phone_number_error = "Invalid phone number format! ex. +79876543210"
full_name_error = (
    "Full name should contain only letters and space! "
    "Min word len is 2 letters!"
)


def validate_profile_full_name(full_name: str) -> Optional[str]:
    """Check that full_name has correct format for Profile.full_name field."""

    full_name_pattern = "^[a-zA-ZА-Яа-я ]{2,}$"
    if not re_match(full_name_pattern, full_name) or full_name.isspace():
        return full_name_error

    app_logger.debug(f"{full_name} has supported format")


def validate_profile_unique_phone(phone: str) -> Optional[str]:
    """Check that phone has correct format for Profile.unique_phone field."""

    correct_phone_pattern = r"^\+\d{11}$"
    if not re_match(correct_phone_pattern, phone):
        return invalid_phone_number_error

    app_logger.debug(f"{phone} has supported format")
