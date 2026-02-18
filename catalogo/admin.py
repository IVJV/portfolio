# catalogo/admin.py
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Area, Trabajo, Documento, Highlight


class HighlightInline(admin.TabularInline):
    model = Highlight
    extra = 0
    fields = ("order", "label", "value")
    ordering = ("order", "id")


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    fields = ("order", "title", "doc_type", "file", "url")
    ordering = ("order", "id")


class TrabajoAdminForm(forms.ModelForm):
    MAX_TAGLINE_WORDS = 12

    class Meta:
        model = Trabajo
        fields = "__all__"
        help_texts = {
            "tagline": "Texto corto que acompaña al título en la card del área.",
            "image": "Portada del trabajo. Recomendado: PNG/JPG. Ideal: 1200×600 (o 1600×800). Se ve mejor con fondo transparente o un fondo limpio, sin bordes.",
            "thumbnail_url": "Miniatura/preview del trabajo (si no subes imagen). Recomendado: 600×300 (o 800×400). Preferible PNG con fondo transparente o imagen sin bordes.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "tagline" in self.fields:
            self.fields["tagline"].help_text = (
                "Texto corto que acompaña al título en la card del área. "
                f"Máximo recomendado: {self.MAX_TAGLINE_WORDS} palabras (para ~2 líneas). "
                "Soporta Markdown inline: *cursiva* y **negrita**."
            )

        self._enable_richtext_admin_ux()

    def _enable_richtext_admin_ux(self) -> None:
        """
        Adds CSS classes + data attributes so the admin JS can inject:
        - Preview (server-side)
        - Cheat sheet
        """
        preview_url = reverse("richtext_preview")

        # Tagline = inline markdown
        if "tagline" in self.fields:
            w = self.fields["tagline"].widget
            w.attrs["class"] = (w.attrs.get("class", "") + " js-richtext").strip()
            w.attrs["data-richtext-mode"] = "inline"
            w.attrs["data-richtext-preview-url"] = preview_url

        # Summary/Description = block markdown
        for fname in ("summary", "description"):
            if fname in self.fields:
                w = self.fields[fname].widget
                w.attrs["class"] = (w.attrs.get("class", "") + " js-richtext").strip()
                w.attrs["data-richtext-mode"] = "block"
                w.attrs["data-richtext-preview-url"] = preview_url

                base_help = (self.fields[fname].help_text or "").strip()
                extra = (
                    "Soporta Markdown: **negrita**, *cursiva*, links [texto](url), listas (- item). "
                    "Usa “Preview” para ver el resultado."
                )
                self.fields[fname].help_text = (base_help + (" " if base_help else "") + extra).strip()

    def clean_tagline(self):
        tagline = (self.cleaned_data.get("tagline") or "").strip()
        if not tagline:
            return tagline

        words = [w for w in tagline.split() if w]
        if len(words) > self.MAX_TAGLINE_WORDS:
            raise ValidationError(
                f"Tagline too long: {len(words)} words. Please use {self.MAX_TAGLINE_WORDS} words or fewer."
            )
        return tagline


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "created_at", "updated_at")
    list_editable = ("order",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    form = TrabajoAdminForm

    list_display = ("title", "area", "status", "is_featured", "order", "published_at", "created_at")
    list_editable = ("is_featured", "order")
    list_filter = ("status", "is_featured", "area")
    search_fields = ("title", "slug", "tagline", "summary")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-created_at")

    inlines = [HighlightInline, DocumentoInline]

    fieldsets = (
        ("Basic", {"fields": ("area", "title", "slug", "status", "published_at")}),
        ("Home ordering", {"fields": ("is_featured", "order")}),
        ("Content", {"fields": ("tagline", "summary", "description", "app_url")}),
        ("Images", {"fields": ("image", "image_url", "thumbnail_url")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    class Media:
        css = {
            "all": (
                "catalogo/admin/admin_tooltips.css",
                "catalogo/admin/richtext_admin.css",
            )
        }
        js = (
            "catalogo/admin/admin_tooltips.js",
            "catalogo/admin/richtext_admin.js",
        )
