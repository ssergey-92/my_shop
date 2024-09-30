"""Admin model for CategoryImage."""

from typing import Optional

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from products.models import Category, CategoryImage
from products.forms import (
    CategoryForm,
    CategoryInlineForm,
    CategoryImageForm,
)


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    model = CategoryImage
    actions = ("delete_selected",)
    form = CategoryImageForm
    verbose_name = "Image"
    verbose_name_plural = "Images"
    list_display = ("id", "alt", "src", "get_categories_titles")
    readonly_fields = ("id", "get_categories_titles",)
    list_display_links = ("id", "alt")

    ordering = ("id", "src", "alt")
    search_fields = ("id", "src", "alt")
    fieldsets = (
        ("DETAILS", {"fields": ("id", "src", "alt")}),
        ("USED BY", {"fields": ("get_categories_titles",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Override method get query set with prefetch related objects."""

        return CategoryImage.objects.prefetch_related("categories")

    def get_categories_titles(self, obj: CategoryImage) -> Optional[str]:
        """Get list of categories titles for image."""

        categories = obj.categories.filter(is_active=True).all()
        if categories:
            return ", ".join([str(category.title) for category in categories])
        return None

    get_categories_titles.short_description = "Categories titles"
