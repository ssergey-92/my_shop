"""Module with form related to Product"""

from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from rest_framework.fields import ImageField

from common.validators import validate_image_src
from products.models import Product, ProductImage, ProductReview
from products.validators import (
    validate_product_price,
    validate_product_review_rate,
    validate_product_sorting_index,
)


class ProductForm(forms.ModelForm):
    """Class ProductForm. Custom form for django admin panel.

     Class is used for Product (admin.ModelAdmin).

     """
    class Meta:
        model = Product
        fields = "__all__"

    def clean_price(self) -> Optional[str]:
        """Add extra validation for 'price' field."""

        price = self.cleaned_data.get("price")
        validation_error = validate_product_price(price)
        if not validation_error:
            return price

        raise ValidationError(validation_error)

    def clean_sorting_index(self) -> Optional[str]:
        """Add extra validation for 'sorting_index' field."""

        sorting_index = self.cleaned_data.get("sorting_index")
        if not sorting_index:
            return None

        validation_error = validate_product_sorting_index(sorting_index)
        if not validation_error:
            return sorting_index

        raise ValidationError(validation_error)

    def clean(self) -> dict:
        """Add Extra validation for 'count' field."""

        cleaned_data = super().clean()
        count = self.cleaned_data.get("count")
        received_amount =  self.cleaned_data.get("received_amount")
        if not "id":
            return cleaned_data

        if count > received_amount:
            raise ValidationError(
                "Remains amount 'count' can not be more that received amount."
            )
        sold_amount = (
            self.instance.orderandproduct_set.
            aggregate(total_sailed=Sum("total_quantity"))["total_sailed"]
        )
        if count > (received_amount - sold_amount):
            raise ValidationError(
                "Summ of 'count'(remains) and 'sold' products can not be more "
                "then received amount!."
            )

        return cleaned_data


class ProductImageInlineForm(forms.ModelForm):
    """Class ProductImageInlineForm. Custom form for django admin panel.

     Class is used for ProductImage (InlineModelAdmin).

     """
    class Meta:
        model = ProductImage
        fields = "__all__"

    def clean_src(self) -> ImageField:
        """Add extra validation for 'src' field."""

        src = self.cleaned_data.get("src")
        validation_error = validate_image_src(src)
        if not validation_error:
            return src

        raise ValidationError(validation_error)


class ProductReviewForm(forms.ModelForm):
    """Class ProductReviewForm. Custom form for django admin panel.

     Class is used for ProductReview (admin.ModelAdmin).

     """
    class Meta:
        model = ProductReview
        fields = "__all__"

    def clean_rate(self):
        """Add extra validation for 'rate' field."""

        rate = self.cleaned_data.get("rate")
        validation_error = validate_product_review_rate(rate)
        if not validation_error:
            return rate

        raise ValidationError(validation_error)
