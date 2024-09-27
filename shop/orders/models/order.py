from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet

from . import Product


class OrderAndProduct(models.Model):
    """Model Class is used as intermediate table for Order and Product."""

    order = models.ForeignKey(
        to="Order", on_delete=models.CASCADE,  null=False, blank=False,
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE,  null=False, blank=False,
    )
    total_quantity = models.PositiveIntegerField(
        default=0,  null=False, blank=False,
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



class Order(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    receiver_fullname = models.CharField(max_length=100, null=True, blank=False)
    receiver_email = models.EmailField(max_length=50, null=True, blank=False)
    receiver_phone = models.CharField(max_length=12, null=True, blank=False)
    products_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True,
    )
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True,
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
        verbose_name_plural = "Orders full details"

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order id: {self.id} created by user: {self.user.id}"

    @classmethod
    def get_by_id_with_prefetch(cls, order_id: int) -> Optional["Order"]:
        """Get active order by id with prefetch related data."""

        return (
            cls.objects.filter(id=order_id, is_active=True).
            select_related("created_by", "created_by__profile").
            prefetch_related(
                "products",
                "products__images",
                "products__tags",
                "products__reviews",
                "products__specifications",
                "orderandproduct_set",
            ).
            first()
        )

    @classmethod
    def get_user_orders_with_prefetch(cls, user: User) -> QuerySet["Order"]:
        """Get user's active orders with prefetch related data."""

        return (
            cls.objects.filter(created_by=user, is_active=True).
            select_related("created_by", "created_by__profile").
            prefetch_related(
                "products",
                "products__images",
                "products__tags",
                "products__reviews",
                "products__specifications",
                "orderandproduct_set",
            )
        )

