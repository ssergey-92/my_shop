"""Module with serializers related to Order."""

from datetime import datetime

from rest_framework import serializers

from common.validators import validate_full_name
from orders.constants import CARD_NUMBER_LENGTH, CARD_CODE_LENGTH

months = [number for number in range(1, 13)]
current_year_last_digits = datetime.now().year % 2000
card_number_length_error = (
    f"Card number length should contain  {CARD_NUMBER_LENGTH} digits!"
)
card_code_length_error = (
    f"Card code length should contain {CARD_CODE_LENGTH} digits!"
)
month_error = f"Month should be in range {months}!"
year_error = f"Year should be greater or equal {current_year_last_digits}!"


class PaymentCardSerializer(serializers.Serializer):
    """Class is used for validation card details."""

    number = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    month = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True)

    def validate_number(self, number: str) -> str:
        """Add extra Validation of field 'number'."""

        if number.isdigit() and (len(str(number)) == CARD_NUMBER_LENGTH):
            return number

        raise serializers.ValidationError(card_number_length_error)

    def validate_name(self, name: str) -> str:
        """Add extra Validation of field 'name'."""

        validation_error = validate_full_name(name)
        if not validation_error:
            return name

        raise serializers.ValidationError(validation_error)

    def validate_month(self, month: int) -> int:
        """Add extra Validation of field 'month'."""

        if month in months:
            return month

        raise serializers.ValidationError(month_error)

    def validate_year(self, year: int) -> int:
        """Add extra Validation of field 'year'."""

        if year >= current_year_last_digits:
            return year

        year = year % 2000
        if year >= current_year_last_digits:
            return year

        raise serializers.ValidationError(year_error)

    def validate_code(self, code: str) -> str:
        """Add extra Validation of field 'year'."""

        if code.isdigit() and (len(str(code)) == CARD_CODE_LENGTH):
            return code

        raise serializers.ValidationError(card_code_length_error)
