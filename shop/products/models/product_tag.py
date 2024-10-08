"""App db model ProductTag with intermediate table."""


from django.db import models


class ProductAndTag(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    tag = models.ForeignKey("ProductTag", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("product", "tag"),)


class ProductTag(models.Model):
    name = models.CharField(
        unique=True, max_length=150, null=False, blank=False,
    )
    products = models.ManyToManyField(
        "Product", through="ProductAndTag", related_name="tags",
    )

    class Meta:
        verbose_name = "Product: tag"
        verbose_name_plural = "Products: tags"

    def __str__(self) -> str:
        """String representation of ProductTag object."""

        return f"Product tag name: {self.name}"
