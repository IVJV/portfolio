# core/richtext_views.py
from __future__ import annotations

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.utils.richtext import render_md_block, render_md_inline


@staff_member_required
@csrf_protect
@require_POST
def richtext_preview(request):
    """
    Admin-only helper endpoint:
    - Receives markdown text and returns sanitized HTML.
    - Accepts:
        POST JSON: { "text": "...", "mode": "inline"|"block" }
        POST form: text=...&mode=...
    - Returns JSON: { "html": "<p>...</p>" }
    """
    ct = (request.headers.get("content-type") or "").lower()
    text = ""
    mode = "block"

    if "application/json" in ct:
        try:
            payload = json.loads((request.body or b"{}").decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")
        text = (payload.get("text") or "").strip()
        mode = (payload.get("mode") or "block").strip().lower()
    else:
        text = (request.POST.get("text") or "").strip()
        mode = (request.POST.get("mode") or "block").strip().lower()

    if mode not in {"inline", "block"}:
        mode = "block"

    html = render_md_inline(text) if mode == "inline" else render_md_block(text)
    return JsonResponse({"html": html})
