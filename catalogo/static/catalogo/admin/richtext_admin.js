// catalogo/static/catalogo/admin/richtext_admin.js
(function () {
  "use strict";

  function getCsrfToken() {
    // Prefer hidden input in the form
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (input && input.value) return input.value;

    // Fallback: cookie
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  async function fetchPreviewHTML(previewUrl, text, mode) {
    const csrftoken = getCsrfToken();

    const resp = await fetch(previewUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
      body: JSON.stringify({ text: text || "", mode: mode || "block" }),
    });

    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(msg || `Preview request failed (${resp.status})`);
    }

    const data = await resp.json();
    return data.html || "";
  }

  function buildCheatSheet(mode) {
    // Inline vs block guidance
    const lines =
      mode === "inline"
        ? [
            "<code>**negrita**</code> → <strong>negrita</strong>",
            "<code>*cursiva*</code> → <em>cursiva</em>",
            "<code>[texto](https://ejemplo.com)</code> → link",
            "<div class='rt-note'>Inline recomendado: evita listas o saltos grandes.</div>",
          ]
        : [
            "<code>**negrita**</code> → <strong>negrita</strong>",
            "<code>*cursiva*</code> → <em>cursiva</em>",
            "<code>[texto](https://ejemplo.com)</code> → link",
            "<code>- item</code> → lista",
            "<code>1. item</code> → lista numerada",
            "<div class='rt-note'>Párrafos: deja una línea en blanco entre bloques.</div>",
          ];

    const details = document.createElement("details");
    details.className = "rt-cheatsheet";

    const summary = document.createElement("summary");
    summary.textContent = "Markdown cheat sheet";

    const body = document.createElement("div");
    body.className = "rt-cheatsheet-body";
    body.innerHTML = lines.map((x) => `<div class="rt-line">${x}</div>`).join("");

    details.appendChild(summary);
    details.appendChild(body);
    return details;
  }

  function ensurePreviewUI(fieldEl) {
    if (fieldEl.dataset.rtBound === "1") return;

    fieldEl.dataset.rtBound = "1";

    const mode = fieldEl.dataset.richtextMode || fieldEl.dataset.rtMode || "block";
    const previewUrl = fieldEl.dataset.richtextPreviewUrl || "/_richtext/preview/";

    const row = fieldEl.closest(".form-row") || fieldEl.parentElement;
    if (!row) return;

    row.classList.add("rt-row");

    const box = document.createElement("div");
    box.className = "rt-preview-box";

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

    const panel = document.createElement("div");
    panel.className = "rt-preview-panel";
    panel.hidden = true;

    const body = document.createElement("div");
    body.className = "rt-preview-body";

    panel.appendChild(body);

    box.appendChild(toolbar);
    box.appendChild(panel);

    // Cache + debounce
    let open = false;
    let lastValue = null;
    let timer = null;

    async function render() {
      const currentValue = fieldEl.value || "";
      if (lastValue === currentValue) return;

      body.classList.add("rt-loading");
      body.innerHTML = "";

      try {
        const html = await fetchPreviewHTML(previewUrl, currentValue, mode);
        body.innerHTML = html || "<div class='rt-muted'>(empty)</div>";
        lastValue = currentValue;
      } catch (err) {
        body.innerHTML = `<div class="rt-error">Preview error: ${String(
          err.message || err
        )}</div>`;
      } finally {
        body.classList.remove("rt-loading");
      }
    }

    function openPanel() {
      open = true;
      panel.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      void render();
    }

    function closePanel() {
      open = false;
      panel.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }

    btn.addEventListener("click", () => {
      if (!open) openPanel();
      else closePanel();
    });

    fieldEl.addEventListener("input", () => {
      lastValue = null;
      if (!open) return;

      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        void render();
      }, 250);
    });

    row.appendChild(box);
  }

  function init() {
    const fields = [
      document.getElementById("id_tagline"),
      document.getElementById("id_summary"),
      document.getElementById("id_description"),
    ].filter(Boolean);

    fields.forEach(ensurePreviewUI);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
