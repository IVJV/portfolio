# catalogo/context_processors.py
from __future__ import annotations

from .models import Area


def nav_areas(request):
    # Used by templates/base.html for the "Estadísticas" dropdown
    return {"nav_areas": Area.objects.all().order_by("order", "name")}
