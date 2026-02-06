# catalogo/models.py
from __future__ import annotations

import os
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


# ------------------------------------------------------------
# Upload paths (keep names stable for old migrations)
# ------------------------------------------------------------

def _safe_slug(value: Optional[str], fallback: str = "unknown") -> str:
    value = (value or "").strip()
    return value if value else fallback


def upload_trabajo_image_to(instance: "Trabajo", filename: str) -> str:
    # Keep callable name stable (old migrations might reference it)
    area_slug = _safe_slug(getattr(instance.area, "slug", None), "area")
    trabajo_slug = _safe_slug(getattr(instance, "slug", None), "trabajo")
    name = os.path.basename(filename)
    return f"catalogo/trabajos/{area_slug}/{trabajo_slug}/{name}"


def upload_documento_file_to(instance: "Documento", filename: str) -> str:
    trabajo = getattr(instance, "trabajo", None)
    area_slug = _safe_slug(getattr(getattr(trabajo, "area", None), "slug", None), "area")
    trabajo_slug = _safe_slug(getattr(trabajo, "slug", None), "trabajo")
    name = os.path.basename(filename)
    return f"catalogo/documentos/{area_slug}/{trabajo_slug}/{name}"


def upload_document_to(instance: "Documento", filename: str) -> str:
    # Old migrations reference: catalogo.models.upload_document_to
    return upload_documento_file_to(instance, filename)


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

class Area(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("catalogo:area_detail", args=[self.slug])


class Trabajo(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="trabajos")

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)

    tagline = models.CharField(max_length=220, blank=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)

    # IMPORTANT: this is a real DB column (needed for your fixture)
    highlights = models.TextField(
        blank=True,
        help_text="Optional. One highlight per line (simple bullets).",
    )

    app_url = models.URLField(blank=True)

    # --- Tooltips (admin) via help_text ---
    image = models.ImageField(
        upload_to=upload_trabajo_image_to,
        blank=True,
        null=True,
        help_text=(
            "Portada (imagen principal del trabajo). "
            "Se recomienda PNG/JPG nítido; ideal sin fondo. "
            "Usa un formato apaisado si es posible (ej.: 1200×600 o 1600×800) para buena vista en el carrusel."
        ),
    )
    image_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(
        blank=True,
        help_text=(
            "Miniatura/thumbnail (URL). "
            "Se recomienda imagen ligera y clara; ideal sin fondo. "
            "Tamaño sugerido: 600×600 o 800×800 (cuadrada) o 800×450 (apaisada), según tu diseño."
        ),
    )

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)

    is_featured = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        constraints = [
            models.UniqueConstraint(fields=["area", "slug"], name="uq_trabajo_area_slug"),
        ]
        verbose_name = "Work"
        verbose_name_plural = "Works"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("catalogo:trabajo_detail", args=[self.area.slug, self.slug])

    @property
    def hero_image(self) -> str:
        # Used by templates/core/home.html (t.hero_image)
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        if self.image_url:
            return self.image_url
        if self.thumbnail_url:
            return self.thumbnail_url
        return ""

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Highlight(models.Model):
    # IMPORTANT: avoid name clash with Trabajo.highlights TextField
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, related_name="highlight_items")
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Highlight"
        verbose_name_plural = "Highlights"

    def __str__(self) -> str:
        return f"{self.label}: {self.value}" if self.value else self.label


class Documento(models.Model):
    class DocType(models.TextChoices):
        METHODOLOGY = "metodologico", "Technical document"
        DATA = "datos", "Statistics and reports"
        OTHER = "otro", "Viewers"

    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, related_name="documentos")

    title = models.CharField(max_length=220)
    doc_type = models.CharField(max_length=30, choices=DocType.choices, default=DocType.METHODOLOGY, db_index=True)

    file = models.FileField(upload_to=upload_document_to, blank=True, null=True)
    url = models.URLField(blank=True)

    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.file and not self.url:
            raise ValidationError("Provide either a file upload or a URL for the document.")
