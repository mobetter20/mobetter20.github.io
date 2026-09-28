(() => {
 const title=document.getElementById('rack-selection');
 const purpose=document.getElementById('rack-purpose');
 const modules=[...document.querySelectorAll('.module')];
 let hovered=null;
 let lastInput="focus";
 function paint(){
  const focused=document.activeElement.closest?.('.module');
  const current=lastInput==="pointer"?(hovered||focused):(focused||hovered);
  title.textContent=current?.dataset.name||'Choose an instrument.';
  purpose.textContent=current?.dataset.purpose||'Open a tool below to begin.';
  modules.forEach(el=>el.classList.toggle('indicated',el===current));
 }
 modules.forEach(el=>{el.addEventListener('pointerenter',()=>{hovered=el;lastInput="pointer";paint();});el.addEventListener('pointerleave',()=>{hovered=null;paint();});});
 document.addEventListener('focusin',()=>{lastInput="focus";paint();});
 document.addEventListener('focusout',()=>requestAnimationFrame(paint));
})();
