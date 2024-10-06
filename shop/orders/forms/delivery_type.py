from decimal import Decimal
from typing import Optional

from django import forms

from orders.models import DeliveryType

class DeliveryTypeForm(forms.ModelForm):
    class Meta:
        model = DeliveryType
        fields = '__all__'

    def clean_price(self) -> Optional[Decimal]:
        price = self.cleaned_data.get("price")
        if (
                not self.errors.get("price") and
                price and
                price >= 0
        ):
            return price

        raise forms.ValidationError(
            "Delivery price should be greater than or equal to zero."
        )

    def free_delivery_order_price(self) -> Optional[Decimal]:
        order_price = self.cleaned_data.get("free_delivery_order_price")
        if not self.errors.get("free_delivery_order_price") and order_price:
            if order_price < 0:
                raise forms.ValidationError(
                    "Order products price for free delivery should be greater "
                    "than or equal to zero."
                )

        return order_price
