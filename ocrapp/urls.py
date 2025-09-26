from django.urls import path
from .views import *

urlpatterns = [
    path('upload/',verify_files)
]
