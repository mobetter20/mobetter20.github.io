/* One image per page load. The server-rendered Austen piece is the no-JS fallback. */
(() => {
  let state;
  let lead;
  let picture;
  let link;
  let caption;

  function renderHomeLead(piece) {
    lead.dataset.piece = piece.slug;
    link.href = piece.href;
    link.setAttribute('aria-label', `Read ${piece.title}`);
    picture.width = piece.width;
    picture.height = piece.height;
    picture.alt = piece.alt;
    caption.textContent = piece.caption;
    caption.hidden = !piece.caption;
    picture.src = piece.image;
  }

  function selectHomeLead(items, randomValue) {
    const index = Math.min(items.length - 1, Math.floor(randomValue * items.length));
    state.selectedSlug = items[index].slug;
    renderHomeLead(items[index]);
  }

  function handleHomeLeadError() {
    if (state.selectedSlug === state.fallback.slug || state.failed) return;
    state.failed = true;
    // Hold the occupied space if a failed request resolves after first paint.
    const occupied = lead.getBoundingClientRect().height;
    const oldImageHeight = picture.getBoundingClientRect().height;
    const oldCaptionHeight = caption.hidden ? 0 : caption.getBoundingClientRect().height;
    state.selectedSlug = state.fallback.slug;
    renderHomeLead(state.fallback);
    const newCaptionHeight = caption.hidden ? 0 : caption.getBoundingClientRect().height;
    const imageHeight = Math.max(1, oldImageHeight + oldCaptionHeight - newCaptionHeight);
    picture.style.aspectRatio = `${picture.getBoundingClientRect().width} / ${imageHeight}`;
    picture.style.objectFit = 'contain';
    lead.style.minHeight = `${occupied}px`;
  }

  function initHomeLead() {
    if (state) return;
    lead = document.querySelector('#home-image-lead');
    if (!lead) return;
    picture = lead.querySelector('[data-piece-image]');
    link = lead.querySelector('[data-piece-link]');
    caption = lead.querySelector('[data-piece-caption]');
    try {
      const catalog = JSON.parse(document.querySelector('#home-image-catalog').textContent);
      if (!catalog.pieces.length || !catalog.fallback) return;
      state = { fallback: catalog.fallback, selectedSlug: null, failed: false };
      picture.addEventListener('error', handleHomeLeadError);
      selectHomeLead(catalog.pieces, Math.random());
    } catch (_) {
      // Retain the fully functional native link and illustration if enhancement fails.
    }
  }

  window.paperHomeLead = Object.freeze({ init: initHomeLead });
})();
