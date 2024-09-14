"""Admin model for ProductImage."""

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignKey
from django.http import HttpRequest

from products.models import Product, ProductImage
from products.forms import (
    ProductImageInlineForm,
)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    model = ProductImage
    actions = ("delete_selected",)
    form = ProductImageInlineForm
    verbose_name = "Image"
    verbose_name_plural = "Images"
    list_display = ("id", "alt", "src", "product")
    readonly_fields = ("id",)
    list_display_links = ("id", "alt")

    ordering = ("id", "src", "alt")
    search_fields = ("id", "src", "alt")
    fieldsets = (
        ("DETAILS", {"fields": ("id", "src", "alt", "product")}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method. Get query set with select related objects."""

        return ProductImage.objects.select_related("product")

    def formfield_for_foreignkey(
            self, db_field: ForeignKey, request: HttpRequest, **kwargs,
    ) -> Any:
        """Override method. Filter product_id to show active only."""

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

