# core/utils/richtext.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import markdown
import nh3


# -----------------------------
# Sanitization policy (allowlist)
# -----------------------------
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}

ALLOWED_TAGS_BLOCK = {
    # structure
    "p", "br",
    "ul", "ol", "li",
    "blockquote",
    "pre", "code",
    # inline emphasis
    "strong", "em",
    # links
    "a",
}

ALLOWED_TAGS_INLINE = {
    "br",
    "strong", "em",
    "code",
    "a",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "*": set(),
}

# Force safe link behavior
SET_TAG_ATTRIBUTE_VALUES = {
    "a": {"target": "_blank"},
}

# Optional: remove a single outer <p> wrapper (common for single-line Markdown)
_P_WRAPPER_RE = re.compile(r"^\s*<p>(.*)</p>\s*$", re.DOTALL)


@dataclass(frozen=True)
class RichTextOptions:
    tags: set[str]
    attributes: dict[str, set[str]]


def _markdown_to_html(text: str) -> str:
    """
    Converts Markdown -> HTML.
    Raw HTML may be present in Markdown input, but will be removed by sanitization.
    """
    return markdown.markdown(
        text or "",
        extensions=[
            "sane_lists",   # consistent list behavior
            "nl2br",        # newlines -> <br>
            "fenced_code",  # ```code``` blocks
        ],
        output_format="html",
    )


def _sanitize(html: str, *, opts: RichTextOptions) -> str:
    """
    Sanitizes HTML with a strict allowlist.
    """
    return nh3.clean(
        html or "",
        tags=opts.tags,
        attributes=opts.attributes,
        url_schemes=ALLOWED_URL_SCHEMES,
        strip_comments=True,
        link_rel="noopener noreferrer",
        set_tag_attribute_values=SET_TAG_ATTRIBUTE_VALUES,
    )


def render_md_block(text: Optional[str]) -> str:
    """
    Markdown -> sanitized HTML (block-friendly).
    Intended for: summary, description, area.description (if you enable it).
    """
    html = _markdown_to_html(text or "")
    return _sanitize(html, opts=RichTextOptions(ALLOWED_TAGS_BLOCK, ALLOWED_ATTRIBUTES)).strip()


def render_md_inline(text: Optional[str]) -> str:
    """
    Markdown -> sanitized HTML (inline-only).
    Intended for: tagline (cards, carousel, headers).
    """
    raw_html = _markdown_to_html(text or "")

    # Strip single outer <p> wrapper before sanitizing (keeps output truly inline)
    m = _P_WRAPPER_RE.match(raw_html)
    if m:
        raw_html = m.group(1)

    clean = _sanitize(raw_html, opts=RichTextOptions(ALLOWED_TAGS_INLINE, ALLOWED_ATTRIBUTES))
    return clean.strip()


def render_md_text(text: Optional[str]) -> str:
    """
    Markdown -> plain text (safe for truncation).
    Use this when you want to do truncatechars without breaking HTML.
    """
    html = _markdown_to_html(text or "")
    # Remove all tags; keep only text content (escaped).
    return nh3.clean(
        html,
        tags=set(),
        attributes={},
        url_schemes=ALLOWED_URL_SCHEMES,
        strip_comments=True,
    ).strip()
