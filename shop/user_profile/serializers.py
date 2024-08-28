"""App serializers for django rest framework."""

from rest_framework import serializers

from .models import Avatar
from .validators import (
    validate_profile_unique_phone,
    validate_profile_full_name,
)


class InProfileSerializer(serializers.Serializer):
    """Class for validating Profile data."""

    fullName = serializers.CharField(allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False, required=True)
    phone = serializers.CharField(allow_blank=False, required=False)

    def validate_fullName(self, value: str) -> str:
        """Extra validation for fullName field.

        Args:
            value (str): Full Name

        Returns:
            str: Full name

        """
        full_name = value.strip()
        validation_error = validate_profile_full_name(full_name)
        if not validation_error:
            return full_name

        raise serializers.ValidationError(validation_error)

    def validate_phone(self, value: str) -> str:
        """Extra validation for phone field.

        Args:
            value (str): Phone number

        Returns:
            str: Phone numbere

        """
        phone = value.strip()
        validation_error = validate_profile_unique_phone(phone)
        if not validation_error:
            return phone

        raise serializers.ValidationError(validation_error)


class OutAvatarSerializer(serializers.ModelSerializer):
    """Class for serializing Avatar object."""

    class Meta:
        model = Avatar
        fields = ["src", "alt"]


class OutProfileSerializer(serializers.Serializer):
    """Class for serializing Profile object."""

    fullName = serializers.CharField(
        allow_blank=True,
        required=True,
        source="full_name",
    )
    email = serializers.EmailField(
        allow_blank=True,
        required=False,
        source="unique_email",
    )
    phone = serializers.CharField(
        allow_blank=True,
        required=False,
        source="unique_phone",
    )
    avatar = OutAvatarSerializer(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    """Class for validating password details."""

    currentPassword = serializers.CharField(allow_blank=False, required=True)
    newPassword = serializers.CharField(allow_blank=False, required=True)
