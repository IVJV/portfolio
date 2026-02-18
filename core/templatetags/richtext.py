# core/templatetags/richtext.py
from __future__ import annotations

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from core.utils.richtext import render_md_block, render_md_inline, render_md_text

register = template.Library()


@register.filter(name="md")
def md_filter(value: str) -> str:
    """
    Block Markdown -> sanitized HTML.
    """
    if not getattr(settings, "ENABLE_RICHTEXT", False):
        return value
    return mark_safe(render_md_block(value))


@register.filter(name="md_inline")
def md_inline_filter(value: str) -> str:
    """
    Inline Markdown -> sanitized HTML.
    """
    if not getattr(settings, "ENABLE_RICHTEXT", False):
        return value
    return mark_safe(render_md_inline(value))


@register.filter(name="md_text")
def md_text_filter(value: str) -> str:
    """
    Markdown -> plain text (safe for truncation).
    """
    if not getattr(settings, "ENABLE_RICHTEXT", False):
        return value
    return render_md_text(value)
