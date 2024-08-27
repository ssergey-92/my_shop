from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .forms import ProfileForm
from .models import Avatar, Profile

admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model =Profile
    form = ProfileForm
    fields = ("full_name","unique_email", "unique_phone", "get_avatar_image", "avatar_src")
    readonly_fields = ('get_avatar_image',)
    verbose_name = "Personal info"
    can_delete = False
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return Profile.objects.select_related("avatar").all()

    def get_avatar_image(self, obj: Profile):
        if hasattr(obj, 'avatar') and obj.avatar.src:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.avatar.src.url)
        return "Upload your avatar below"

    get_avatar_image.short_description = 'Avatar'


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "full_name", "is_superuser", "is_staff")
    list_display_links = ("username", "full_name")
    list_filter =  ("is_active", "is_superuser", "is_staff")
    ordering = ["pk"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            User.objects.
            select_related("profile").
            select_related("profile__avatar").
            all()
        )

    def full_name(self, obj: User) -> str:
        return obj.profile.full_name

    full_name.short_description = 'FULL NAME'


admin.site.register(User, CustomUserAdmin)