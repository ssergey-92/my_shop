"""Admin models for Product."""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from common.admin import archive_items, restore_items
from products.forms import (
    ProductForm,
    ProductImageInlineForm,
    ProductReviewForm,
)
from products.models import (
    Product,
    ProductImage,
    ProductReview,
    ProductAndSpecification,
    ProductSpecification,
    ProductTag,
    ProductAndTag,
)


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    form = ProductImageInlineForm
    verbose_name = "image"
    extra = 1


class ProductTagInline(admin.StackedInline):
    model = ProductAndTag
    verbose_name = "tag"
    extra = 1


class ProductReviewInline(admin.TabularInline):
    max_num = 10
    model = ProductReview
    form = ProductReviewForm
    verbose_name = "review"
    verbose_name_plural = "Reviews (max 10)"
    extra = 0


class ProductSpecificationInline(admin.StackedInline):
    model = ProductAndSpecification
    verbose_name = "specification"
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = (archive_items, restore_items)
    list_max_show_all = 20
    form = ProductForm
    inlines = [
        ProductImageInline,
        ProductReviewInline,
        ProductTagInline,
        ProductSpecificationInline,
    ]
    list_display = (
        "id",
        "title",
        "category",
        "price",
        "count",
        "created_date",
        "is_active",
    )
    readonly_fields = ("id", "created_date", "rating")
    list_display_links = ("id", "title")
    list_filter = ("is_active", "count")
    ordering = ("is_active", "category", "price", "count", "created_date")
    search_fields = ("id", "price", "count", "created_date")
    fieldsets = (
        ("SOFT DELETE", {"fields": ("is_active",)}),
        (
            "DETAILS",
            {
                "fields": (
                    "id",
                    "title",
                    "category",
                    "shot_description",
                    "full_description",
                    "created_date",
                )
            }
        ),
        ("QUALITY", {"fields": ("rating", "sorting_index", "is_limited")}),
        ("PRICE AND QUANTITY", {"fields": ("price", "count")}),
        ("DELIVERY", {"fields": ("free_delivery",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method.Get query set with select/prefetch related objects."""

        return (
            Product.objects.
            select_related("category").
            prefetch_related(
                "images",
                "productandtag_set",
                "productandspecification_set",
                "reviews",
            )
        )

    def delete_queryset(self, request: HttpRequest, queryset:QuerySet) -> None:
        """Override method. Instances are archived instead of deletion."""

        queryset.update(is_active=False)

    def delete_model(self, request: HttpRequest, obj: Product) -> None:
        """Override method. Instance is archived instead of deletion."""

        obj.is_active = False
        obj.save()
