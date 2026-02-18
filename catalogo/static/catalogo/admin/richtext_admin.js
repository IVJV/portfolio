// catalogo/static/catalogo/admin/richtext_admin.js
(function () {
  "use strict";

  const PREVIEW_URL = "/_richtext/preview/";
  const DEBOUNCE_MS = 250;

  function getCookie(name) {
    // Django docs approach (cookie-based CSRF)
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  function debounce(fn, waitMs) {
    let t = null;
    return function (...args) {
      window.clearTimeout(t);
      t = window.setTimeout(() => fn.apply(this, args), waitMs);
    };
  }

  function isTextControl(el) {
    return el && (el.tagName === "TEXTAREA" || (el.tagName === "INPUT" && el.type === "text"));
  }

  async function fetchPreview(text, mode) {
    const csrftoken = getCookie("csrftoken");
    const body = new URLSearchParams({ text: text || "", mode: mode || "block" });

    const resp = await fetch(PREVIEW_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-CSRFToken": csrftoken || "",
        "X-Requested-With": "XMLHttpRequest",
      },
      body,
      credentials: "same-origin",
    });

    if (!resp.ok) {
      throw new Error(`Preview request failed (${resp.status})`);
    }

    return await resp.json();
  }

  function buildCheatSheet(mode) {
    const details = document.createElement("details");
    details.className = "rt-cheatsheet";

    const summary = document.createElement("summary");
    summary.textContent = "Markdown cheat sheet";
    details.appendChild(summary);

    const body = document.createElement("div");
    body.className = "rt-cheatsheet-body";

    // Keep it minimal and aligned with your “allowed subset”
    const items = [];

    items.push(`<div><code>**negrita**</code> → <strong>negrita</strong></div>`);
    items.push(`<div><code>*cursiva*</code> → <em>cursiva</em></div>`);
    items.push(`<div><code>[texto](https://ejemplo.com)</code> → link</div>`);

    if (mode === "block") {
      items.push(`<div style="margin-top:6px;"><code>- item</code> → lista</div>`);
      items.push(`<div><code>1. item</code> → lista numerada</div>`);
      items.push(`<div style="margin-top:6px;">Párrafos: deja una línea en blanco entre bloques.</div>`);
    } else {
      items.push(`<div style="margin-top:6px;">Inline recomendado: evita listas o saltos grandes.</div>`);
    }

    body.innerHTML = items.join("");
    details.appendChild(body);

    return details;
  }

  function attachRichTextUI(field) {
    if (!isTextControl(field)) return;

    const mode = (field.dataset.richtextMode || "block").toLowerCase() === "inline" ? "inline" : "block";

    // Container under the field
    const tools = document.createElement("div");
    tools.className = "rt-tools";

    const btnPreview = document.createElement("button");
    btnPreview.type = "button";
    btnPreview.className = "button rt-btn";
    btnPreview.textContent = "Preview";
    tools.appendChild(btnPreview);

    // Preview box
    const preview = document.createElement("div");
    preview.className = "rt-preview is-hidden";

    const title = document.createElement("div");
    title.className = "rt-preview-title";
    title.textContent = "Preview";
    preview.appendChild(title);

    const body = document.createElement("div");
    body.className = "rt-preview-body";
    body.innerHTML = "<em>Click “Preview” to render…</em>";
    preview.appendChild(body);

    // Cheat sheet
    const cheat = buildCheatSheet(mode);

    // Insert after the field
    field.insertAdjacentElement("afterend", cheat);
    field.insertAdjacentElement("afterend", preview);
    field.insertAdjacentElement("afterend", tools);

    let previewOpen = false;

    async function updatePreview() {
      try {
        const data = await fetchPreview(field.value || "", mode);

        if (!data.enabled) {
          body.innerHTML = "<em>Preview disabled (ENABLE_RICHTEXT is off).</em>";
          return;
        }

        const html = (data.html || "").trim();
        body.innerHTML = html ? html : "<em>(empty)</em>";
      } catch (err) {
        body.innerHTML = `<em>Preview error: ${String(err.message || err)}</em>`;
      }
    }

    const debouncedUpdate = debounce(() => {
      if (previewOpen) updatePreview();
    }, DEBOUNCE_MS);

    field.addEventListener("input", debouncedUpdate);

    btnPreview.addEventListener("click", async () => {
      previewOpen = !previewOpen;
      preview.classList.toggle("is-hidden", !previewOpen);

      if (previewOpen) {
        await updatePreview();
      }
    });
  }

  function init() {
    const fields = document.querySelectorAll(".js-richtext");
    fields.forEach((f) => attachRichTextUI(f));
  }

  document.addEventListener("DOMContentLoaded", init);
})();
