from django.contrib import admin
from django.urls import path
from src.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('create-project/', create_project, name='create-project'),
    path('', dashboard, name='dashboard'),
    path('project/<str:project_id>/', project_details, name='project_details'),

    path('token/<str:secret_key>', create_example_token, name='create_example_token'),
]
