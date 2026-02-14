# catalogo/models.py
from __future__ import annotations

import os
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.files.storage import Storage, default_storage
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.deconstruct import deconstructible


# ------------------------------------------------------------
# Custom RAW storage for documents (Cloudinary in production)
# ------------------------------------------------------------

@deconstructible
class DocumentRawStorage(Storage):
    """
    - Production (CLOUDINARY_URL present): Cloudinary RAW storage
    - Local (no CLOUDINARY_URL): Django default storage (filesystem)
    """

    def __init__(self):
        super().__init__()
        self._backend = None

    def _get_backend(self):
        if self._backend is not None:
            return self._backend

        cloudinary_url = os.environ.get("CLOUDINARY_URL", "").strip()
        if cloudinary_url:
            from cloudinary_storage.storage import RawMediaCloudinaryStorage
            self._backend = RawMediaCloudinaryStorage()
        else:
            self._backend = default_storage

        return self._backend

    def _open(self, name, mode="rb"):
        return self._get_backend()._open(name, mode)

    def _save(self, name, content):
        return self._get_backend()._save(name, content)

    def delete(self, name):
        return self._get_backend().delete(name)

    def exists(self, name):
        return self._get_backend().exists(name)

    def listdir(self, path):
        return self._get_backend().listdir(path)

    def size(self, name):
        return self._get_backend().size(name)

    def url(self, name):
        return self._get_backend().url(name)

    def get_available_name(self, name, max_length=None):
        return self._get_backend().get_available_name(name, max_length=max_length)

    def path(self, name):
        backend = self._get_backend()
        if hasattr(backend, "path"):
            return backend.path(name)
        raise NotImplementedError("This storage backend does not support absolute paths.")


# ------------------------------------------------------------
# Upload paths (CANONICAL STRUCTURE)
# ------------------------------------------------------------

def _safe_slug(value: Optional[str], fallback: str = "unknown") -> str:
    value = (value or "").strip()
    return value if value else fallback


def upload_trabajo_image_to(instance: "Trabajo", filename: str) -> str:
    """
    Canon:
      catalogo/images/<area_slug>/<trabajo_slug>/<archivo>
    """
    area_slug = _safe_slug(getattr(instance.area, "slug", None), "area")
    trabajo_slug = _safe_slug(getattr(instance, "slug", None), "trabajo")
    name = os.path.basename(filename)
    return f"catalogo/images/{area_slug}/{trabajo_slug}/{name}"


def upload_documento_file_to(instance: "Documento", filename: str) -> str:
    """
    Canon:
      catalogo/docs/<area_slug>/<trabajo_slug>/<archivo>
    """
    trabajo = getattr(instance, "trabajo", None)
    area_slug = _safe_slug(getattr(getattr(trabajo, "area", None), "slug", None), "area")
    trabajo_slug = _safe_slug(getattr(trabajo, "slug", None), "trabajo")
    name = os.path.basename(filename)
    return f"catalogo/docs/{area_slug}/{trabajo_slug}/{name}"


def upload_document_to(instance: "Documento", filename: str) -> str:
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

    highlights = models.TextField(blank=True)

    app_url = models.URLField(blank=True)

    image = models.ImageField(
        upload_to=upload_trabajo_image_to,
        max_length=500,  # IMPORTANT: prevent Postgres varchar(100) overflow for long paths
        blank=True,
        null=True,
    )

    image_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        constraints = [
            models.UniqueConstraint(fields=["area", "slug"], name="uq_trabajo_area_slug"),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("catalogo:trabajo_detail", args=[self.area.slug, self.slug])

    @property
    def hero_image(self) -> str:
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


# ------------------------------------------------------------
# RESTORED MODEL (THIS FIXES PRODUCTION)
# ------------------------------------------------------------

class Highlight(models.Model):
    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name="highlight_items",
    )
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"{self.label}: {self.value}" if self.value else self.label


class Documento(models.Model):

    class DocType(models.TextChoices):
        METHODOLOGY = "metodologico", "Technical document"
        DATA = "datos", "Statistics and reports"
        OTHER = "otro", "Viewers"

    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name="documentos",
    )

    title = models.CharField(max_length=220)
    doc_type = models.CharField(max_length=30, choices=DocType.choices, default=DocType.METHODOLOGY)

    file = models.FileField(
        upload_to=upload_document_to,
        storage=DocumentRawStorage(),
        max_length=500,  # IMPORTANT: prevent Postgres varchar(100) overflow for long paths
        blank=True,
        null=True,
    )

    url = models.URLField(blank=True)

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.file and not self.url:
            raise ValidationError("Provide either a file upload or a URL.")
