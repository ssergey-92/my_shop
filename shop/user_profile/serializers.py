from rest_framework import serializers

from .models import Avatar
from .validators import (
    validate_profile_unique_phone,
    validate_profile_full_name,
)


class OutAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ["src", "alt"]


class InProfileSerializer(serializers.Serializer):
    fullName = serializers.CharField(allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False, required=True)
    phone= serializers.CharField(allow_blank=False, required=False)
    avatar = OutAvatarSerializer(required=False, allow_null=True)

    def validate_fullName(self, value: str):
        full_name = value.strip()
        validation_error = validate_profile_full_name(full_name)
        if not validation_error:
            return full_name

        raise serializers.ValidationError(validation_error)

    def validate_phone(self, value: str):
        phone = value.strip()
        validation_error = validate_profile_unique_phone(phone)
        if not validation_error:
            return phone

        raise serializers.ValidationError(validation_error)


class OutProfileSerializer(serializers.Serializer):
    fullName = serializers.CharField(
        allow_blank=True, required=True, source="full_name",
    )
    email = serializers.EmailField(
        allow_blank=True, required=False, source="unique_email",
    )
    phone = serializers.CharField(
        allow_blank=True, required=False, source="unique_phone",
    )
    avatar = OutAvatarSerializer(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(allow_blank=False, required=True)
    newPassword = serializers.CharField(allow_blank=False, required=True)
