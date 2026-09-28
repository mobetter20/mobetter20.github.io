// Keep ordinary essay arrivals in the writing archive. Machine arrivals return to their key.
(() => {
  if (new URLSearchParams(location.search).get('from') !== 'machine') return;
  const slug = location.pathname.split('/').filter(Boolean).pop();
  const back = document.querySelector('a.back');
  if (!back || !slug) return;
  back.href = '/?section=writing#' + encodeURIComponent(slug);
  back.target = '_self';
  back.textContent = '← ajin.im / writing';
})();
