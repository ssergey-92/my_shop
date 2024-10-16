from typing import Optional

from django import forms

from common.validators import validate_full_name, validate_phone_number
from orders.constants import ORDER_STATUSES
from orders.models import Order
from orders.validators import validate_address, validate_city_name


class OrderForm(forms.ModelForm):
    """Class OrderForm. Custom form for django admin panel.

    Class is used for Order (admin.ModelAdmin).

    """
    class Meta:
        model = Order
        fields = "__all__"

    def clean_receiver_fullname(self) -> Optional[str]:
        """Add extra validation for 'receiver_fullname' field."""

        full_name = self.cleaned_data["receiver_fullname"]
        if full_name is None:
            return

        full_name = full_name.strip()
        validation_error = validate_full_name(full_name)
        if not validation_error:
            return full_name

        raise forms.ValidationError(validation_error)

    def clean_receiver_phone(self) -> Optional[str]:
        """Add extra validation for 'receiver_phone' field."""

        phone = self.cleaned_data.get("receiver_phone")
        if phone is None:
            return

        phone = phone.strip()
        validation_error = validate_phone_number(phone)
        if not validation_error:
            return phone

        raise forms.ValidationError(validation_error)

    def clean_city(self) -> Optional[str]:
        """Add extra validation for 'city' field."""

        city = self.cleaned_data.get("city")
        if city is None:
            return

        validation_error = validate_city_name(city)
        if not validation_error:
            return city

        raise forms.ValidationError(validation_error)

    def clean_address(self) -> Optional[str]:
        """Add extra validation for 'address' field."""

        address = self.cleaned_data.get("address")
        if address is None:
            return

        address = address.strip()
        validation_error = validate_address(address)
        if not validation_error:
            return address

        raise forms.ValidationError(validation_error)

    def clean_payment_comment(self) -> str:
        """Extra validation for 'payment_comment' field.

        Field is mandatory if status is 'payment rejected'.

        """
        if (
                self.cleaned_data.get("status") and
                self.cleaned_data["status"].name ==
                ORDER_STATUSES["payment_rejected"] and not
                self.cleaned_data.get("payment_comment")
        ):
            raise forms.ValidationError("Describe reason of rejected payment!")

        return self.cleaned_data.get("payment_comment")
