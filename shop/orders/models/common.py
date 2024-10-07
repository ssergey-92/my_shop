"""Module for importing db models from other apps."""

from django.apps import apps

Product = apps.get_model("products", "Product", require_ready=False)
Category = apps.get_model("products", "Category", require_ready=False)
