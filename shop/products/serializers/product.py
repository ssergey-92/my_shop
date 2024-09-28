"""Serializers with related model Product."""

from datetime import datetime, date
from typing import Optional

from rest_framework import serializers

from .product_tag import ProductTagSerializer, SpecificProductTagSerializer
from .product_review import  ProductReviewSerializer
from .product_specification import ProductSpecificationsSerializer
from .product_image import ProductImageSerializer
from products.models import Product, ProductImage


class CommonProductSerializer(serializers.ModelSerializer):
    """Class is used as base class for serializing Product."""

    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
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

    def get_price(self, obj: Product) -> float:
        today_date = date.today()
        if (
                obj.is_sales and
                obj.sales_price and
                (obj.sales_from <= today_date <= obj.sales_to)
        ):
            return float(obj.sales_price)

        return float(obj.price)

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


class InSalesProductSerializer(serializers.Serializer):
    """Class is used for validation query param for GET /sales."""

    currentPage = serializers.IntegerField(
        required=False, default=1, min_value=1,
    )

    def to_representation(self, instance: dict) -> dict:
        return {"current_page": instance["currentPage"]}


class OutSalesProductSerializer(serializers.ModelSerializer):
    """Class is used for serializing sales product."""

    salePrice = serializers.SerializerMethodField()
    dateFrom = serializers.SerializerMethodField()
    dateTo = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "title",
            "images",
        )

    def get_salePrice(self, obj: Product) -> float:
        price = obj.sales_price or obj.price
        return float(price)

    def get_dateFrom(self, obj: Product) -> Optional[str]:
        return obj.sales_from.strftime("%m-%d") if obj.sales_from else None

    def get_dateTo(self, obj: Product) -> Optional[date]:
        return obj.sales_to.strftime("%m-%d") if obj.sales_to else None

    def get_images(self, obj: Product) -> list[dict]:
        images = obj.images.all()
        if not images.exists():
            return [{"alt": ""}]
        return ProductImageSerializer(images, many=True).data


