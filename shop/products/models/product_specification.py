"""App db model ProductSpecification with intermediate table."""

from django.db import models


class ProductAndSpecification(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, null=False, blank=False,
    )
    specification = models.ForeignKey(
        "ProductSpecification", on_delete=models.CASCADE, null=False, blank=False,
    )

    class Meta:
        unique_together = (("product", "specification"),)



class ProductSpecification(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    value = models.CharField(max_length=150, null=False, blank=False)
    products = models.ManyToManyField(
        "Product",
        through="ProductAndSpecification",
        related_name="specifications",
        )

    class Meta:
        verbose_name = "Product: image"
        verbose_name_plural = "Products: specifications"

    def __str__(self) -> str:
        """String representation of ProductSpecification object."""

        return f"Product specification name: {self.name} value: {self.value}"
