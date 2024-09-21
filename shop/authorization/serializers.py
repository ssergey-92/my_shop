"""App serializers for django rest framework."""

from rest_framework import serializers

from common.validators import validate_full_name

class SignInSerializer(serializers.Serializer):
    """Class for validating user sign in details."""

    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)


class SignUpSerializer(serializers.Serializer):
    """Class for validating user sign up details."""

    name = serializers.CharField(allow_blank=False, required=True)
    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)

    def validate_name(self, name: str) -> str:
        """Extra validation for field 'name'."""

        validation_error = validate_full_name(name)
        if not validation_error:
            return name

        raise serializers.ValidationError(validation_error)
