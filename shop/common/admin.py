from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

admin.site.site_header = "My_Shop admin panel"
admin.site.index_title = "Admin Panel"
admin.site.site_title = "My_Shop"

admin.site.disable_action("delete_selected")


@admin.action(description="Restore items")
def restore_items(self, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(is_active=True)


@admin.action(description="Archive items")
def archive_items(self, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(is_active=False)
