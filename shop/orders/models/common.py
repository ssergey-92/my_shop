from django.apps import apps

Product = apps.get_model("products", "Product", require_ready=False)