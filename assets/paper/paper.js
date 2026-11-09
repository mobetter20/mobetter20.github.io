(() => {
  document.querySelectorAll('[data-today]').forEach((element) => {
    const today = new Date();
    element.dateTime = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    element.textContent = today.toLocaleDateString('en-US', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  });

  const dialog = document.querySelector('#cartoon-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const dialogState = { open: false, opener: null };

  function renderCartoonDialog() {
    if (dialogState.open && !dialog.open) dialog.showModal();
    if (!dialogState.open && dialog.open) dialog.close();
  }

  function openCartoonDialog(event) {
    // Modified clicks retain the ordinary image link.
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    dialogState.open = true;
    dialogState.opener = event.currentTarget;
    renderCartoonDialog();
  }

  function closeCartoonDialog() {
    dialogState.open = false;
    renderCartoonDialog();
    dialogState.opener?.focus({ preventScroll: true });
  }

  function initCartoonDialog() {
    document.querySelectorAll('[data-cartoon-view]').forEach((link) => {
      link.addEventListener('click', openCartoonDialog);
    });
    dialog.querySelector('[data-close-cartoon]').addEventListener('click', closeCartoonDialog);
    dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      closeCartoonDialog();
    });
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) closeCartoonDialog();
    });
  }
  initCartoonDialog();
})();
