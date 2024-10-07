"""Admin model for order payment type."""

from django.contrib import admin

from orders.models import PaymentType


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    """Model admin class for 'PaymentType' model."""

    model = PaymentType
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    list_max_show_all = 20
    readonly_fields = ("id",)
    ordering = ("id", "name")
    search_fields = ("id", "name")
    fieldsets = (("DETAILS", {"fields": ("id", "name")}),)