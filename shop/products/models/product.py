"""App db model Product."""

from datetime import date
from decimal import Decimal

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
    sales_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True,
    )
    sales_from = models.DateField(null=True)
    sales_to = models.DateField(null=True)
    received_amount = models.PositiveIntegerField(null=False)
    count = models.PositiveIntegerField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    shot_description = models.CharField(
        max_length=1000, default="Not prescribed",
    )
    full_description = models.CharField(
        max_length=5000, default="See short description",
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, null=True, blank=True,
    )
    sorting_index = models.PositiveSmallIntegerField(
        default=0, null=True, blank=True, db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_limited = models.BooleanField(default=False, db_index=True, null=False)
    is_sales = models.BooleanField(default=False, db_index=True, null=False)

    class Meta:
        verbose_name = "Product: full details"
        verbose_name_plural = "Products: full details"

    def __str__(self) -> str:
        """String representation of Product object."""

        return f"ID {self.id}: {self.title} - {self.count_final_price()} $"

    def add_new_review(self, new_review_data: dict) -> None:
        """Add new review to product."""

        app_logger.debug(f"Adding new review {new_review_data=}, {self=}")
        product_review = ProductReview(**new_review_data, product=self)
        product_review.save()
        self.reviews.add(product_review)
        self.save()


    def count_final_price(self) -> Decimal:
        """Get product price bases sales if available.

        If Product sales flag is activated, sales price is set, today date is
        between sales dates if set then use sales price else ordinary price.
        """

        today_date = date.today()
        if (
                self.is_sales and
                self.sales_price and
                (self.sales_from is None or self.sales_from <= today_date) and
                (self.sales_to is None or today_date <= self.sales_to)
        ):
            return self.sales_price

        return self.price

    @classmethod
    def get_limited_products(cls, total_products: int) -> QuerySet:
        """Get limited products."""

        return (
            cls.objects.
            select_related("category").
            prefetch_related("images", "reviews", "tags").
            filter(is_active=True, count__gt=0, is_limited=True).
            order_by("rating", "count", "price")
            [:total_products]
        )

    @classmethod
    def get_banners_products(cls, products_ids: list[int]) -> QuerySet:
        """Get banners products."""

        return (
            cls.objects.
            select_related("category").
            prefetch_related("images", "reviews", "tags").
            filter(id__in=products_ids)
        )

    @classmethod
    def get_popular_products(cls, total_products: int) -> QuerySet:
        """Get popular products."""

        return (
            cls.objects.
            select_related("category").
            prefetch_related("images", "reviews", "tags").
            filter(is_active=True, count__gt=0).
            annotate(total_sailed=Sum("orderandproduct__total_quantity")).
            order_by("-sorting_index", "-total_sailed")
            [:total_products]
        )

    @classmethod
    def get_sales_products(cls) -> QuerySet:
        """Get sales products."""

        today_date = date.today()
        return (
            cls.objects.
            prefetch_related("images").
            filter(
                Q(is_active=True) &
                Q(count__gte=1) &
                Q(is_sales=True) &
                (Q(sales_from__isnull=True) | Q(sales_from__lte=today_date)) &
                (Q(sales_to__isnull=True) | Q(sales_to__gte=today_date))
            ).
            order_by("id")
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
            select_for_update().
            filter(is_active=True, count__gt=0, id__in=products_ids)

        )
    @classmethod
    def filter_available(cls) -> QuerySet:
        """Filter available products.

        Product considered is available if is_active=True and count > 0.

        """
        return cls.objects.filter(is_active=True, count__gt=0)


    @classmethod
    def get_by_id_with_prefetch(cls, id: int) -> QuerySet:
        """Get active Product object with prefetch related data."""

        return (
            cls.objects.
            select_related("category").
            prefetch_related("images", "reviews", "tags", "specifications").
            get(id=id, is_active=True)
        )

    @classmethod
    def get_products_ids(cls) -> list:
        """Get all active and available Products ids."""

        return list(
                Product.objects.
                filter(is_active=True, count__gt=0).
                values_list("id", flat=True)
            )
