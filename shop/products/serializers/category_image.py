"""Serializers with related model CategoryImage."""

from rest_framework import serializers

from products.models import Category, CategoryImage


class CategoryImageSerializer(serializers.ModelSerializer):
    """Class is used for serializing CategoryImage."""

    class Meta:
        model = CategoryImage
        fields = ("src", "alt")
