"""Serializers with related model ProductTag."""

from rest_framework import serializers

from products.models import ProductTag


class ProductTagSerializer(serializers.ModelSerializer):
    """ProductTag base serializer."""

    class Meta:
        model = ProductTag
        fields = ("id", "name")


class SpecificProductTagSerializer(serializers.ModelSerializer):
    """ProductTag specific serializer."""
    # name = serializers.SerializerMethodField()

    class Meta:
        model = ProductTag
        fields = ("name", )

    # deviated from swagger file !!!
    # def get_name(self, obj: ProductTag) -> int:
    #     return obj.id
