"""App db model CategoryImage."""

from django.db import models

unavailable_image = "Image is currently unavailable!"

def get_product_image_saving_path(
        instance: "ProductImage", filename: str,
) -> str:
    """Create saving relative path for image of Product."""

    return "products/product_{product_id}/images/{filename}".format(
        product_id=instance.product.id, filename=filename,
    )


class ProductImage(models.Model):
    src = models.ImageField(
        upload_to=get_product_image_saving_path,
        max_length=150,
        blank=False,
        null=False,
    )
    alt = models.CharField(
        default=unavailable_image,
        max_length=150,
        blank=False,
        null=False,
        )
    product = models.ForeignKey(
        to="Product",
        to_field="id",
        on_delete=models.CASCADE,
        related_name="images",
        null=False,
    )

    class Meta:
        verbose_name = "Product: image"
        verbose_name_plural = "Products: images"

    def __str__(self) -> str:
        """String representation of ProductImage object."""

        return f"Image url: {self.src.url} for product: {self.product.title}"
