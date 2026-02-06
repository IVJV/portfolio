/* core/static/core/js/base.js */

/**
 * Home carousel: update "Área" pill from active slide
 * Safe-guarded: does nothing if carousel/pill is not present.
 */
(function () {
  function initAreaPill() {
    const carouselEl = document.getElementById("latestCarousel");
    const pillEl = document.getElementById("leaAreaPill");
    if (!carouselEl || !pillEl) return;

    function setPillFromActive() {
      const active = carouselEl.querySelector(".carousel-item.active");
      const area = active?.getAttribute("data-area") || "";
      pillEl.textContent = area ? `Área: ${area}` : "";
    }

    setPillFromActive();
    carouselEl.addEventListener("slid.bs.carousel", setPillFromActive);
  }

  // Ensure DOM is ready (works even if script is moved/loaded differently)
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAreaPill);
  } else {
    initAreaPill();
  }
})();
