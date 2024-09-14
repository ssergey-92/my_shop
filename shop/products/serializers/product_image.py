"""Serializers with related model ProductImage."""

from rest_framework import serializers

from products.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Class is used for serializing ProductImage."""

    class Meta:
        model = ProductImage
        fields = ("src", "alt")
