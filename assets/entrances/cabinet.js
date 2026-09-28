(() => {
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 motion.addEventListener('change',()=>{if(motion.matches)document.getAnimations().forEach(a=>a.cancel());});
 const keys=[...document.querySelectorAll('[data-section]')];
 const inventories=[...document.querySelectorAll('.inventory')];
 const counts=Object.fromEntries(inventories.map(p=>[p.id,p.dataset.count]));
 function show(name,animate=false){
  if(!Object.hasOwn(counts,name))name='writing';
  keys.forEach(k=>k.setAttribute('aria-pressed',String(k.dataset.section===name)));
  inventories.forEach(p=>p.hidden=p.id!==name);
  document.getElementById('section-name').textContent=name;
  document.getElementById('section-count').textContent=counts[name];
  document.getElementById('bay-name').textContent=name.toUpperCase();
  if(animate&&!motion.matches){
   document.querySelector('.readout').animate([{opacity:.55},{opacity:1}],{duration:180});
   document.getElementById(name).animate([{opacity:.65},{opacity:1}],{duration:160});
  }
 }
 function fitCabinet(){
  const focused=document.activeElement;
  inventories.forEach(p=>p.style.minHeight='');
  if(innerWidth<=650)return;
  const selected=keys.find(k=>k.getAttribute('aria-pressed')==='true')?.dataset.section||'writing';
  let tallest=0;
  inventories.forEach(p=>{p.hidden=false;tallest=Math.max(tallest,p.getBoundingClientRect().height);p.hidden=true;});
  inventories.forEach(p=>p.style.minHeight=Math.ceil(tallest)+'px');
  show(selected);
  if(focused?.closest?.(".inventory")&&!focused.closest("[hidden]"))focused.focus({preventScroll:true});
 }
 show(new URLSearchParams(location.search).get('section'));
 let lastWidth=0;
 new ResizeObserver(entries=>{const width=entries[0].contentRect.width;if(width!==lastWidth){lastWidth=width;fitCabinet();}}).observe(document.querySelector('.selection-bay'));
 document.fonts.ready.then(fitCabinet);
 keys.forEach(k=>k.addEventListener('click',()=>{
  if(k.getAttribute('aria-pressed')==='true')return;
  const u=new URL(location.href);u.searchParams.set('section',k.dataset.section);u.hash='';
  history.pushState({},'',u);show(k.dataset.section,true);
 }));
 addEventListener('popstate',()=>show(new URLSearchParams(location.search).get('section')));
 // Persist the activated key in this history entry for native browser Back.
 document.querySelectorAll('[data-essay-slug]').forEach(a=>a.addEventListener('click',()=>{
  history.replaceState({...history.state,returnFocus:a.id},'',location.href);
 }));
 function restoreFocus(){
  let id=history.state?.returnFocus;
  try { id=decodeURIComponent(location.hash.slice(1))||id; } catch (_) {}
  const el=id&&document.getElementById(id);
  if(el&&!el.closest('[hidden]'))requestAnimationFrame(()=>el.focus({preventScroll:true}));
 }
 addEventListener('pageshow',restoreFocus);
 restoreFocus();
})();
