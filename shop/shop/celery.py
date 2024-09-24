from os import environ as os_environ

from celery import Celery


os_environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
app = Celery("shop")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
