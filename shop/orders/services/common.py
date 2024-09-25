from orders.models import DeliveryType

class DeliveryService:
    """Class for handling business logic related to order delivery."""

    @staticmethod
    def count_cost(
            order_price: int, delivery_type: DeliveryType
    ) -> int:
        """Get delivery price depend on delivery speed."""


        if order_price >= delivery_type.free_delivery_order_price:
            return 0

        return delivery_type.price
