"""App db model Product."""

from django.db import models
from django.db.models import QuerySet, Q, Sum

from .product_review import ProductReview
from common.custom_logger import app_logger


class Product(models.Model):
    title = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    category = models.ForeignKey(
        to="Category",
        to_field="id",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    received_amount = models.PositiveIntegerField(null=False)
    count = models.PositiveIntegerField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    shot_description = models.CharField(
        max_length=1000, default="Not prescribed",
    )
    full_description = models.CharField(
        max_length=1000, default="See short description",
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, null=True, blank=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    sorting_index = models.PositiveSmallIntegerField(
        default=0, null=True, blank=True, db_index=True,
    )
    is_limited = models.BooleanField(default=False, db_index=True, null=False)

    class Meta:
        verbose_name = "Product: full details"
        verbose_name_plural = "Products: full details"

    def __str__(self) -> str:
        """String representation of Product object."""

        return f"Product id: {self.id} title: {self.title}"

    def add_new_review(self, new_review_data: dict) -> None:
        """Add new review to product."""

        app_logger.debug(f"Adding new review {new_review_data=}, {self=}")
        product_review = ProductReview(**new_review_data, product=self)
        product_review.save()
        self.reviews.add(product_review)
        self.save()

    @classmethod
    def get_limited_products(cls, total_products: int) -> QuerySet:
        """Get limited products."""

        return (
            cls.objects.
            filter(is_active=True, count__gt=0, is_limited=True).
            order_by("rating", "count", "price")
            [:total_products]
        )

    @classmethod
    def get_banners_products(cls, products_ids: list[int]) -> QuerySet:
        """Get banners products."""

        return cls.objects.filter(id__in=products_ids)

    @classmethod
    def get_popular_products(cls, total_products: int) -> QuerySet:
        """Get popular products."""

        return (
            cls.objects.
            filter(is_active=True, count__gt=0).
            annotate(total_sailed=Sum("orderandproduct__total_quantity")).
            order_by("-sorting_index", "-total_sailed")
            [:total_products]
        )
    @classmethod
    def get_unavailable_products(cls, products_ids: list[int]) -> QuerySet:
        """Get unavailable products.

        Product considered is unavailable if is_active=False or count <= 0.

        """
        return (
            Product.objects.
            filter(
                (Q(is_active=False) | Q(count__lte=0)) & Q(id__in=products_ids)
            )
        )

    @classmethod
    def select_available_products(
            cls, products_ids: list[int],
    ) -> QuerySet:
        """Select available products for update.

        Product considered is available if is_active=True and count > 0.

        """
        return (
            cls.objects.
            filter(is_active=True, count__gt=0, id__in=products_ids).
            select_for_update()
        )

