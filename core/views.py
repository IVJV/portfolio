from django.shortcuts import render
from catalogo.models import Area, Trabajo


def home(request):
    areas = Area.objects.all().order_by("order", "name")

    latest_trabajos = (
        Trabajo.objects.filter(status=Trabajo.Status.PUBLISHED)
        .order_by("-published_at", "-id")[:3]
    )

    return render(
        request,
        "core/home.html",
        {"areas": areas, "latest_trabajos": latest_trabajos},
    )


def laboratorio(request):
    return render(request, "core/laboratorio.html")
