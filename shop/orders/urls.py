"""App URl configuration module."""

from django.urls import path

from .apps import OrdersConfig
from .views import BasketAPIView

app_name = OrdersConfig.name

urlpatterns = [
    path("basket", BasketAPIView.as_view(), name="basket_crud"),
]