"""URL configuration for shop project."""

from django.contrib import admin
from django.contrib.messages import api
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth.urls')),
    path("", include("frontend.urls")),
]
