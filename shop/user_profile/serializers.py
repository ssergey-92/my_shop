from rest_framework import serializers

from .models import Avatar, Profile

class OutAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ["src", "alt"]


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
