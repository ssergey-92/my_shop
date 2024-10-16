"""Module with app schemas."""

from datetime import datetime
from re import match as re_match

from pydantic import BaseModel, field_validator, Field

CARD_NUMBER_LENGTH = 16
CVV_CODE_LENGTH = 3
name_pattern = "^[a-zA-ZА-Яа-я ]{2,}$"
current_year_shot = datetime.now().year % 2000


class PaymentDetails(BaseModel):
    """Schema for validation payment details from request body."""

    number: str
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=current_year_shot)
    code: str
    name: str
    charge_price: float = Field(ge=0)

    @field_validator("number", mode="after")
    @classmethod
    def validate_number(cls, number: str) -> str:
        """Extra validation that for card number."""

        if number.isdigit() and len(number) == CARD_NUMBER_LENGTH:
            return number

        raise ValueError(
            f"Card number length must be {CARD_NUMBER_LENGTH} digits long!"
        )

    @field_validator("code", mode="after")
    @classmethod
    def validate_cvv_code(cls, code: str) -> str:
        """Extra validation that for card cvv code."""

        if len(code) == CVV_CODE_LENGTH or code.isdigit():
            return code

        raise ValueError(f"CVV code must be {CVV_CODE_LENGTH} digits long!")

    @field_validator("name", mode="after")
    @classmethod
    def validate_card_holder_name(cls, name: str) -> str:
        """Extra validation that for cardholder name."""

        if re_match(name_pattern, name) and not name.isspace():
            return name

        raise ValueError(
            f"{name} has unsupported format. "
            f"It should match with pattern {name_pattern}"
        )
