# core/urls.py
from django.urls import path
from .views import home, laboratorio

urlpatterns = [
    path("", home, name="home"),
    path("laboratorio/", laboratorio, name="laboratorio"),
]
