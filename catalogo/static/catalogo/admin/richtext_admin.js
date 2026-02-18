// catalogo/static/catalogo/admin/richtext_admin.js
(function () {
  "use strict";

  // Default preview endpoint (matches Phase 3 url)
  const PREVIEW_URL = window.RICHTEXT_PREVIEW_URL || "/admin/richtext/preview/";

  function getCookie(name) {
    const cookieValue = document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith(name + "="));
    return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : "";
  }

  async function fetchPreviewHTML(text, mode) {
    const csrftoken = getCookie("csrftoken");

    const resp = await fetch(PREVIEW_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ text: text || "", mode: mode || "block" }),
    });

    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(msg || `Preview request failed (${resp.status})`);
    }

    // Accept either JSON {html: "..."} or raw HTML response
    const contentType = (resp.headers.get("content-type") || "").toLowerCase();
    if (contentType.includes("application/json")) {
      const data = await resp.json();
      return data.html || "";
    }
    return await resp.text();
  }

  function ensurePreviewUI(fieldEl, mode) {
    // We attach UI once per field
    if (fieldEl.dataset.rtBound === "1") return;

    fieldEl.dataset.rtBound = "1";
    fieldEl.dataset.rtMode = mode;

    // Where to append: in Django admin, each field is inside .form-row
    const row = fieldEl.closest(".form-row") || fieldEl.parentElement;
    if (!row) return;

    row.classList.add("rt-row");

    // Create container on the right side (same row)
    const box = document.createElement("div");
    box.className = "rt-preview-box";

    // Button
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "button rt-preview-btn";
    btn.textContent = "Preview";

    // Panel (hidden by default)
    const panel = document.createElement("div");
    panel.className = "rt-preview-panel";
    panel.hidden = true;

    // Body (render target)
    const body = document.createElement("div");
    body.className = "rt-preview-body";

    panel.appendChild(body);

    // Put into DOM
    box.appendChild(btn);
    box.appendChild(panel);

    // IMPORTANT: avoid showing any “help text” — we intentionally do NOT add it.

    // Cache last rendered content to avoid needless requests
    let lastRenderedValue = null;
    let lastRenderedMode = mode;

    async function openPanel() {
      const currentValue = fieldEl.value || "";

      // Only render if needed
      if (lastRenderedValue !== currentValue || lastRenderedMode !== mode) {
        body.classList.add("rt-loading");
        body.innerHTML = "";
        try {
          const html = await fetchPreviewHTML(currentValue, mode);
          body.innerHTML = html || "";
          lastRenderedValue = currentValue;
          lastRenderedMode = mode;
        } catch (err) {
          body.innerHTML =
            `<div class="rt-error">Preview error: ${String(err.message || err)}</div>`;
        } finally {
          body.classList.remove("rt-loading");
        }
      }

      panel.hidden = false;
      box.classList.add("is-open");
      btn.setAttribute("aria-expanded", "true");
    }

    function closePanel() {
      panel.hidden = true;
      box.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    }

    function togglePanel() {
      if (panel.hidden) {
        void openPanel();
      } else {
        closePanel();
      }
    }

    btn.addEventListener("click", togglePanel);

    // Optional: if user types while preview is open, mark it stale (re-render on next open)
    fieldEl.addEventListener("input", () => {
      if (!panel.hidden) {
        // keep open but re-render quickly after pause? -> no (simpler)
        // just mark stale and show subtle hint
        lastRenderedValue = null;
      }
    });

    // Insert box at the end of the row (right side)
    row.appendChild(box);
  }

  function init() {
    // Tagline is short: inline markdown preview
    const tagline = document.getElementById("id_tagline");
    if (tagline) ensurePreviewUI(tagline, "inline");

    // Summary/Description: block markdown preview
    const summary = document.getElementById("id_summary");
    if (summary) ensurePreviewUI(summary, "block");

    const description = document.getElementById("id_description");
    if (description) ensurePreviewUI(description, "block");

    // If you later add more rich fields, you can bind them here.
  }

  document.addEventListener("DOMContentLoaded", init);
})();
