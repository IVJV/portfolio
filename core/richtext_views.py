# core/richtext_views.py
from __future__ import annotations

from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from core.utils.richtext import render_md_block, render_md_inline


@staff_member_required
@require_POST
@csrf_protect
def richtext_preview(request):
    """
    Admin-only Markdown preview endpoint.
    Uses the SAME server-side renderer + sanitizer as the public site
    (so preview matches production behavior).
    """
    if not getattr(settings, "ENABLE_RICHTEXT", False):
        return JsonResponse({"enabled": False, "html": ""})

    text = request.POST.get("text", "") or ""
    mode = (request.POST.get("mode", "block") or "block").strip().lower()

    if mode not in {"block", "inline"}:
        return HttpResponseBadRequest("Invalid mode")

    html = render_md_inline(text) if mode == "inline" else render_md_block(text)
    return JsonResponse({"enabled": True, "html": html})
