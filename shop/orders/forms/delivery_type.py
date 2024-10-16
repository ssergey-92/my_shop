from decimal import Decimal
from typing import Optional

from django import forms

from orders.models import DeliveryType


class DeliveryTypeForm(forms.ModelForm):
    """Class DeliveryTypeForm. Custom form for django admin panel.

    Class is used for DeliveryType (admin.ModelAdmin).

    """
    class Meta:
        model = DeliveryType
        fields = "__all__"

    def clean_price(self) -> Optional[Decimal]:
        """Add extra validation for 'price' field.

        If price is passed default validation without errors than check that
        price >=0.
        """

        price = self.cleaned_data.get("price")
        if not self.errors.get("price") and price >= 0:
            return price

        raise forms.ValidationError(
            "Delivery price should be greater than or equal to zero."
        )

    def clean_free_delivery_order_price(self) -> Optional[Decimal]:
        """Add extra validation for 'free_delivery_order_price' field.

        If field is set than check that price >= 0.
        """

        order_price = self.cleaned_data.get("free_delivery_order_price")
        if not self.errors.get("free_delivery_order_price") and order_price:
            if order_price < 0:
                raise forms.ValidationError(
                    "Order products price for free delivery should be greater "
                    "than or equal to zero."
                )

        return order_price
