# catalogo/views.py
from django.shortcuts import get_object_or_404, render
from .models import Area, Trabajo, Documento


def areas(request):
    areas_qs = Area.objects.all().order_by("order", "name")
    return render(request, "catalogo/areas.html", {"areas": areas_qs})


def area_detail(request, area_slug):
    area = get_object_or_404(Area, slug=area_slug)
    trabajos = (
        area.trabajos
        .filter(status=Trabajo.Status.PUBLISHED)
        .order_by("-published_at", "-created_at")
    )
    return render(request, "catalogo/area_detail.html", {"area": area, "trabajos": trabajos})


def trabajo_detail(request, area_slug, trabajo_slug):
    trabajo = get_object_or_404(Trabajo, area__slug=area_slug, slug=trabajo_slug)

    # Highlights: keep existing behavior
    highlights = trabajo.highlight_items.all().order_by("order", "id")

    # Documents grouped by category (ordered)
    docs_tech = trabajo.documentos.filter(doc_type=Documento.DocType.METHODOLOGY).order_by("order", "id")
    docs_stats = trabajo.documentos.filter(doc_type=Documento.DocType.DATA).order_by("order", "id")
    docs_viewers = trabajo.documentos.filter(doc_type=Documento.DocType.OTHER).order_by("order", "id")

    return render(
        request,
        "catalogo/trabajo_detail.html",
        {
            "trabajo": trabajo,
            "highlights": highlights,
            "docs_tech": docs_tech,
            "docs_stats": docs_stats,
            "docs_viewers": docs_viewers,
        },
    )


def trabajo_documentos(request, area_slug, trabajo_slug):
    trabajo = get_object_or_404(Trabajo, area__slug=area_slug, slug=trabajo_slug)
    documentos = trabajo.documentos.all().order_by("order", "id")
    return render(request, "catalogo/trabajo_documentos.html", {"trabajo": trabajo, "documentos": documentos})
