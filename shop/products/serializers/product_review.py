"""Serializers with related model ProductReview."""

from rest_framework import serializers

from products.models import ProductReview


class ProductReviewSerializer(serializers.ModelSerializer):
    """Class is used for serializing ProductReview."""

    class Meta:
        model = ProductReview
        fields = ("author", "email", "text", "date", "rate")
