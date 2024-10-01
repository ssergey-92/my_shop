"""App serializers for django rest framework."""
from typing import Optional

from rest_framework import serializers

from .models import Avatar
from common.validators import (
    validate_full_name,
    validate_phone_number,
)


class InProfileSerializer(serializers.Serializer):
    """Class for validating Profile data."""

    fullName = serializers.CharField(allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False, required=True)
    phone = serializers.CharField(allow_blank=False, required=False)

    def validate_fullName(self, value: str) -> str:
        """Extra validation for fullName field."""

        full_name = value.strip()
        validation_error = validate_full_name(full_name)
        if not validation_error:
            return full_name

        raise serializers.ValidationError(validation_error)

    def validate_phone(self, value: str) -> Optional[str]:
        """Extra validation for phone field."""

        if not value:
            return value

        phone = value.strip()
        validation_error = validate_phone_number(phone)
        if not validation_error:
            return phone

        raise serializers.ValidationError(validation_error)

    def to_representation(self, instance: dict) -> dict:
        """Sort validated data to required format."""

        formated_instance = {
            "full_name": instance["fullName"],
            "unique_email": instance["email"],
        }
        if instance.get("phone", None):
            formated_instance["unique_phone"]  = instance["phone"]

        return formated_instance


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

    def to_representation(self, instance: dict) -> dict:
        """Sort validated data to required format."""

        return {
            "current_password": instance["currentPassword"],
            "new_password": instance["newPassword"],
        }
