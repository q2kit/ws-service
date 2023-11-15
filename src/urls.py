from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView

from src.views import *
from src.admin import admin_site


urlpatterns = [
    path("", index, name="index"),
    path("api/refresh_secret_key/<str:project>/", refresh_secret_key, name="refresh_secret_key"),
    path("dashboard/", admin_site.urls),
    path("signup/", signup, name="signup"),
    path("verify", verify_email, name="verify"),
    path("token/<str:secret_key>", create_example_token, name="create_example_token"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password_reset/<str:token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
