"""URL configuration for 'auth' app of project 'shop'."""

from django.urls import path

from .apps import AuthConfig
from .views import SignInView, SignOutView, SignUpView


app_name = AuthConfig.name

urlpatterns = [
    path('sign-in', SignInView.as_view(), name="sign_in"),
    path("sign-up", SignUpView.as_view(), name="sign_up"),
    path("sign-out", SignOutView.as_view(), name="sign_out"),
]
