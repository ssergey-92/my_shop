from decimal import Decimal


class OrderedProductHandler:

    @staticmethod
    def recount_total_price(
        previous_qnty: int,
        previous_total_price: Decimal,
        new_qnty: int,
        current_product_price: Decimal,
    ) -> Decimal:
        """Recount total price for ordered product in order."""

        new_total_price = previous_total_price
        if new_qnty < previous_qnty:
            new_total_price = round(
                previous_total_price / previous_qnty * new_qnty, 2
            )
        elif new_qnty > previous_qnty:
            new_total_price += (
                (new_qnty -previous_qnty) * current_product_price
            )
        return new_total_price
