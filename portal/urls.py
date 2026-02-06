from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Language switch endpoint (required)
    path("i18n/", include("django.conf.urls.i18n")),

    path("admin/", admin.site.urls),
    path("", include("core.urls")),

    # Namespaced include so `{% url 'catalogo:...' %}` works
    path("", include(("catalogo.urls", "catalogo"), namespace="catalogo")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
