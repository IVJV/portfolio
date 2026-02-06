# catalogo/urls.py
from django.urls import path
from . import views

app_name = "catalogo"

urlpatterns = [
    path("areas/", views.areas, name="areas"),
    path("areas/<slug:area_slug>/", views.area_detail, name="area_detail"),
    path("<slug:area_slug>/<slug:trabajo_slug>/", views.trabajo_detail, name="trabajo_detail"),
    path("<slug:area_slug>/<slug:trabajo_slug>/documentos/", views.trabajo_documentos, name="trabajo_documentos"),
]
