"""App db model CategoryImage."""

from django.db import models

unavailable_image = "Image is currently unavailable!"


def get_category_image_saving_path(
        instance: "CategoryImage", filename: str,
) -> str:
    """Create saving path for image of Category."""

    return "categories/images/{filename}".format(filename=filename)


class CategoryImage(models.Model):
    src = models.ImageField(
        upload_to=get_category_image_saving_path,
        max_length=150,
        blank=False,
        null=False,
    )
    alt = models.CharField(default=unavailable_image, max_length=150)


    class Meta:
        verbose_name = "Category: image"
        verbose_name_plural = "Categories: images"

    def __str__(self) -> str:
        """String representation of CategoryImage object."""

        return f"{self.__class__.__name__} id: {self.id}"
