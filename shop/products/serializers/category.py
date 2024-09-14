"""Serializers with related model Category."""

from typing import Union

from rest_framework import serializers

from .category_image import CategoryImageSerializer
from products.models import Category


class OutSubcategorySerializer(serializers.ModelSerializer):
    """Class is used for serializing subcategory (Category model class).

    Set default value for image field if not provided.

    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "image")

    def get_image(self, obj: Category) -> Union[str, dict]:
        """set default value for image field if not provided."""

        if obj.image:
            return CategoryImageSerializer(obj.image).data
        else:
            return "Not set"

class OutCategoriesTreeSerializer(serializers.ModelSerializer):
    """Class is used for serializing categories tree.

    Serialize only active subcategories and set default value for image field
    if not provided.

    """
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "image", "subcategories")

    def get_image(self, obj: Category) -> Union[str, dict]:
        """set default value for image field if not provided."""

        if obj.image:
            return CategoryImageSerializer(obj.image).data
        else:
            return "Not set"

    def get_subcategories(self, obj: Category) -> Union[list, list[dict]]:
        """Serialize only active subcategories else pass."""

        subcategories = []
        for subcategory in obj.subcategories.order_by("title").all():
            if subcategory.is_active:
                subcategories.append(OutSubcategorySerializer(subcategory).data)

        return subcategories
