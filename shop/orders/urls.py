"""App URl configuration module."""

from django.urls import path

from .apps import OrdersConfig
from .views import BasketView, OrderView, PaymentView

app_name = OrdersConfig.name

urlpatterns = [
    path("basket", BasketView.as_view(), name="basket_crud"),
    path("orders", OrderView.as_view(), name="order_create_or_get_orders"),
    path(
        "order/<int:id>",
        OrderView.as_view(),
        name="order_update_or_get",
    ),
    path("payment/<int:id>", PaymentView.as_view(), name="payment"),
]
