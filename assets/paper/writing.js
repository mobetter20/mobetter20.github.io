(() => {
  const root = document.querySelector('.unified-writing');
  if (!root) return;
  const selection = document.querySelector('#selection');
  const archive = document.querySelector('#all');
  const state = { view: 'selection' };

  function renderView() {
    selection.hidden = state.view !== 'selection';
    archive.hidden = state.view !== 'all';
    document.title = `ajin.im · Writing${state.view === 'all' ? ' · Archive' : ''}`;
  }

  function positionView() {
    const target = location.hash === '#cartoons' ? document.querySelector('#cartoons') : (state.view === 'all' ? archive : selection);
    target.focus({ preventScroll: true });
    if (location.hash === '#cartoons') target.scrollIntoView({ behavior: 'instant', block: 'start' });
    else window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function handleHashChange() {
    if (!['', '#all', '#selection', '#cartoons'].includes(location.hash)) return;
    state.view = location.hash === '#all' ? 'all' : 'selection';
    renderView();
    positionView();
  }

  root.classList.add('is-enhanced');
  window.addEventListener('hashchange', handleHashChange);
  state.view = location.hash === '#all' ? 'all' : 'selection';
  renderView();
  if (['#all', '#selection', '#cartoons'].includes(location.hash)) window.addEventListener('load', positionView, { once: true });
})();
