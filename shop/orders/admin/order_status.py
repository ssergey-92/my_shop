"""Admin model for order status type."""

from django.contrib import admin

from orders.models import OrderStatus


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """Model admin class for 'OrderStatus' model."""

    model = OrderStatus
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    list_max_show_all = 20
    readonly_fields = ("id",)
    ordering = ("id", "name")
    search_fields = ("id", "name")
    fieldsets = (("DETAILS", {"fields": ("id", "name")}),)
