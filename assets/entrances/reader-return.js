// Keep ordinary essay arrivals in the writing archive. Machine arrivals return to their card on the home tray.
(() => {
  if (new URLSearchParams(location.search).get('from') !== 'machine') return;
  const slug = location.pathname.split('/').filter(Boolean).pop();
  const back = document.querySelector('a.back');
  if (!back || !slug) return;
  back.href = '/#' + encodeURIComponent(slug);
  back.target = '_self';
  back.textContent = '← ajin.im';
})();
