/* Share the piece's canonical URL. No image payloads or tracking parameters. */
(() => {
  const initialized = new WeakSet();
  const states = new WeakMap();

  function shareData(button) {
    try {
      const title = button.getAttribute('data-share-title');
      const url = new URL(button.getAttribute('data-share-url'));
      if (!title?.trim() || url.origin !== 'https://ajin.im' || url.username || url.password) return null;
      return { title, url: url.href };
    } catch (_) { return null; }
  }

  function canShare(data) {
    try {
      return typeof navigator.share === 'function' &&
        (typeof navigator.canShare !== 'function' || navigator.canShare(data));
    } catch (_) { return false; }
  }

  function clearFeedback(group, state) {
    clearTimeout(state.timer);
    state.status.textContent = '';
    group.querySelector('.share-url')?.remove();
  }

  function initShareControls(root) {
    const groups = root.matches?.('.piece-share') ? [root] : [];
    groups.push(...(root.querySelectorAll?.('.piece-share') || []));
    for (const group of groups) {
      if (initialized.has(group)) continue;
      const button = group.querySelector('.share-button');
      const status = group.querySelector('.share-status');
      if (!button || !status) continue;
      initialized.add(group);
      const state = { status, busy: false, operation: 0, timer: null };
      states.set(button, state);
      // A slide restored from a cloned template must not inherit a pending action.
      clearFeedback(group, state);
      button.removeAttribute('aria-busy');
      const data = shareData(button);
      button.disabled = !data;
      button.hidden = !data;
      group.hidden = !data;
      if (data) button.textContent = canShare(data) ? 'Share' : 'Copy link';
    }
  }

  function manualCopy(group, state, url) {
    const field = document.createElement('input');
    field.className = 'share-url';
    field.type = 'text';
    field.readOnly = true;
    field.value = url;
    field.setAttribute('aria-label', 'Link to this piece');
    group.append(field);
    state.status.textContent = 'Copy this link:';
    field.focus();
    field.select();
  }

  async function onShareClick(event) {
    if (event.defaultPrevented) return;
    const button = event.target.closest?.('.share-button');
    const group = button?.closest('.piece-share');
    const state = button && states.get(button);
    if (!group || !state || state.busy || button.disabled || !button.isConnected) return;
    // Capture both values once; a later slide or URL change cannot alter this action.
    const data = shareData(button);
    if (!data) return;
    event.preventDefault();
    clearFeedback(group, state);
    const operation = ++state.operation;
    const current = () => operation === state.operation && group.isConnected && button.isConnected && group.contains(button);
    state.busy = true;
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    try {
      if (canShare(data)) {
        try {
          await navigator.share(data);
          return; // Resolving the share sheet does not prove that anything was sent.
        } catch (error) {
          if (error?.name === 'AbortError') return;
        }
      }
      if (!current()) return;
      try {
        if (typeof navigator.clipboard?.writeText !== 'function') throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(data.url);
        if (!current()) return;
        state.status.textContent = 'Copied';
        state.timer = setTimeout(() => { if (current()) state.status.textContent = ''; }, 2000);
      } catch (_) {
        if (current()) manualCopy(group, state, data.url);
      }
    } finally {
      if (current()) {
        state.busy = false;
        button.disabled = false;
        button.removeAttribute('aria-busy');
      }
    }
  }

  function onShareMutations(records) {
    for (const record of records) for (const node of record.addedNodes) {
      if (node.nodeType !== 1) continue;
      initShareControls(node);
      const group = node.closest?.('.piece-share');
      if (group) initShareControls(group);
    }
  }

  initShareControls(document);
  document.addEventListener('click', onShareClick);
  new MutationObserver(onShareMutations).observe(document.body, { childList: true, subtree: true });
})();
