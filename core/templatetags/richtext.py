# core/templatetags/richtext.py
from __future__ import annotations

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def _enabled() -> bool:
    return bool(getattr(settings, "ENABLE_RICHTEXT", False))


@register.filter(name="md")
def md_filter(value: str) -> str:
    """
    Block Markdown -> sanitized HTML.
    """
    if not _enabled():
        return value
    from core.utils.richtext import render_md_block  # lazy import
    return mark_safe(render_md_block(value))


@register.filter(name="md_inline")
def md_inline_filter(value: str) -> str:
    """
    Inline Markdown -> sanitized HTML.
    """
    if not _enabled():
        return value
    from core.utils.richtext import render_md_inline  # lazy import
    return mark_safe(render_md_inline(value))


@register.filter(name="md_text")
def md_text_filter(value: str) -> str:
    """
    Markdown -> plain text (safe for truncation).
    """
    if not _enabled():
        return value
    from core.utils.richtext import render_md_text  # lazy import
    return render_md_text(value)
