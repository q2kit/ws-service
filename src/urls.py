from django.contrib import admin
from django.urls import path

from src.views import *

admin.site.site_header = "Websocket Service Admin"
admin.site.site_title = "Websocket Service Admin Portal"
admin.site.index_title = "Welcome to Websocket Service Portal"
admin.site.site_url = None
admin.site.site_header = None


urlpatterns = [
    path("admin/api/refresh_secret_key/<str:project_id>/", refresh_secret_key, name="refresh_secret_key"),
    path("admin/", admin.site.urls, name="admin"),
    path("token/<str:secret_key>", create_example_token, name="create_example_token"),
]
