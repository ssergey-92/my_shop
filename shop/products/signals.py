"""App signal functions."""

from django.db.models import Count, Sum, FloatField
from django.db.models.base import ModelBase
from django.db.models.functions import Cast
from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
    post_delete,
)
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import CategoryImage, ProductImage, ProductReview, Product
from common.custom_logger import app_logger
from common.utils import delete_file_from_sys


@receiver([pre_save, pre_delete], sender=CategoryImage)
def delete_category_image_from_sys(
    sender: ModelBase, instance: CategoryImage, *args, **kwargs,
) -> None:
    """Delete image of category from sys.

    Delete image if signal is pre_delete or pre_save in case field "src" is
    updated.

    Args:
        sender (ModelBase): CategoryImage model
        instance (User): CategoryImage instance

    """

    if kwargs.get("raw", False):
        app_logger.info(
            f"\n'delete_category_image_from_sys' is disabled for "
            f"loading fixture\n"
        )
        return

    app_logger.info(f"Caught signal {kwargs.get("signal")} for {instance}")
    if not instance.id:
        return

    if kwargs.get("signal") == pre_save:
        image = CategoryImage.objects.get(id=instance.id)
        image_path = image.src.path
        if image.src.path == instance.src.path:
            return
    else:
        image_path = instance.src.path

    app_logger.info(f"Deleting old image for {instance}")
    delete_file_from_sys(image_path)


@receiver([pre_save, pre_delete], sender=ProductImage)
def delete_product_image_from_sys(
    sender: ModelBase, instance: CategoryImage, *args, **kwargs,
) -> None:
    """Delete image of product from sys.

    Delete image if signal is pre_delete or pre_save in case field "src" is
    updated.

    Args:
        sender (ModelBase): ProductImage model
        instance (User): ProductImage instance

    """
    if kwargs.get("raw", False):
        app_logger.info(
            f"\n'delete_product_image_from_sys' is disabled for "
            f"loading fixture\n"
        )
        return

    app_logger.info(f"Caught signal {kwargs.get("signal")} for {instance}")
    if not instance.id:
        return

    if kwargs.get("signal") == pre_save:
        image = ProductImage.objects.get(id=instance.id)
        image_path = image.src.path
        if image.src.path == instance.src.path:
            return
    else:
        image_path = instance.src.path

    app_logger.info(f"Deleting old image for {instance}")
    delete_file_from_sys(image_path)


@receiver([post_save, post_delete], sender=ProductReview)
def recount_product_rating(
    sender: ModelBase, instance: ProductReview, *args, **kwargs,
) -> None:
    """Recount product rating after changing in product reviews.

    Args:
        sender (ModelBase): ProductReview
        instance (User): ProductReview instance

    """

    if kwargs.get("raw", False):
        app_logger.info(
            f"\n'recount_product_rating' is disabled for loading fixture\n"
        )
        return

    app_logger.info(
        f"Caught signal {kwargs.get("signal")} for {instance.product.id}"
    )
    product_rating = (
        ProductReview.objects.
        filter(product_id=instance.product.id).
        aggregate(
            rate=(Cast(Sum("rate"), output_field=FloatField()) / Count("id"))
        )
    )
    app_logger.info(f"Rating {product_rating}  for {instance.product.id}")
    (
        Product.objects.
        filter(id=instance.product.id).
        update(rating=product_rating["rate"])
     )
