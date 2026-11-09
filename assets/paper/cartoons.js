/* Optional touch gesture over the art. Native links remain the navigation source. */
(() => {
  const stage = document.querySelector('.slide-stage');
  if (!stage) return;
  let swipeState = null;
  function down(event) {
    if (event.pointerType !== 'touch') return;
    if (event.isPrimary && swipeState?.finished) swipeState = null;
    if (swipeState && event.pointerId !== swipeState.pointerId) { swipeState.cancelled = true; return; }
    if (!event.isPrimary || !stage.contains(event.target) || event.target.closest('.slide-arrow')) return;
    swipeState = {pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,cancelled:false,navigated:false,finished:false,suppressClick:false};
  }
  function move(event) { if (swipeState && event.pointerId === swipeState.pointerId) { /* browser owns scroll and zoom */ } }
  function up(event) {
    const gesture = swipeState;
    if (!gesture || event.pointerId !== gesture.pointerId || gesture.navigated) return;
    if (gesture.cancelled) { swipeState = null; return; }
    const dx = event.clientX - gesture.startX, dy = event.clientY - gesture.startY;
    if (Math.abs(dx) < 60 || Math.abs(dx) <= 1.5 * Math.abs(dy)) { swipeState = null; return; }
    gesture.finished = true; gesture.suppressClick = true; event.preventDefault();
    const anchor = stage.querySelector(`[data-slide-${dx < 0 ? 'next' : 'previous'}]`);
    if (anchor) { gesture.navigated = true; location.assign(anchor.href); }
    setTimeout(() => { if (swipeState === gesture) swipeState = null; }, 500);
  }
  function cancel(event) { if (swipeState && event.pointerId === swipeState.pointerId) swipeState = null; }
  function click(event) { if (swipeState?.suppressClick) { event.preventDefault(); event.stopImmediatePropagation(); swipeState.suppressClick = false; } }
  document.addEventListener('pointerdown', down); document.addEventListener('pointermove', move, {passive:true}); document.addEventListener('pointerup', up); document.addEventListener('pointercancel', cancel); stage.addEventListener('click', click, true);
})();
