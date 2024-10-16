"""App db model Order with intermediate table for Product."""

from decimal import Decimal
from typing import Optional

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import QuerySet, F, Sum

from . import Product
from orders.exceptions import OrderException


class OrderAndProduct(models.Model):
    """Model Class is used as intermediate table for Order and Product."""

    order = models.ForeignKey(
        to="Order", on_delete=models.CASCADE, null=False, blank=False,
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, null=False, blank=False,
    )
    total_quantity = models.PositiveIntegerField(
        default=0, null=False, blank=False,
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False,
    )

    class Meta:
        unique_together = (("order", "product"),)

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order id: {self.order.id} - Product id: {self.product.id}"

    @classmethod
    def bulk_add(
        cls, products_data: list[dict], order_id: int,
    ) -> None:
        """Bulk create instances."""

        cls.objects.bulk_create(
            [cls(order_id=order_id, **product) for product in products_data]
        )

    @classmethod
    def count_order_price(cls, order_id: int) -> Decimal:
        """Count order products price."""

        order_price = (
            cls.objects.filter(order_id=order_id).
            aggregate(order_price=Sum('total_price'))
        )["order_price"]
        return order_price or 0

    def custom_delete(self) -> None:
        """Delete instance in transaction with related objects updates.

        Delete instance, update related Product and Order as per instance
        details.

        """

        with transaction.atomic():
            (
                Product.objects.filter(id=self.product.id).
                update(count=(F("count") + self.total_quantity))
            )
            (
                Order.objects.filter(id=self.order.id).
                update(
                    products_cost=(F("products_cost") - self.total_price),
                    total_cost=(F("total_cost") - self.total_price),
                )
            )
            self.delete()

    def custom_create(self) -> None:
        """Create instance in transaction with related objects updates.

        Create instance, select for update related Product and Order and
        update them as per instance details. Raise error in case product
        quantity is less than required quantity.

        """
        with transaction.atomic():
            product = (
                Product.objects.select_for_update().
                get(id=self.product.id, is_active=True, count__gte=1)
            )
            if product.count < self.total_quantity:
                raise OrderException(
                    f"Correct your order # {self.order.id}! Only "
                    f"{product.count} '{product.title}' are available to "
                    f"purchase!"
                )
            product.count -= self.total_quantity
            product.save()
            (
                Order.objects.filter(id=self.order.id).
                update(
                    products_cost=(F("products_cost") + self.total_price),
                    total_cost=(F("total_cost") + self.total_price),
                )
            )
            self.save()

    def custom_update(
        self, previous_total_price: Decimal, previous_total_qnty: int,
    ) -> None:
        """Update instance in transaction with related objects updates.

        Update instance, select for update related Product and Order and
        update them as per instance details. Raise error in case product
        quantity is less than required quantity.

        """

        with transaction.atomic():
            product = (
                Product.objects.select_for_update().
                get(id=self.product.id, is_active=True, count__gte=1)
            )
            extra_products_qnty = self.total_quantity - previous_total_qnty
            if product.count < extra_products_qnty:
                raise OrderException(
                    f"Correct your order # {self.order.id}! Only "
                    f"{product.count} '{product.title}' are available to purchase!"
                )
            product.count -= extra_products_qnty
            product.save()
            extra_products_price = self.total_price - previous_total_price
            (
                Order.objects.filter(id=self.order.id).
                update(
                    products_cost=(F("products_cost") + extra_products_price),
                    total_cost=(F("total_cost") + extra_products_price),
                )
            )
            self.save()


class Order(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    receiver_fullname = models.CharField(
        max_length=100, null=True, blank=False,
    )
    receiver_email = models.EmailField(max_length=50, null=True, blank=False)
    receiver_phone = models.CharField(max_length=12, null=True, blank=False)
    products_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True, default=0,
    )
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True, default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=50, null=True, blank=False)
    address = models.CharField(max_length=200, null=True, blank=False)
    is_active = models.BooleanField(default=True)
    delivery_type = models.ForeignKey(
        to="DeliveryType",
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    payment_type = models.ForeignKey(
        to="PaymentType",
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    payment_comment = models.CharField(max_length=200, null=True, blank=True)
    status = models.ForeignKey(
        to="OrderStatus",
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
    )
    products = models.ManyToManyField(
        to=Product,
        through="OrderAndProduct",
        related_name="orders",
    )

    class Meta:
        verbose_name = "Order: full details"
        verbose_name_plural = "Orders: full details"

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order id: {self.id} created by user: {self.created_by.id}"

    @classmethod
    def get_by_id_with_prefetch(cls, order_id: int) -> Optional["Order"]:
        """Get active order by id with prefetch related data."""

        return (
            cls.objects.
            select_related("created_by", "created_by__profile").
            prefetch_related(
                "products",
                "products__images",
                "products__tags",
                "products__reviews",
                "products__specifications",
                "orderandproduct_set",
            ).
            get(id=order_id, is_active=True)
        )

    @classmethod
    def get_user_orders_with_prefetch(cls, user: User) -> QuerySet["Order"]:
        """Get user's active orders with prefetch related data."""

        return (
            cls.objects.
            select_related("created_by", "created_by__profile").
            prefetch_related(
                "products",
                "products__images",
                "products__tags",
                "products__reviews",
                "products__specifications",
                "orderandproduct_set",
            ).
            filter(created_by=user, is_active=True)
        )

    @classmethod
    def reset_delivery_related_costs(
        cls, order_id: int, delivery_cost: Decimal,
    ) -> None:
        """Reset delivery and total costs."""

        (
            cls.objects.filter(id=order_id).
            update(
                total_cost=F("products_cost") + delivery_cost,
                delivery_cost=delivery_cost
            )
        )
