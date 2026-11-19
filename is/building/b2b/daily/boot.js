// Keep the initial page usable when a module or core data request fails.
const game=document.querySelector('#game');
try{
  await import('./app.js?v=daily-5');
  document.querySelector('#loading-screen').hidden=true;
  for(const id of ['help-button','menu-button','archive-button'])document.getElementById(id).disabled=false;
}catch(error){
  document.querySelector('#loading-screen').hidden=true;
  document.querySelector('#puzzle-screen').hidden=true;
  document.querySelector('#empty-screen').hidden=false;
  document.querySelector('#empty-heading').textContent='The puzzle couldn’t load.';
  document.querySelector('#empty-copy').textContent='Reload the page to try again.';
  const reload=document.querySelector('#empty-screen button');
  reload.textContent='Reload';reload.disabled=false;
  reload.addEventListener('click',()=>location.reload());
  document.querySelector('#empty-copy').setAttribute('role','alert');
  console.error('Bird to Bird could not load:',error);
}finally{
  game.setAttribute('aria-busy','false');
}
