"""Admin models for specifications of products."""

from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.fields.files import FileField
from django.http import HttpRequest

from products.models import (
    Product,
    ProductSpecification,
    ProductAndSpecification,
)


class ProductInline(admin.StackedInline):
    """StackedInline admin class for 'Product' model.

    Class is design to use as inlines for 'ProductSpecification' model admin.

    """
    model = ProductAndSpecification
    verbose_name = "product"
    extra = 2

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method. Add filtering to return only active products."""

        qs = super().get_queryset(request)
        return qs.filter(product__is_active=True)

    def formfield_for_foreignkey(
            self, db_field: {FileField.formfield}, request: HttpRequest, **kwargs
    ) -> Any:
        """Override method. Filter product_id to show active only."""

        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """Model admin class for 'ProductSpecification' model."""

    model = ProductSpecification
    actions = ("delete_selected",)
    inlines = (ProductInline,)
    list_display = ("id", "name", "value")
    readonly_fields = ("id",)
    list_display_links = ("id", "name")
    ordering = ("id", "name", "value")
    search_fields = ("id", "name", "value")
    fieldsets = (("DETAILS", {"fields": ("id", "name", "value")}),)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method. Get query set with prefetch related objects."""

        return ProductSpecification.objects.prefetch_related("products")
