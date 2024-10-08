"""Module with common app validators."""

from re import match as re_match
from typing import Optional

from common.custom_logger import app_logger

city_name_error = (
    "City name {name} has unsupported format! "
    "It should contain only letters and space! Min word len is 3 letters!"
)
address_error = (
    "Address {address} has unsupported format! It should contain only letters, "
    "digits, comma, digits and space! Min address length is 5 symbols!"
)

def validate_city_name(city_name: str) -> Optional[str]:
    """Check that city name has correct format."""

    city_name_pattern = "^[a-zA-ZА-Яа-я ]{3,}$"
    if not re_match(city_name_pattern, city_name) or city_name.isspace():
        return city_name_error.format(
            name=city_name, pattern=city_name_pattern,
        )

    app_logger.debug(f"{city_name} has supported format")


def validate_address(address: str) -> Optional[str]:
    """Check that address has correct format."""

    address_pattern = "^[a-zA-ZА-Яа-я0-9,. ]{5,}$"
    if not re_match(address_pattern, address) or address.isspace():
        return address_error.format(address=address, pattern=address_pattern)

    app_logger.debug(f"{address} has supported format")
