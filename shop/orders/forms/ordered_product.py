from typing import Optional

from django import forms
from django.core.exceptions import ValidationError

from orders.models import OrderAndProduct, Product
from orders.services import OrderedProductHandler


class OrderedProductInlineForm(forms.ModelForm):
    """Class OrderedProductInlineForm. Custom form for django admin panel.

    Class is used for OrderedProduct (admin.StackedInline).

    """
    current_price = forms.DecimalField(
        label='Current Price', required=False, max_digits=10, decimal_places=2,
    )
    purchased_price = forms.DecimalField(
        label='Purchased Price',
        required=False,
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        model = OrderAndProduct
        fields = ("product", "total_price", "total_quantity")

    def __init__(self, *args, **kwargs):
        """Call super method init, add extra fields and set readonly."""

        super(OrderedProductInlineForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id and self.instance.product:
            self.fields["purchased_price"].initial = round(
                (self.instance.total_price / self.instance.total_quantity), 2
            )
            self.fields["current_price"].initial = (
                self.instance.product.count_final_price()
            )
            self.fields["product"].disabled = True

        self.fields["current_price"].disabled = True
        self.fields["purchased_price"].disabled = True

    @staticmethod
    def _validate_product_extra_qnty(
        previous_qnty: int, new_qnty: int, available_qnty: Optional[int],
    ) -> None:
        """Validate product available quantity for aditing to order.

        If available quantity is less than then required quantity then
        raise corresponding ValidationError.

        """
        if available_qnty > (new_qnty - previous_qnty):
            return

        if previous_qnty > 0:
            error_msg = {
                "field": "total_quantity",
                "error": (
                    f"You can add extra {available_qnty} items to ordered"
                    f"{previous_qnty}! Total {previous_qnty + available_qnty}."
                ),
            }
        else:
            error_msg = {
                "field": "total_quantity",
                "error": f"{available_qnty} items are available to purchase!",
            }
        raise ValidationError(error_msg)

    def _validate_product_total_qnty(self) -> None:
        """Add optional extra validation for field 'total_quantity'.

        If total_quantity is more than previous quantity then additionally
        check that product has enough quantity for editing to order.

        """

        new_qnty = self.cleaned_data.get("total_quantity")
        previous_qnty = self.instance.total_quantity or 0
        if new_qnty <= previous_qnty:
            return

        product = self.cleaned_data.get("product")
        available_qnty = (
            Product.filter_available().
            filter(id=product.id).
            values_list("count", flat=True)
        )
        if not available_qnty:
            raise ValidationError({
                "field": "product",
                "error": f"'{product.title}' is not available to purchase "
                         f"or add extra quantity!"
            })
        self._validate_product_extra_qnty(
            previous_qnty, new_qnty, available_qnty[0],
        )

    def clean(self) -> Optional[dict]:
        """Add Extra validate and set fields values.

        Start validation and set fields values if there is no errors during
        built in validation.

        """
        try:
            cleaned_data = super().clean()
            if self.errors:
                return

            self._validate_product_total_qnty()
            if not cleaned_data.get("id"):  # CREATE
                cleaned_data["total_price"] = (
                    cleaned_data["total_quantity"] *
                    cleaned_data["product"].count_final_price()
                )
            elif cleaned_data["DELETE"] or self.has_changed() is False:  # DELETE | NO UPDATE
                cleaned_data["total_price"] = self.instance.total_price
            elif self.has_changed():  # UPDATE
                cleaned_data["previous_total_qnty"] = self.instance.total_quantity
                cleaned_data["previous_total_price"] = self.instance.total_price
                cleaned_data["total_price"] = (
                    OrderedProductHandler.recount_total_price(
                        cleaned_data["previous_total_qnty"],
                        cleaned_data["previous_total_price"],
                        cleaned_data["total_quantity"],
                        cleaned_data["current_price"],
                    )
                )
        except ValidationError as exc:
            self.add_error(
                exc.message_dict.get("field")[0],
                exc.message_dict.get("error")[0],
            )
        else:
            return cleaned_data
