"""App serializers for django rest framework."""

from rest_framework import serializers


class SignInSerializer(serializers.Serializer):
    """Class for validating user sign in details."""

    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)

class SignUpSerializer(serializers.Serializer):
    """Class for validating user sign up details."""

    name = serializers.CharField(allow_blank=False, required=True)
    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)
