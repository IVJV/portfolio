# core/richtext_views.py
from __future__ import annotations

import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from core.utils.richtext import render_md_block, render_md_inline


@require_http_methods(["POST", "GET"])
def richtext_preview(request):
    """
    Admin-only helper endpoint:
    - Receives markdown text and returns sanitized HTML.
    - Accepts:
        POST JSON: { "text": "...", "mode": "inline"|"block" }
        GET params: ?text=...&mode=...
    - Returns JSON: { "html": "<p>...</p>" }
    """
    # You can allow preview even if ENABLE_RICHTEXT is off; it's just a preview.
    _ = getattr(settings, "ENABLE_RICHTEXT", False)

    text = ""
    mode = "block"

    if request.method == "POST":
      ct = (request.headers.get("content-type") or "").lower()
      if "application/json" in ct:
          try:
              payload = json.loads(request.body.decode("utf-8") or "{}")
          except Exception:
              return HttpResponseBadRequest("Invalid JSON")
          text = (payload.get("text") or payload.get("value") or "").strip()
          mode = (payload.get("mode") or "block").strip().lower()
      else:
          text = (request.POST.get("text") or request.POST.get("value") or "").strip()
          mode = (request.POST.get("mode") or "block").strip().lower()
    else:
      text = (request.GET.get("text") or request.GET.get("value") or "").strip()
      mode = (request.GET.get("mode") or "block").strip().lower()

    if mode not in {"inline", "block"}:
        mode = "block"

    html = render_md_inline(text) if mode == "inline" else render_md_block(text)
    return JsonResponse({"html": html})
