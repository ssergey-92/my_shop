import re

from rest_framework import serializers

from .models import Avatar

invalid_phone_number = (
    "Invalid phone number format! ex. +79876543210 or 89876543210"
)
full_name_error = (
    "Full name should contain only letters and space! "
    "Min word len is 2 letters!"
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
        full_name_pattern = "^[a-zA-ZА-Яа-я ]{2,}$"
        if re.match(full_name_pattern, full_name) and not full_name.isspace():
            return full_name

        raise serializers.ValidationError(full_name_error)

    def validate_phone(self, value: str):
        phone = value.strip()
        if (
                phone.startswith("+") and
                len(phone) == 12 and
                phone.lstrip("+").isdigit()
        ) or (
                len(phone) == 11 and phone.isdigit()
        ):
            return phone

        raise serializers.ValidationError(invalid_phone_number)


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
