"""App configuration module."""

from os import getenv as os_getenv
from threading import Thread

from django.apps import AppConfig

from .tasks_listeners import listen_order_payment_status


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self) -> None:
        """Start Redis listener in a separate daemon thread.

        Activated only for django project docker container and avoid starting
        listener func for celery workers in Celery container.
        """

        if not os_getenv("CELERY_WORKER"):
            thread = Thread(target=listen_order_payment_status)
            thread.daemon = True
            thread.start()
