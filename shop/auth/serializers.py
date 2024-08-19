from rest_framework import serializers


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)

class SignUpSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=False, required=True)
    username = serializers.CharField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)
