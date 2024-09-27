"""Module with serializers related to catalog."""

from typing import Optional

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.custom_logger import app_logger
from products.models import Category

sort_items = ["rating", "price", "reviews", "date"]
sort_types = ["dec", "inc"]


class CatalogQueryParamsSerializer(serializers.Serializer):
    """Class is used to validate data from query parameters (GET /catalog)."""

    name = serializers.CharField(required=False, allow_blank=True)
    minPrice = serializers.FloatField(
        required=False, min_value=0, max_value=500000,
    )
    maxPrice = serializers.FloatField(
        required=False, min_value=0, max_value=500000,
    )
    freeDelivery = serializers.BooleanField(required=False)
    available = serializers.BooleanField(required=False)
    category= serializers.IntegerField(required=False, allow_null=True)
    currentPage = serializers.IntegerField(required=False, default=1)
    limit = serializers.IntegerField(required=False, default=20)
    tags = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    sort = serializers.CharField(required=False, default="date")
    sortType = serializers.CharField(required=False, default="dec")

    def validate_category(self, value) -> int:
        """Extra category id validation. Check that category id is existed"""
        if (
                not value or
                Category.objects.filter(id=value, is_active=True).exists()
        ):
            return value

        raise ValidationError(f"Category id: {id} is not existed")

    def validate_sort(self, value) -> str:
        """Extra sort validation. Check that sort value in sort_items."""

        if value not in sort_items:
            raise serializers.ValidationError(
                f"Sort value {value} is not supported!"
                f"\nSupported {sort_items}"
            )
        return value

    def validate_sortType(self, value) -> str:
        """Extra sortType validation. Check that sortType in sort_types."""

        if value not in sort_types:
            raise serializers.ValidationError(
                f"Sort type {value} is not supported!\nSupported {sort_types}!"
            )
        return value

    def to_representation(self, instance: dict) -> dict:
        """Sort and arrange validated data in required format."""

        app_logger.debug(f"{instance=}")
        return {
            "category_id":(
                instance.get("category") if instance.get("category") != 0
                else None
            ),
            "filters": self._get_filter_items(instance),
            "sort": self._get_sort_item(instance),
            "pagination": {
                "current_page": instance["currentPage"],
                "limit": instance["limit"],
            },
        }

    @staticmethod
    def _get_filter_items(instance: dict) -> dict:
        """Create new dict for filter method in query set.

        Drop fields if value is not set for optional fields and rename fields
        to use in query set filter.

        """
        filter_items = {}
        if instance.get("name"):
            filter_items["title__icontains"] = instance["name"]

        if instance.get("tags"):
            filter_items["tags__id__in"] = instance["tags"]

        if instance.get("available"):
            filter_items["count__gte"] = 1

        if instance.get("freeDelivery"):
            filter_items["free_delivery"] = instance["freeDelivery"]

        if instance.get("minPrice") is not None:
            filter_items["price__gte"] =  instance["minPrice"]

        if instance.get("maxPrice") is not None:
            filter_items["price__lte"] = instance["maxPrice"]

        return filter_items

    @staticmethod
    def _get_sort_item(instance: dict) -> Optional[str]:
        """Create str for order_by method in query set.

        Drop fields if value is not set for optional fields and rename fields
        to use in  order_by method in query set.

        """
        if not instance.get("sort"):
            return

        if instance["sort"] == "date":
            order_by_field = "created_date"
        elif instance["sort"] == "reviews":
            order_by_field = "total_reviews"
        elif instance["sort"] == "rating":
            order_by_field = "total_sailed"
        else:
            order_by_field = instance["sort"]

        sort_sequence = "-" if instance["sortType"] == "dec" else ""

        return sort_sequence + order_by_field
