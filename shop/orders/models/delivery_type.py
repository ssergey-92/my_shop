from django.db import models


class DeliveryType(models.Model):
    name = models.CharField(
        max_length=100, unique=True, null=False, blank=False,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True,
    )
    free_delivery_order_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )


    class Meta:
        verbose_name = "Order: delivery type"
        verbose_name_plural = "Order: delivery types"

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order delivery type: {self.name}"
