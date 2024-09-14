"""Serializers with related model Product."""

from datetime import datetime

from rest_framework import serializers

from .product_tag import ProductTagSerializer, SpecificProductTagSerializer
from .product_review import  ProductReviewSerializer
from .product_specification import ProductSpecificationsSerializer
from .product_image import ProductImageSerializer
from products.models import Product, ProductImage


class CommonProductSerializer(serializers.ModelSerializer):
    """Class is used as base class for serializing Product."""

    category = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    freeDelivery = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "rating",
        )

    def get_category(self, obj: Product) -> int:
        return obj.category.id if obj.category else None

    def get_date(self, obj: Product) -> datetime:
        return obj.created_date

    def get_description(self, obj: Product) -> str:
        return obj.shot_description

    def get_freeDelivery(self, obj: Product) -> bool:
        return obj.free_delivery

    def get_images(self, obj: Product) -> list:
        images = obj.images.all()
        if not images.exists():
            return [{"alt": ""}]
        return ProductImageSerializer(images, many=True).data


class OutSpecialProductSerializer(CommonProductSerializer):
    """Class is used to serialize Product for group specific format.

    Products groups: 'popular', 'limited', 'banners', 'catalog'.

    """
    reviews = serializers.SerializerMethodField()
    tags = ProductTagSerializer(many=True, required=False)

    class Meta(CommonProductSerializer.Meta):  # Inherit Meta class
        fields = CommonProductSerializer.Meta.fields + ("reviews", "tags")

    def get_reviews(self, obj: Product) -> int:
        return obj.reviews.count() if hasattr(obj, "reviews") else 0


class OutProductFullSerializer(CommonProductSerializer):
    """Class is used to serialize Product for (GET /product)."""

    reviews = ProductReviewSerializer(many=True, required=False)
    specifications = ProductSpecificationsSerializer(many=True, required=False)
    tags = SpecificProductTagSerializer(many=True, required=False)
    fullDescription = serializers.SerializerMethodField()

    class Meta(CommonProductSerializer.Meta):  # Inherit Meta class
        fields = (
                CommonProductSerializer.Meta.fields +
                ("reviews", "specifications", "tags", "fullDescription")
        )

    def get_fullDescription(self, obj: Product) -> str:
        return obj.full_description or obj.shot_description

