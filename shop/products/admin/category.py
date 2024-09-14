"""Admin models for Category."""

from typing import Any, Optional, Union

from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignKey
from django.http import HttpRequest

from common.admin import archive_items, restore_items
from django.utils.html import format_html
from django.utils.safestring import SafeString

from products.forms import (
    CategoryForm,
    CategoryInlineForm,
    CategoryImageForm,
)

from products.models import Category, CategoryImage
from products.services import category_max_nesting_level


class SubcategoryInline(admin.StackedInline):
    model = Category
    form = CategoryInlineForm
    verbose_name = "subcategories"
    fields = ("title", "get_subcategory_image", "image", "is_active")
    readonly_fields = ("id", "get_subcategory_image")
    can_delete = False
    extra = 0

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        """Add restriction to add subcategory.

        If category is not created or category nesting level is reached
        max nesting limit then restrict auditing subcategories.

        """

        if (
                not obj or
                Category.get_nesting_level(obj.id) >= category_max_nesting_level
        ):
            return False

        return True

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Add additional filtering (is_active=True) to class super method."""

        qs = super().get_queryset(request)
        return qs.filter(is_active=True)

    def get_subcategory_image(self, obj: Category) -> Union[str, SafeString]:
        """Create extra read only field with subcategory image if existed.

        Args:
            obj (Profile): Profile object.

        Returns:
            Union[str, SafeString]: Avatar image if existed else msg.

        """
        if hasattr(obj, "image") and obj.image.src:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.src.url,
            )
        return "Upload your image below"

    get_subcategory_image.short_description = "Set image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = (archive_items, restore_items)
    list_max_show_all = 20
    inlines = (SubcategoryInline,)
    form = CategoryForm
    verbose_name = "Category"
    verbose_name_plural = "Categories"
    list_display = (
        "id",
        "title",
        "get_root_category",
        "get_parent_category",
        "get_nesting_depth",
        "get_subcategories",
        "is_active",
    )
    readonly_fields = (
        "id",
        "get_root_category",
        "get_parent_category",
        "get_nesting_depth",
        "get_subcategories",
        "get_category_image"
    )
    list_display_links = ("id", "title")
    list_filter = ("is_active",)
    ordering = ("id", "is_active", "parent_id")
    search_fields = ("id", "title")
    fieldsets = (
        ("SOFT DELETE", {"fields": ("is_active",)}),
        (
            "DETAILS",
            {"fields":
                 ("id", "title", "parent", "get_category_image", "image")
            },
         ),
        (
            "EXTRA",
            {"fields":
                ("get_root_category", "get_nesting_depth", "get_subcategories")
            },
        ),
    )

    def delete_model(self, request: HttpRequest, obj: Category) -> None:
        """Override method. Model instance is archived instead of deletion."""

        obj.is_active = False
        obj.save()

    def delete_queryset(self, request: HttpRequest, queryset:QuerySet) -> None:
        """Override method. Instances are archived instead of deletion."""

        queryset.update(is_active=False)

    def formfield_for_foreignkey(
            self, db_field: ForeignKey, request: HttpRequest, **kwargs,
    ) -> Any:
        """Override method. Filter parent_id to show active only."""

        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method. Get queryset with select/prefetch related objects."""

        return (
            Category.objects.
            select_related("image", "parent").
            prefetch_related("subcategories")
        )

    def get_parent_category(self, obj: Category) -> Optional[int]:
        """Get parent category."""

        return obj.parent.id if obj.parent else None

    get_parent_category.short_description = "Parent id"

    def get_subcategories(self, obj: Category) -> Optional[str]:
        """Get str of subcategories ids."""

        subcategories = obj.subcategories.filter(is_active=True).all()
        if subcategories:
            return ", ".join([str(category.id) for category in subcategories])
        return None

    get_subcategories.short_description = "Subcategories ids"

    def get_nesting_depth(self, obj: Category) -> int:
        """Get nesting level of Category."""

        return Category.get_nesting_level(obj.id)

    get_nesting_depth.short_description = "Nesting level"


    def get_root_category(self, obj: Category) -> Optional[str]:
        """Get root category."""

        return obj.get_root_category_id()

    get_root_category.short_description = "Root id"

    def get_category_image(self, obj: Category) -> Union[str, SafeString]:
        """Create extra read only field with category image if existed.

        Args:
            obj (Profile): Profile object.

        Returns:
            Union[str, SafeString]: Avatar image if existed else msg.

        """
        if hasattr(obj, "image") and obj.image.src:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.src.url,
            )
        return "Upload your image below"

    get_category_image.short_description = "Set image"
