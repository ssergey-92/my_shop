import traceback
from typing import Any

from django.contrib import admin, messages
from django.db.models import QuerySet, F, Q
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.files import FileField
from django.http import HttpRequest

from common.admin import archive_items, restore_items
from common.custom_logger import app_logger
from orders.exceptions import OrderException
from orders.forms import OrderForm, OrderedProductInlineForm
from orders.models import (
    Category,
    Order,
    OrderAndProduct,
    Product,
    OrderStatus,
)
from orders.services import DeliveryService


class OrderProductInline(admin.StackedInline):
    model = OrderAndProduct
    verbose_name = "Product"
    verbose_name_plural = "Products"
    readonly_fields = ["total_price"]
    form = OrderedProductInlineForm
    extra = 1

    def formfield_for_foreignkey(
            self,
            db_field: {FileField.formfield},
            request: HttpRequest,
            **kwargs,
    ) -> Any:
        """Override method for product field else return super method.

        Select available products only for new model 'Order' (OrderAdmin)
        and additionally select unavailable products if there are included
        in created order.

        """
        if db_field.name == "product":
            order_id = request.resolver_match.kwargs.get("object_id")
            if order_id:
                products_ids = list(
                    OrderAndProduct.objects.filter(order_id=order_id).
                    values_list("product_id", flat=True)
                )
                kwargs["queryset"] = (
                    Product.objects.filter(
                        Q(id__in=products_ids) |
                        (Q(is_active=True) & Q(count__gte=1))
                        )
                )
            else:
                kwargs["queryset"] = Product.filter_available()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderProductInline,)
    actions = (archive_items, restore_items)
    form = OrderForm
    list_max_show_all = 20
    verbose_name = "Order"
    verbose_name_plural = "Orders"
    list_display = (
        "id",
        "created_by",
        "created_at",
        "city",
        "display_total_cost",
        "display_status",
        "is_active",
    )
    readonly_fields = (
        "id", "created_at", "products_cost", "delivery_cost", "total_cost",
    )
    list_display_links = ("id", "created_by")
    list_filter = ("is_active",)
    ordering = ("id", "is_active", "created_by", "created_at")
    search_fields = (
        "id",
        "created_by__profile__full_name",
        "status__name",
        "city",
    )
    fieldsets = (
        ("SOFT DELETE", {"fields": ("is_active",)}),
        ("DETAILS", {"fields": ("id", "status", "created_by", "created_at",)}),
        ("COSTS", {"fields": ("products_cost", "delivery_cost", "total_cost")}),
        ("PAYMENT", {"fields": ("payment_type", "payment_comment")}),
        (
            "RECEIVER",
            {"fields": ("receiver_fullname", "receiver_email", "receiver_phone")},
        ),
        ("DELIVERY", {"fields": ("delivery_type", "city", "address")}),
    )

    def display_status(self, obj: Order) -> str:
        """Override default field status to display satus name."""

        return obj.status.name

    display_status.short_description = "Status"
    display_status.admin_order_field = "display_status"

    def display_total_cost(self, obj: Order) -> str:
        """Override default field total cost for custom field naming. """

        return obj.total_cost

    display_total_cost.short_description = "Total Cost: $"
    display_total_cost.admin_order_field = "display_total_cost"

    def delete_model(self, request: HttpRequest, obj: Order) -> None:
        """Override method. Model instance is archived instead of deletion."""

        obj.is_active = False
        obj.save()

    def delete_queryset(
            self, request: HttpRequest, queryset: QuerySet,
    ) -> None:
        """Override method. Instances are archived instead of deletion."""

        queryset.update(is_active=False)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs,
    ) -> Any:
        """Override method. Filter Categories to show active only."""

        if db_field.name == "status":
            kwargs["queryset"] = OrderStatus.objects.order_by("id").all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get queryset with annotate and select/prefetch related objects."""

        return (
            Order.objects.
            select_related(
                "created_by", "delivery_type", "payment_type", "status",
            ).
            prefetch_related("products").
            annotate(
                display_status=F("status__name"),
                display_total_cost=F("total_cost"),
            )
        )

    @staticmethod
    def _crud_ordered_product_inline_form(
            form: OrderedProductInlineForm, formset,
    ) -> None:
        """Handle CRUD for form instance and update formset attributes."""

        if form.cleaned_data["DELETE"]:  # Delete
            formset.deleted_objects.append(form.instance)
            form.instance.custom_delete()
        elif not form.cleaned_data["id"]:  # Create
            form.instance.custom_create()
            formset.new_objects.append(form.instance)
        elif form.has_changed():  # Update
            form.instance.custom_update(
                form.cleaned_data["previous_total_price"],
                form.cleaned_data["previous_total_qnty"],
            )
            formset.changed_objects.append(
                (form.instance, form.changed_data),
            )

    def _save_ordered_product_inline_formset(
            self, request: HttpRequest, form, formset,
    ) -> None:
        """Handle CRUD for form 'OrderedProductInlineForm' from formset.

        Call handling function for CRUD form. Call (self.message_user)
        to notify user in case some error. Update Order delivery_cost and
        total_cost in case changes in form instances from formset.

        """
        count_changes = 0
        error_msg = ""
        for i_form in formset:
            if not (i_form.is_valid() and i_form.has_changed()):
                continue
            instance = i_form.instance
            instance.total_price = i_form.cleaned_data["total_price"]
            instance.total_quantity = i_form.cleaned_data["total_quantity"]
            try:
                self._crud_ordered_product_inline_form(i_form, formset)
            except OrderException as exc:
                error_msg = exc
            except Product.DoesNotExist:
                error_msg = (
                    f"Product {instance.product.title} is not available for "
                    f"editing to order!"
                )
            except Exception:
                app_logger.error(traceback.format_exc())
                error_msg = (
                    f"Error while handling product '{instance.product.title}' "
                    f"in order # {instance.order.id}. Kindly try again later!"
                )
            finally:
                if error_msg:
                    self.message_user(request, error_msg, messages.ERROR)
                else:
                    count_changes += 1

        if count_changes > 0:
            Order.reset_delivery_related_costs(
                form.instance.id,
                DeliveryService.recount_delivery_cost(form.instance.id),
            )

    def save_formset(
            self, request: HttpRequest, form, formset, change: bool,
    ) -> None:
        """Call super or custom method depending on formset model."""

        if formset.model == OrderProductInline.model:
            # Mandatory to init formset object related attributes
            formset.new_objects = []
            formset.changed_objects = []
            formset.deleted_objects = []
            self._save_ordered_product_inline_formset(request, form, formset)
        else:
            super().save_formset(request, form, formset, change)

    def save_model(self, request, obj: Order, form, change):
        """Recount order delivery and total cost and call super method."""

        obj.delivery_cost = DeliveryService.count_cost(
            obj.products_cost, obj.delivery_type,
        )
        obj.total_cost = obj.products_cost + obj.delivery_cost
        super().save_model(request, obj, form, change)


