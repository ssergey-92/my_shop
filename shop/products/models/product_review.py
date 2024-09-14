"""App db model ProductReview."""

from django.db import models


class ProductReview(models.Model):
    author = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    text = models.TextField(max_length=1000, null=False, blank=False)
    rate = models.SmallIntegerField(null=False)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        to="Product",
        to_field="id",
        related_name="reviews",
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        unique_together = (("email", "product"),)
        verbose_name = "Product: review"
        verbose_name_plural = "Products: reviews"

    def __str__(self) -> str:
        """String representation of ProductReview object."""

        return f"Product review: {self.id} for product: {self.product.title}"
