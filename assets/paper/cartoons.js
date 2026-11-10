/* Enhance the generated slide pages; their links remain the no-JS/error fallback. */
(() => {
  let stage = document.querySelector('.slide-stage');
  if (!stage) return;
  let visit = href => location.assign(href);
  let shell = document.querySelector('main.slide-shell');

  if (shell && typeof fetch === 'function' && typeof AbortController === 'function') {
    const cache = new Map();
    const firstSlide = shell.getAttribute('data-first-slide');
    const firstPath = firstSlide ? new URL(firstSlide, location.href).pathname : null;
    const metadata = 'link[rel="canonical"],meta[property^="og:"],meta[name^="twitter:"],meta[name="description"]';
    const status = document.createElement('p');
    status.className = 'visually-hidden';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-atomic', 'true');
    shell.after(status);
    let navigation = 0;
    let pending = false;
    let active = true;

    function slideURL(href) {
      const url = new URL(href, location.href);
      return url.origin === location.origin && url.pathname.startsWith('/is/writing/cartoons/slides/') ? url : null;
    }
    function key(url) {
      const pathname = firstPath && url.pathname === '/is/writing/cartoons/slides/' ? firstPath : url.pathname;
      return url.origin + pathname + url.search;
    }
    function capture(doc) {
      const main = doc.querySelector('main.slide-shell');
      if (!main?.querySelector('.slide-image') || !main.querySelector('#slide-title')) throw new Error('Invalid slide');
      return { main: main.cloneNode(true), title: doc.title,
        head: Array.from(doc.head.querySelectorAll(metadata), node => node.cloneNode(true)), images: [] };
    }
    function decodeImage(src, entry) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        entry.images.push(img); // Retain the decoded image while this slide is cached.
        function abort() { img.removeAttribute('src'); reject(new Error('Image load cancelled')); }
        if (entry.controller.signal.aborted) return abort();
        entry.controller.signal.addEventListener('abort', abort, { once: true });
        img.decoding = 'async';
        img.src = src;
        img.decode().then(resolve, reject).finally(() => entry.controller.signal.removeEventListener('abort', abort));
      });
    }
    function loadSlide(url, initial) {
      const id = key(url);
      if (cache.has(id)) return cache.get(id).ready;
      const entry = { controller: new AbortController(), images: [], loaded: false };
      cache.set(id, entry);
      const timeout = setTimeout(() => entry.controller.abort(), 8000);
      entry.ready = (async () => {
        let data = initial;
        if (!data) {
          const response = await fetch(id, { signal: entry.controller.signal, credentials: 'same-origin' });
          if (!response.ok || key(new URL(response.url)) !== id) throw new Error('Slide unavailable');
          data = capture(new DOMParser().parseFromString(await response.text(), 'text/html'));
        }
        const sources = new Set(Array.from(data.main.querySelectorAll('img'), img => new URL(img.getAttribute('src'), url).href));
        await Promise.all(Array.from(sources, src => decodeImage(src, entry)));
        data.images = entry.images;
        entry.loaded = true;
        return data;
      })().catch(error => {
        entry.controller.abort();
        if (cache.get(id) === entry) cache.delete(id);
        throw error;
      }).finally(() => clearTimeout(timeout));
      return entry.ready;
    }
    function discard(id, entry) {
      cache.delete(id);
      if (!entry.loaded) entry.controller.abort();
    }
    function warmNeighbours() {
      if (pending || !active || document.readyState !== 'complete') return;
      const neighbours = Array.from(shell.querySelectorAll('[data-slide-next],[data-slide-previous]'), a => slideURL(a.href)).filter(Boolean);
      const keep = new Set([key(new URL(location.href)), ...neighbours.map(key)]);
      for (const [id, entry] of cache) if (!keep.has(id)) discard(id, entry);
      const connection = navigator.connection;
      if (connection?.saveData || /^(slow-)?2g$/.test(connection?.effectiveType || '')) return;
      for (const url of neighbours) loadSlide(url).catch(() => {}); // Speculation never navigates or executes scripts.
    }
    function focusAfterChange(selector) {
      if (!selector) return;
      const arrow = shell.querySelector(selector);
      if (arrow?.matches('.slide-arrow') && arrow.getClientRects().length) arrow.focus({ preventScroll: true });
      else {
        const title = shell.querySelector('#slide-title');
        title.tabIndex = -1;
        title.focus({ preventScroll: true });
      }
    }
    visit = async (href, { mode = 'push', focus = null } = {}) => {
      const url = slideURL(href);
      if (!url) return location.assign(href);
      const turn = ++navigation;
      pending = true;
      shell.setAttribute('aria-busy', 'true');
      // Cancel speculative work that would compete with this requested image.
      for (const [id, entry] of cache) {
        if (!entry.loaded && id !== key(url) && id !== key(new URL(location.href))) discard(id, entry);
      }
      try {
        const data = await loadSlide(url);
        if (turn !== navigation) return;
        const next = data.main.cloneNode(true);
        shell.replaceWith(next);
        shell = next;
        stage = shell.querySelector('.slide-stage');
        document.title = data.title;
        document.head.querySelectorAll(metadata).forEach(node => node.remove());
        data.head.forEach(node => document.head.append(node.cloneNode(true)));
        // Update the title before history: the existing GA4 history measurement owns page views.
        if (mode === 'push') history.pushState(null, '', url.href);
        focusAfterChange(focus);
        shell.scrollIntoView({ behavior: 'instant', block: 'start' });
        status.textContent = `${shell.querySelector('#slide-title').textContent}. ${shell.querySelector('.slide-position').getAttribute('aria-label')}.`;
        pending = false;
        warmNeighbours();
      } catch (_) {
        if (turn !== navigation) return;
        pending = false;
        shell.removeAttribute('aria-busy');
        if (mode === 'pop') location.replace(url.href);
        else location.assign(url.href);
      }
    };
    document.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const anchor = event.target.closest('[data-slide-next],[data-slide-previous]');
      if (!anchor || !shell.contains(anchor) || anchor.target !== '_self' || anchor.hasAttribute('download') || !slideURL(anchor.href)) return;
      event.preventDefault();
      const direction = anchor.hasAttribute('data-slide-next') ? 'next' : 'previous';
      const area = anchor.closest('.slide-pagination') ? '.slide-pagination' : '.slide-stage';
      visit(anchor.href, { focus: `${area} [data-slide-${direction}]` });
    });
    window.addEventListener('popstate', () => visit(location.href, { mode: 'pop', focus: '#slide-title' }));
    window.addEventListener('pagehide', () => {
      navigation++;
      pending = false;
      active = false;
      shell.removeAttribute('aria-busy');
      for (const [id, entry] of cache) if (!entry.loaded) discard(id, entry);
    });
    window.addEventListener('pageshow', event => { if (event.persisted) { active = true; warmNeighbours(); } });
    // Wait for the page as well as its artwork, so speculation cannot delay the initial load event.
    loadSlide(new URL(location.href), capture(document)).catch(() => {}).finally(() => {
      if (document.readyState === 'complete') warmNeighbours();
      else window.addEventListener('load', warmNeighbours, { once: true });
    });
  }

  let swipeState = null;
  function down(event) {
    if (event.pointerType !== 'touch') return;
    if (event.isPrimary && swipeState?.finished) swipeState = null;
    if (swipeState && event.pointerId !== swipeState.pointerId) { swipeState.cancelled = true; return; }
    if (!event.isPrimary || !stage.contains(event.target) || event.target.closest('.slide-arrow')) return;
    swipeState = {pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,stage,cancelled:false,navigated:false,finished:false,suppressClick:false};
  }
  function move(event) { if (swipeState && event.pointerId === swipeState.pointerId) { /* browser owns scroll and zoom */ } }
  function up(event) {
    const gesture = swipeState;
    if (!gesture || event.pointerId !== gesture.pointerId || gesture.navigated) return;
    if (gesture.cancelled || gesture.stage !== stage) { swipeState = null; return; }
    const dx = event.clientX - gesture.startX, dy = event.clientY - gesture.startY;
    if (Math.abs(dx) < 60 || Math.abs(dx) <= 1.5 * Math.abs(dy)) { swipeState = null; return; }
    gesture.finished = true; gesture.suppressClick = true; event.preventDefault();
    const anchor = gesture.stage.querySelector(`[data-slide-${dx < 0 ? 'next' : 'previous'}]`);
    if (anchor) { gesture.navigated = true; visit(anchor.href); }
    setTimeout(() => { if (swipeState === gesture) swipeState = null; }, 500);
  }
  function cancel(event) { if (swipeState && event.pointerId === swipeState.pointerId) swipeState = null; }
  function click(event) { if (swipeState?.suppressClick && (stage.contains(event.target) || swipeState.stage.contains(event.target))) { event.preventDefault(); event.stopImmediatePropagation(); swipeState.suppressClick = false; } }
  document.addEventListener('pointerdown', down); document.addEventListener('pointermove', move, {passive:true}); document.addEventListener('pointerup', up); document.addEventListener('pointercancel', cancel); document.addEventListener('click', click, true);
})();
