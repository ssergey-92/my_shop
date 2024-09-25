from django.db import models


class PaymentType(models.Model):
    name = models.CharField(
        max_length=50, unique=True, null=False, blank=False,
    )

    class Meta:
        verbose_name = "Order: payment type"
        verbose_name_plural = "Order: payment types"

    def __str__(self) -> str:
        """String representation of instance."""

        return f"Order payment type: {self.name}"
