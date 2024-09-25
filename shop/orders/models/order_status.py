from django.db import models


class OrderStatus(models.Model):
    name = models.CharField(
        max_length=50, null=False, blank=False, unique=True,
    )

    class Meta:
        verbose_name = "Order: status"
        verbose_name_plural = "Order: statuses"

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order status: {self.name}"
