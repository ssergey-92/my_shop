"""Serializers with related model ProductSpecification."""

from rest_framework import serializers

from products.models import ProductSpecification

class ProductSpecificationsSerializer(serializers.ModelSerializer):
    """Class is used for serializing ProductSpecification."""

    class Meta:
        model = ProductSpecification
        fields = ("name", "value")
