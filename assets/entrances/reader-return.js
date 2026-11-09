// The old Home tray used ?from=machine to return readers to a prose anchor.
// Home no longer owns essay cards, so both paths now converge on Writing.
(() => {
  if (new URLSearchParams(location.search).get('from') !== 'machine') return;
  const back = document.querySelector('a.back');
  if (!back) return;
  back.href = '/is/writing/#all';
  back.target = '_self';
  back.textContent = '← All writing';
})();
