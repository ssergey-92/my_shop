"""Admin model for order delivery type."""

from django.contrib import admin

from orders.forms import DeliveryTypeForm
from orders.models import DeliveryType


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    """Model admin class for 'DeliveryType' model."""

    model = DeliveryType
    form = DeliveryTypeForm
    list_display = ("id", "name", "price", "free_delivery_order_price")
    list_display_links = ("id", "name")
    list_max_show_all = 20
    readonly_fields = ("id",)
    ordering = ("id", "name", "price", "free_delivery_order_price")
    search_fields = ("id", "name", "price", "free_delivery_order_price")
    fieldsets = (
        (
            "DETAILS",
            {"fields": ("id", "name", "price", "free_delivery_order_price")},
        ),
    )
