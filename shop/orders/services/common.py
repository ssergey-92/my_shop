from orders.models import DeliveryType, Order

class DeliveryService:
    """Class for handling business logic related to order delivery."""

    @staticmethod
    def count_cost(
            products_cost: int, delivery_type: DeliveryType
    ) -> int:
        """Count delivery cost for new Order instance."""

        if (
                delivery_type.free_delivery_order_price and
                products_cost >= delivery_type.free_delivery_order_price
        ):
            return 0

        return delivery_type.price

    @classmethod
    def recount_delivery_cost(cls, order_id: int) -> int:
        """Recount delivery cost for existed order."""

        order = Order.objects.select_related("delivery_type").get(id=order_id)
        return cls.count_cost(order.products_cost, order.delivery_type)
