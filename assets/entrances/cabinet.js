(() => {
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 motion.addEventListener('change',()=>{if(motion.matches)document.getAnimations().forEach(a=>a.cancel());});
 // Old shared links (/?section=building) still land on their part of the tray.
 const legacy={writing:'worlds',building:'building',running:'running'}[new URLSearchParams(location.search).get('section')];
 if(legacy&&!location.hash)addEventListener('load',()=>document.getElementById(legacy)?.scrollIntoView());
 // Persist the activated essay card in this history entry for native browser Back.
 document.querySelectorAll('[data-essay-slug]').forEach(a=>a.addEventListener('click',()=>{
  history.replaceState({...history.state,returnFocus:a.id},'',location.href);
 }));
 function restoreFocus(){
  let id=history.state?.returnFocus;
  try { id=decodeURIComponent(location.hash.slice(1))||id; } catch (_) {}
  const el=id&&document.getElementById(id);
  if(el?.matches?.('[data-essay-slug]'))requestAnimationFrame(()=>el.focus({preventScroll:true}));
 }
 addEventListener('pageshow',restoreFocus);
 restoreFocus();
})();
