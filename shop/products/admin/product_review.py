"""Admin model for reviews of product."""

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignKey
from django.http import HttpRequest


from products.models import Product, ProductReview
from products.forms import ProductReviewForm


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Model admin class for 'ProductReview' model."""

    model = ProductReview
    actions = ("delete_selected",)
    form = ProductReviewForm
    list_display = ("id", "product", "rate", "author", "date")
    readonly_fields = ("id", "date")
    list_display_links = ("id", "product")
    ordering = ("id", "product", "rate", "author", "date")
    search_fields = ("id", "rate", "author", "date")
    fieldsets = (
        ("AUTHOR", {"fields": ("author", "email")}),
        ("PRODUCT", {"fields": ("product",)}),
        ("RATING", {"fields": ("rate",)}),
        ("DESCRIPTION", {"fields": ("id", "text", "date")}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method. Get query set with select related object."""

        return ProductReview.objects.select_related("product")

    def formfield_for_foreignkey(
            self, db_field: ForeignKey, request: HttpRequest, **kwargs,
    ) -> Any:
        """Override method. Filter product_id to show active only."""

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
