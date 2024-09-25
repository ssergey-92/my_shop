"""App URl configuration module."""

from django.urls import path

from .apps import OrdersConfig
from .views import BasketAPIView, OrderAPIView, PaymentAPIView

app_name = OrdersConfig.name

urlpatterns = [
    path("basket", BasketAPIView.as_view(), name="basket_crud"),
    path("orders", OrderAPIView.as_view(), name="order_create_or_get_orders"),
    path(
        "order/<int:id>",
        OrderAPIView.as_view(),
        name="order_update_or_get",
    ),
    path("payment/<int:id>", PaymentAPIView.as_view(), name="payment"),
]
