"""App admin models for django admin panel."""

from typing import Union, Optional

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .forms import ProfileForm
from .models import Profile
from common.admin import archive_items, restore_items

class ProfileInline(admin.StackedInline):
    """Class Profile Inline for django admin panel."""

    model = Profile
    form = ProfileForm
    fields = (
        "full_name",
        "unique_email",
        "unique_phone",
        "get_avatar_image",
        "avatar_src",
    )
    readonly_fields = ("get_avatar_image",)
    verbose_name = "Personal info"
    can_delete = False
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get query set with select related object Avatar."""

        return Profile.objects.select_related("avatar").all()

    def get_avatar_image(self, obj: Profile) -> Union[str, SafeString]:
        """Create extra read only field with avatar image if existed."""

        if hasattr(obj, "avatar") and obj.avatar.src:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.avatar.src.url,
            )
        return "Upload your avatar below"

    get_avatar_image.short_description = "Avatar"


class CustomUserAdmin(UserAdmin):
    """Class Custom user admin for build in clas User in django admin panel."""

    model = User
    inlines = [ProfileInline]
    actions = (archive_items, restore_items)
    list_display = (
        "id", "username", "full_name", "is_superuser", "is_staff", "is_active",
    )
    list_display_links = ("username", "full_name")
    list_filter = ("is_active", "is_superuser", "is_staff")
    ordering = ("id", "username", "is_superuser", "is_staff")
    fieldsets = (
        ("SOFT DELETE", {"fields": ("is_active",)}),
        ("DETAILS", {"fields": ("username", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    def full_name(self, obj: User) -> Optional[str]:
        """Create extra field with user's full name."""

        return obj.profile.full_name

    full_name.short_description = "FULL NAME"
    full_name.admin_order_field = "full_name"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get query set with select related objects Profile and Avatar."""

        qs = super().get_queryset(request)
        return qs.select_related("profile", "profile__avatar")


    def delete_model(self, request: HttpRequest, obj: User) -> None:
        """Override method. Model instance is archived instead of deletion."""

        obj.is_active = False
        obj.save()

    def delete_queryset(
            self, request: HttpRequest, queryset: QuerySet,
    ) -> None:
        """Override method. Instances are archived instead of deletion."""

        queryset.update(is_active=False)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
