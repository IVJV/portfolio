// catalogo/static/catalogo/admin/richtext_admin.js
(function () {
  "use strict";

  // Must match portal/urls.py:
  // path("_richtext/preview/", richtext_preview, name="richtext_preview")
  const PREVIEW_URL = window.RICHTEXT_PREVIEW_URL || "/_richtext/preview/";

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

    const contentType = (resp.headers.get("content-type") || "").toLowerCase();
    if (contentType.includes("application/json")) {
      const data = await resp.json();
      return data.html || "";
    }
    return await resp.text();
  }

  function buildCheatSheet(mode) {
    const details = document.createElement("details");
    details.className = "rt-cheatsheet";

    const summary = document.createElement("summary");
    summary.textContent = "Markdown cheat sheet";
    details.appendChild(summary);

    const body = document.createElement("div");
    body.className = "rt-cheatsheet-body";

    // Helpers
    const line = (leftCode, rightText) => {
      const row = document.createElement("div");
      row.className = "rt-line";

      const code = document.createElement("code");
      code.textContent = leftCode;

      const sep = document.createTextNode(" \u2192 "); // →
      const label = document.createElement("span");
      label.textContent = rightText;

      row.appendChild(code);
      row.appendChild(sep);
      row.appendChild(label);
      body.appendChild(row);
    };

    line("**negrita**", "negrita");
    line("*cursiva*", "cursiva");
    line("`Se@Sp99 = 90,8%`", "fórmula / monoespaciado");
    line("[texto](https://ejemplo.com)", "link");

    if (mode === "block") {
      line("- item", "lista");
      line("1. item", "lista numerada");

      const note = document.createElement("div");
      note.className = "rt-note";
      note.textContent = "Párrafos: deja una línea en blanco entre bloques.";
      body.appendChild(note);
    } else {
      const note = document.createElement("div");
      note.className = "rt-note";
      note.textContent = "Inline recomendado: evita listas o saltos grandes.";
      body.appendChild(note);
    }

    details.appendChild(body);
    return details;
  }

  function ensureRichtextUI(fieldEl) {
    if (!fieldEl || fieldEl.dataset.rtBound === "1") return;

    const mode = (fieldEl.dataset.richtextMode || "block").toLowerCase() === "inline" ? "inline" : "block";

    fieldEl.dataset.rtBound = "1";
    fieldEl.dataset.rtMode = mode;

    // Django admin field wrapper
    const row = fieldEl.closest(".form-row") || fieldEl.closest(".fieldBox") || fieldEl.parentElement;
    if (!row) return;

    const formRow = fieldEl.closest(".form-row");
    if (formRow) formRow.classList.add("rt-row");

    // Right-side container
    const box = document.createElement("div");
    box.className = "rt-preview-box";

    // Toolbar: Preview + Cheat sheet
    const toolbar = document.createElement("div");
    toolbar.className = "rt-toolbar";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "button rt-preview-btn";
    btn.textContent = "Preview";
    btn.setAttribute("aria-expanded", "false");

    const cheat = buildCheatSheet(mode);

    toolbar.appendChild(btn);
    toolbar.appendChild(cheat);

    // Panel (hidden by default)
    const panel = document.createElement("div");
    panel.className = "rt-preview-panel";
    panel.hidden = true;

    const body = document.createElement("div");
    body.className = "rt-preview-body";
    panel.appendChild(body);

    box.appendChild(toolbar);
    box.appendChild(panel);

    // Cache last rendered content
    let lastRenderedValue = null;
    let lastRenderedMode = mode;

    async function openPanel() {
      const currentValue = fieldEl.value || "";

      if (lastRenderedValue !== currentValue || lastRenderedMode !== mode) {
        body.classList.add("rt-loading");
        body.innerHTML = "";
        try {
          const html = await fetchPreviewHTML(currentValue, mode);
          body.innerHTML = html || "";
          lastRenderedValue = currentValue;
          lastRenderedMode = mode;
        } catch (err) {
          body.innerHTML = `<div class="rt-error">Preview error: ${String(err.message || err)}</div>`;
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

    // If user edits while open, mark stale so next open refreshes
    fieldEl.addEventListener("input", () => {
      lastRenderedValue = null;
    });

    // Append to the row
    if (formRow) {
      formRow.appendChild(box);
    } else {
      row.appendChild(box);
    }
  }

  function init() {
    // Bind every richtext-enabled field (tagline/summary/description, and any future field)
    document.querySelectorAll(".js-richtext").forEach((el) => ensureRichtextUI(el));
  }

  document.addEventListener("DOMContentLoaded", init);
})();
