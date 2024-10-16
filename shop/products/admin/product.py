"""Admin models for products."""

from django.contrib import admin
from django.db.models import QuerySet, Sum
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
    """StackedInline admin class for 'ProductImage' model.

    Class is design to use as inlines for 'Product' model admin.

    """
    model = ProductImage
    form = ProductImageInlineForm
    verbose_name = "image"
    extra = 1


class ProductTagInline(admin.StackedInline):
    """StackedInline admin class for 'ProductAndTag' model.

    Class is design to use as inlines for 'Product' model admin.

    """
    model = ProductAndTag
    verbose_name = "tag"
    extra = 1


class ProductReviewInline(admin.TabularInline):
    """StackedInline admin class for 'ProductReview' model.

    Class is design to use as inlines for 'Product' model admin.

    """
    max_num = 10
    model = ProductReview
    form = ProductReviewForm
    verbose_name = "review"
    verbose_name_plural = "Reviews (max 10)"
    extra = 0


class ProductSpecificationInline(admin.StackedInline):
    """StackedInline admin class for 'ProductAndSpecification' model.

    Class is design to use as inlines for 'Product' model admin.

    """
    model = ProductAndSpecification
    verbose_name = "specification"
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Model admin class for 'Product' model."""

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
    readonly_fields = ("id", "created_date", "rating", "get_sold_products")
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
            },
        ),
        ("QUALITY", {"fields": ("rating", "sorting_index", "is_limited")}),
        (
            "PRICE AND QUANTITY",
            {"fields": (
                "price", "received_amount", "get_sold_products", "count",
                ),
            },
        ),
        ("DELIVERY", {"fields": ("free_delivery",)}),
        (
            "SALES",
            {"fields": ("is_sales", "sales_from", "sales_to", "sales_price")},
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get query set with select/prefetch related objects."""

        return (
            Product.objects.
            select_related("category").
            prefetch_related(
                "images",
                "productandtag_set",
                "productandspecification_set",
                "reviews",
                "orders",
            )
        )

    def delete_queryset(self, request: HttpRequest, queryset:QuerySet) -> None:
        """Override method. Instances are archived instead of deletion."""

        queryset.update(is_active=False)

    def delete_model(self, request: HttpRequest, obj: Product) -> None:
        """Override method. Instance is archived instead of deletion."""

        obj.is_active = False
        obj.save()

    def save_model(
        self,
        request: HttpRequest,
        obj: Product,
        form: ProductForm,
        change: bool,
    ):
        """Add extra logic for saving new instance.

        If new Product is created set remains == received Product quantity.

        """
        if not obj.id:  # new Product created
            obj.received_amount = obj.count

        super().save_model(request, obj, form, change)

    def get_sold_products(self, obj: Product) -> int:
        """Get parent category."""

        return (
            obj.orderandproduct_set.
            aggregate(total_sailed=Sum("total_quantity"))
            ["total_sailed"]
        )

    get_sold_products.short_description = "Sold products"
