(function () {
  function attachTooltips() {
    // Django admin renders help text as <div class="help">...</div> (or similar).
    // We convert that help block into an (ℹ️) icon next to the label with title tooltip.
    const helpBlocks = document.querySelectorAll(".help, .helptext");

    helpBlocks.forEach((help) => {
      const text = (help.textContent || "").trim();
      if (!text) return;

      // Find the nearest field container and its label.
      const fieldRow =
        help.closest(".form-row") ||
        help.closest(".fieldBox") ||
        help.closest(".aligned") ||
        help.parentElement;

      if (!fieldRow) return;

      const label =
        fieldRow.querySelector("label") ||
        fieldRow.querySelector(".flex-container label");

      if (!label) return;

      // Avoid duplicating icons on reload.
      if (label.querySelector(".lea-help-icon")) return;

      const icon = document.createElement("span");
      icon.className = "lea-help-icon";
      icon.textContent = "ℹ️";
      icon.setAttribute("title", text);

      label.appendChild(icon);

      // Remove the original help text block so the UI stays clean.
      help.remove();
    });
  }

  document.addEventListener("DOMContentLoaded", attachTooltips);
})();
