"""App URl configuration module."""

from django.urls import path

from .apps import OrdersConfig

app_name = OrdersConfig.name

urlpatterns = []