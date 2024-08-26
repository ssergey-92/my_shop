"""URL configuration for shop project."""
from os import getenv as os_getenv

from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from common import admin as common_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authorization.urls')),
    path('api/', include('user_profile.urls')),
    path("", include("frontend.urls")),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

if os_getenv("SHOP_TESTING", None) != "True":
    urlpatterns.extend(debug_toolbar_urls())