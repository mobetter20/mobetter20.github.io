import {createDailySession,nextMidnightDelay} from './state.js?v=daily-4';
import {SOURCE,LEXICON} from '../route/world-lexicon.js';

async function loadData(){
    return await Promise.all(['content.json','notes.json','media.json'].map(async file=>{
      const response=await fetch(new URL(`${file}?v=daily-4`,import.meta.url));
      if(!response.ok)throw new Error(`Could not load ${file}`);
      const value=await response.json();
      if(!value||typeof value!=='object'||Array.isArray(value))throw new Error(`Invalid ${file}`);
      return value;
    }));
}
const [content,NAME_NOTES,NAME_NOTE_IMAGES]=await loadData();
const root=document.querySelector('#game');
const modes=new URLSearchParams(location.search).getAll('mode');
const isPlaytest=modes.length===1&&modes[0]==='playtest';
const session=createDailySession({schedule:content.schedule,rounds:content.rounds,lexicon:LEXICON,sourceVersion:content.sourceVersion,mode:isPlaytest?'playtest':'daily'});
const calendar=[...content.schedule].sort((a,b)=>a.date.localeCompare(b.date));
const engine=session.engine;
const ui={screen:'puzzle',helpOpen:false,solutionShown:false,note:null,rolloverNotice:false};
const els=Object.fromEntries([...root.querySelectorAll('[id]')].map(el=>[el.id,el]));
const buttons={cancel:root.querySelector('[data-action="cancel"]'),go:root.querySelector('[data-action="go"]')};
const tiles=new Map();
const mediaBase=new URL('./',import.meta.url);
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
let boardId=null,pathSignature='',previewSignature='',historySignature='',mediaBirdId=null,currentPhoto=null;

function text(el,value){if(el.textContent!==value)el.textContent=value;}
function moveText(n){return `${n} ${n===1?'move':'moves'}`;}
function hasBirdDetail(id){return Boolean(NAME_NOTES[id]&&NAME_NOTE_IMAGES[id]);}
function imageUrl(id){return new URL(NAME_NOTE_IMAGES[id].path,mediaBase).href;}
function thumbnailUrl(id){const media=NAME_NOTE_IMAGES[id];return new URL(media.thumbnailPath||media.path,mediaBase).href;}
function link(label,url){const a=document.createElement('a');a.textContent=label;a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
els.attribution.append('Names adapted from AviList Core Team, ',link('AviList 2026',SOURCE.url),', under ',link('CC BY 4.0',SOURCE.licenseUrl),'.');
text(els['mode-description'],`Daily puzzles are prepared through ${dateLabel(calendar.at(-1).date)}. They open at midnight in your time zone and are also available in the beta. Progress stays in this browser. Starting again keeps your best route.`);
if(isPlaytest){
  text(els['archive-heading'],'Puzzles');
  text(els['archive-description'],`All ${calendar.length} puzzles are available to try.`);
  text(els['mode-description'],`This beta contains ${calendar.length} puzzles. You can play them all, including those used in the daily game. Progress in each mode is saved separately. Starting again keeps your best route.`);
}

function nameNodes(bird,previous=null){
  const fragment=document.createDocumentFragment();
  let cursor=0;
  for(const [index,part]of bird.parts.entries()){
    const start=bird.name.toUpperCase().indexOf(part,cursor);
    if(start<0){fragment.replaceChildren(bird.name);return fragment;}
    if(start>cursor)fragment.append(bird.name.slice(cursor,start));
    const word=bird.name.slice(start,start+part.length);
    if(previous&&part!==previous.parts[index]){const mark=document.createElement('mark');mark.className='changed';mark.textContent=word;fragment.append(mark);}
    else fragment.append(word);
    cursor=start+part.length;
  }
  if(cursor<bird.name.length)fragment.append(bird.name.slice(cursor));
  return fragment;
}
function showStorageStatus(){els['storage-notice'].hidden=!session.storageUnavailable;}
function persist(){session.persist();showStorageStatus();}
function announce(message){text(els.status,message);}
function dateLabel(date,options={day:'numeric',month:'long',year:'numeric'}){return new Intl.DateTimeFormat('en-GB',options).format(new Date(`${date}T12:00:00`));}
function currentView(){return session.activeDate?engine.view():null;}
function puzzleIndex(date=session.activeDate){return calendar.findIndex(entry=>entry.date===date);}
function puzzleLabel(date){return isPlaytest?`Puzzle ${puzzleIndex(date)+1}`:dateLabel(date);}
function puzzleUrl(date,playtest=isPlaytest){
  const url=new URL(location.href);url.search='';url.hash='';url.searchParams.set('v','daily-4');
  if(playtest){url.searchParams.set('mode','playtest');url.searchParams.set('puzzle',(calendar.find(entry=>entry.date===date)||calendar[0]).puzzleId);}
  else if(date)url.searchParams.set('date',date);
  return url;
}
function scrollTop(){window.scrollTo({top:0,behavior:'instant'});}
function firstTile(){return [...tiles.values()].find(tile=>!tile.disabled);}
function focusPuzzleHeading(){els['game-heading'].focus({preventScroll:true});scrollTop();}

function makePath(path,withDetails=false){
  return path.map((bird,index)=>{
    const row=document.createElement('li');row.className='route-row';
    const step=document.createElement('span');step.className='step';step.textContent=index===0?'Start':String(index);
    row.append(step);
    if(!withDetails||!hasBirdDetail(bird.id)){
      const label=document.createElement('span');label.className='bird-label';label.append(nameNodes(bird));row.append(label);return row;
    }
    const button=document.createElement('button');button.type='button';button.className='bird-link';
    button.dataset.birdId=bird.id;button.dataset.pathIndex=String(index);
    button.setAttribute('aria-label',`${bird.name}: photo and name`);
    button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls','bird-detail');
    const frame=document.createElement('span');frame.className='route-thumb-frame';
    const photo=document.createElement('img');photo.className='route-thumb';photo.alt='';photo.loading='lazy';photo.decoding='async';
    photo.width=72;photo.height=48;
    photo.style.objectPosition=NAME_NOTE_IMAGES[bird.id].objectPosition||'50% 50%';
    if(bird.id==='avibase-67D43542')photo.style.transform='scale(1.22)';
    photo.addEventListener('error',()=>{
      if(!photo.isConnected)return;
      const fallback=document.createElement('span');fallback.className='route-thumb route-thumb-failed';fallback.textContent='Photo unavailable';fallback.setAttribute('aria-hidden','true');photo.replaceWith(fallback);
    },{once:true});
    frame.append(photo);
    const label=document.createElement('span');label.className='bird-label';label.textContent=bird.name;
    button.append(frame,label);row.append(button);
    // A thumbnail is created only for a completed route.
    photo.src=thumbnailUrl(bird.id);
    return row;
  });
}
function renderThumbnailCredits(path){
  const unique=[...new Map(path.filter(b=>hasBirdDetail(b.id)).map(b=>[b.id,b])).values()];
  els['thumbnail-credits'].hidden=!unique.length;
  els['thumbnail-credit-list'].replaceChildren();
  if(!unique.length)return;
  const intro=document.createElement('p');intro.textContent='Source previews are unchanged. Smaller previews are cropped for the route; larger photos keep the source framing.';els['thumbnail-credit-list'].append(intro);
  for(const bird of unique){
    const media=NAME_NOTE_IMAGES[bird.id],p=document.createElement('p');
    p.append(`${bird.name}: `,link(media.title||bird.name,media.sourcePage),` by ${media.creator} · `,link(media.license,media.licenseUrl));
    if(media.licenseNotice)p.append(' ',link(media.licenseNotice,media.licenseNoticeSource));
    els['thumbnail-credit-list'].append(p);
  }
}
function clearPhoto(){
  currentPhoto?.removeAttribute('src');currentPhoto=null;mediaBirdId=null;
  els['bird-image-frame'].replaceChildren(els['bird-image-status']);
  text(els['bird-image-status'],'');els['bird-image-status'].hidden=true;
  els['bird-photo-credit'].replaceChildren();
}
function renderPhoto(id){
  if(mediaBirdId===id)return;
  clearPhoto();
  if(!id)return;
  mediaBirdId=id;
  const media=NAME_NOTE_IMAGES[id],photo=document.createElement('img');
  photo.className='bird-photo';photo.alt=media.alt;photo.width=media.width;photo.height=media.height;photo.decoding='async';photo.hidden=true;
  photo.style.objectPosition=media.objectPosition;
  currentPhoto=photo;text(els['bird-image-status'],'Loading photo…');els['bird-image-status'].hidden=false;
  const isCurrent=()=>ui.note?.birdId===id&&currentPhoto===photo&&photo.isConnected;
  photo.addEventListener('load',()=>{if(isCurrent()){photo.hidden=false;els['bird-image-status'].hidden=true;}});
  photo.addEventListener('error',()=>{if(isCurrent()){photo.hidden=true;text(els['bird-image-status'],'Photo unavailable.');els['bird-image-status'].hidden=false;}});
  els['bird-image-frame'].append(photo);
  els['bird-photo-credit'].append('Photo: ',link(media.creator,media.sourcePage),' · ',link(media.license,media.licenseUrl));
  photo.src=imageUrl(id);
}
function renderBirdDetail(view){
  if(!view.won||ui.screen!=='puzzle'||view.path[ui.note?.pathIndex]?.id!==ui.note?.birdId)ui.note=null;
  const id=ui.note?.birdId,note=id&&NAME_NOTES[id];
  for(const button of els['finished-path'].querySelectorAll('.bird-link')){
    button.setAttribute('aria-expanded',String(Boolean(note)&&Number(button.dataset.pathIndex)===ui.note.pathIndex));
  }
  els['bird-detail'].hidden=!note;
  if(!note){renderPhoto(null);els['bird-sources'].replaceChildren();return;}
  text(els['bird-title'],note.name);text(els['bird-latin'],note.scientificName);text(els['bird-copy'],note.text);
  renderPhoto(id);
  // Leave focused source anchors in place when other controls change.
  if(els['bird-sources'].dataset.birdId!==id||!els['bird-sources'].childElementCount){
    els['bird-sources'].dataset.birdId=id;
    els['bird-sources'].replaceChildren(...note.sources.map(s=>link(s.title,s.url)));
  }
}
function renderResult(view){
  els.result.hidden=!view.won;
  if(!view.won){
    ui.solutionShown=false;ui.note=null;pathSignature='';
    els['finished-path'].replaceChildren();els['thumbnail-credit-list'].replaceChildren();
    els['thumbnail-credits'].hidden=true;els['thumbnail-credits'].open=false;
    renderBirdDetail(view);return;
  }
  text(els['result-title'],view.perfect?'Perfect!':'You made it.');
  text(els['result-count'],moveText(view.moves));
  text(els['result-description'],view.perfect?'That’s a shortest route.':`A shortest route takes ${moveText(view.shortest)}.`);
  text(els['retry-main'],view.perfect?'Play again':'Try a shorter route');
  text(els['next-puzzle-button'],isPlaytest?(puzzleIndex()<calendar.length-1?'Next puzzle':'Choose a puzzle'):'Play more puzzles');
  els['next-puzzle-button'].className='primary';
  els['retry-main'].className='link-button';
  els['next-daily-copy'].hidden=isPlaytest;
  text(els['next-daily-copy'],calendar.some(entry=>entry.date>session.todayDate)?'Daily puzzles open at midnight.':`You can try all ${calendar.length} puzzles in the beta.`);
  els['solution-button'].hidden=view.perfect;
  text(els['solution-button'],ui.solutionShown?'Hide shortest route':'Show shortest route');
  els['solution-button'].setAttribute('aria-expanded',String(ui.solutionShown));
  els.solution.hidden=!ui.solutionShown;
  text(els['solution-path'],ui.solutionShown?view.solution.map(b=>b.name).join(' → '):'');
  const signature=`${view.round.id}|${view.path.map(b=>b.id).join('|')}`;
  if(signature!==pathSignature){
    pathSignature=signature;
    els['finished-path'].replaceChildren(...makePath(view.path,true));
    renderThumbnailCredits(view.path);
  }
  els['bird-cue'].hidden=!view.path.some(b=>hasBirdDetail(b.id));
  renderBirdDetail(view);
}
function renderBoard(view){
  if(boardId!==view.round.id){
    boardId=view.round.id;tiles.clear();
    for(const part of view.round.parts){
      const button=document.createElement('button');button.type='button';button.className='tile';button.dataset.part=part;
      button.textContent=part.charAt(0)+part.slice(1).toLowerCase();button.setAttribute('aria-pressed','false');tiles.set(part,button);
    }
    els['word-box'].replaceChildren(...tiles.values());
  }
  text(els['start-name'],view.start.name);text(els['goal-name'],view.target.name);text(els['current-name'],view.current.name);
  text(els.moves,moveText(view.moves));els.best.hidden=view.bestMoves===null;text(els.best,view.bestMoves===null?'':`Best: ${view.bestMoves}`);
  els.play.hidden=view.won;els.history.hidden=view.won;els['restart-row'].hidden=view.won;
  const available=new Set(view.replacements.map(r=>r.part));
  const pending=view.completeBird?.parts.find((p,i)=>p!==view.current.parts[i]);
  for(const [part,tile]of tiles){tile.disabled=view.won||!available.has(part);tile.setAttribute('aria-pressed',String(part===pending));}
  buttons.cancel.disabled=!view.completeBird;buttons.go.disabled=!view.completeBird;
  els['restart-button'].disabled=view.moves===0&&!view.draft.length;
  const signature=`${view.round.id}|${view.current.id}|${view.completeBird?.id||''}`;
  if(signature!==previewSignature){
    previewSignature=signature;
    els['next-name'].classList.toggle('empty',!view.completeBird);
    if(view.completeBird)els['next-name'].replaceChildren(nameNodes(view.completeBird,view.current));
    else text(els['next-name'],'Choose a word.');
  }
  text(els['history-label'],view.moves?`Your route · ${moveText(view.moves)}`:'Your route');
  const history=`${view.round.id}|${view.path.map(b=>b.id).join('|')}`;
  if(history!==historySignature){historySignature=history;els['history-path'].replaceChildren(...makePath(view.path));}
  renderResult(view);
}
function renderHelp(){
  els['how-to'].hidden=!ui.helpOpen||ui.screen==='archive';
  els['help-button'].setAttribute('aria-expanded',String(!els['how-to'].hidden));
}
function renderArchive(){
  const puzzles=session.puzzleSummaries().filter(puzzle=>isPlaytest||puzzle.date<session.todayDate);
  if(isPlaytest)puzzles.sort((a,b)=>a.date.localeCompare(b.date));
  els['archive-empty'].hidden=puzzles.length>0;
  const fragment=document.createDocumentFragment();let month=null,list;
  if(isPlaytest){list=document.createElement('ol');list.className='puzzle-list';list.setAttribute('aria-label','All puzzles');fragment.append(list);}
  for(const puzzle of puzzles){
    if(!isPlaytest&&month!==puzzle.date.slice(0,7)){
      month=puzzle.date.slice(0,7);
      const heading=document.createElement('h3');heading.className='archive-month';heading.textContent=dateLabel(puzzle.date,{month:'long',year:'numeric'});
      list=document.createElement('ol');list.className='puzzle-list';list.setAttribute('aria-label',heading.textContent);
      fragment.append(heading,list);
    }
    const row=document.createElement('li'),button=document.createElement('button');button.type='button';button.dataset.date=puzzle.date;
    if(puzzle.active)button.setAttribute('aria-current','true');
    const title=document.createElement('span');title.className='puzzle-title';
    const date=document.createElement(isPlaytest?'span':'time');
    if(isPlaytest){date.className='puzzle-number';date.textContent=puzzleLabel(puzzle.date);}
    else{date.dateTime=puzzle.date;date.textContent=dateLabel(puzzle.date,{weekday:'short',day:'numeric',month:'short'});}
    const birds=document.createElement('span');birds.className='archive-birds';birds.textContent=`${puzzle.from} → ${puzzle.to}`;title.append(date,birds);
    const status=document.createElement('span');status.className='puzzle-status';
    status.textContent=puzzle.status==='in-progress'?`In progress · ${moveText(puzzle.moves)}`:puzzle.bestMoves!==null?`${puzzle.perfect?'Perfect':'Best'} · ${moveText(puzzle.bestMoves)}`:'Not started';
    if(puzzle.status==='in-progress'&&puzzle.bestMoves!==null){const best=document.createElement('small');best.textContent=`Best · ${moveText(puzzle.bestMoves)}`;status.append(' ',best);}
    button.append(title,status);row.append(button);list.append(row);
  }
  els['archive-list'].replaceChildren(fragment);
}
function renderDateAndNotice(){
  const active=session.activeDate;
  if(isPlaytest){
    text(els['round-label'],`Beta · ${puzzleLabel(active)} of ${calendar.length}`);
    text(els['today-button'],'Daily puzzle');els['today-button'].hidden=false;els['daily-notice'].hidden=true;return;
  }
  text(els['round-label'],active?`${active===session.todayDate?'Today · ':''}${dateLabel(active)}`:dateLabel(session.todayDate));
  els['today-button'].hidden=!active||active===session.todayDate;
  const available=content.schedule.some(entry=>entry.date===session.todayDate);
  els['daily-notice'].hidden=!ui.rolloverNotice||active===session.todayDate;
  text(els['daily-notice-copy'],available?'Today’s puzzle is ready.':'The date has changed. Your route is still here.');
  text(els['new-today-button'],available?'Play today':'Today');
}
function renderScreen(){
  const view=currentView(),archive=ui.screen==='archive';
  els['puzzle-screen'].hidden=archive||!view;els['archive-screen'].hidden=!archive;els['empty-screen'].hidden=archive||Boolean(view);
  text(els['archive-button'],archive?'Back':isPlaytest?'Puzzles':'Archive');
  els['archive-button'].setAttribute('aria-expanded',String(archive));
  renderDateAndNotice();renderHelp();
  if(view)renderBoard(view);
  else{
    ui.note=null;clearPhoto();
    text(els['empty-heading'],session.calendarStatus()==='before-start'?'The first puzzle is coming.':'No puzzle for today');
    text(els['empty-copy'],session.calendarStatus()==='before-start'?`The first puzzle is on ${dateLabel(session.firstDate)}.`:'There isn’t a puzzle for this date. You can still play earlier puzzles in the archive.');
  }
  if(archive)renderArchive();showStorageStatus();return view;
}
function clearTransient(){ui.screen='puzzle';ui.helpOpen=false;ui.solutionShown=false;ui.note=null;els.history.open=false;els['thumbnail-credits'].open=false;}
function focusCurrent(){if(session.activeDate)focusPuzzleHeading();else{els['empty-heading'].focus({preventScroll:true});scrollTop();}}
function writeLocation(date,replace=false){
  const url=puzzleUrl(date);
  history[replace?'replaceState':'pushState']({date},'',url);
}
function handleArchiveToggle(){
  ui.screen=ui.screen==='archive'?'puzzle':'archive';ui.helpOpen=false;ui.note=null;renderScreen();
  if(ui.screen==='archive'){els['archive-heading'].focus({preventScroll:true});scrollTop();}else focusCurrent();
}
function handleArchiveSelect(date){
  if((!isPlaytest&&date>=session.todayDate)||!session.selectDate(date))return;
  clearTransient();ui.rolloverNotice=false;writeLocation(date);renderScreen();focusCurrent();
  announce(`${puzzleLabel(date)}. ${engine.view().start.name} to ${engine.view().target.name}.`);
}
function handleNextPuzzle(){
  const next=calendar[puzzleIndex()+1];
  if(!isPlaytest){location.assign(puzzleUrl((next||calendar[0]).date,true));return;}
  if(!next){handleArchiveToggle();return;}
  if(!session.selectPuzzle(next.puzzleId))return;
  clearTransient();writeLocation(next.date);renderScreen();focusCurrent();
  announce(`${puzzleLabel(next.date)}. ${engine.view().start.name} to ${engine.view().target.name}.`);
}
function handleToday(){
  if(isPlaytest){location.assign(puzzleUrl(null,false));return;}
  session.refreshToday();session.openToday();clearTransient();ui.rolloverNotice=false;writeLocation(null);renderScreen();focusCurrent();
}
function handlePlayNewToday(){handleToday();}
function selectFromLocation(normalize=false){
  const params=new URLSearchParams(location.search),dates=params.getAll('date');
  if(isPlaytest){
    const ids=params.getAll('puzzle'),valid=ids.length===1&&session.selectPuzzle(ids[0]);
    if(!valid)session.selectPuzzle(calendar[0].puzzleId);
    if(normalize&&(!valid||dates.length))writeLocation(session.activeDate,true);
    return;
  }
  const valid=dates.length===1&&session.selectDate(dates[0]);
  if(!valid)session.openToday();
  if(normalize&&((dates.length&&!valid)||params.has('mode')||params.has('puzzle')))writeLocation(valid?dates[0]:null,true);
}
function handlePopState(){
  session.refreshToday();selectFromLocation();clearTransient();ui.rolloverNotice=false;renderScreen();focusCurrent();
}
let midnightTimer;
function scheduleMidnight(){clearTimeout(midnightTimer);if(!isPlaytest)midnightTimer=setTimeout(handleRollover,nextMidnightDelay(new Date())+50);}
function handleRollover(){
  if(isPlaytest)return;
  const previousDate=session.todayDate;
  if(session.refreshToday()){
    if(session.activeDate&&session.activeDate!==session.todayDate&&!new URLSearchParams(location.search).has('date'))writeLocation(session.activeDate,true);
    ui.rolloverNotice=session.activeDate!==session.todayDate;
    renderDateAndNotice();
    if(ui.screen==='archive')renderArchive();
    if(!session.activeDate)renderScreen();
    if(session.todayDate!==previousDate)announce('The date has changed. Your current route is kept.');
  }
  scheduleMidnight();
}
function handleHelpToggle(){
  if(ui.screen==='archive'){ui.screen='puzzle';renderScreen();}
  ui.helpOpen=!ui.helpOpen;renderHelp();
}
function handleSolutionToggle(){
  const view=currentView();if(!view?.won||view.perfect)return;
  ui.solutionShown=!ui.solutionShown;renderResult(view);
  announce(ui.solutionShown?'One shortest route is shown.':'Shortest route hidden.');
}
function handleBirdOpen(button){
  const view=engine.view(),birdId=button.dataset.birdId,pathIndex=Number(button.dataset.pathIndex);
  if(!session.activeDate||!view.won||view.path[pathIndex]?.id!==birdId||!hasBirdDetail(birdId))return;
  if(ui.note?.pathIndex===pathIndex){handleBirdClose();return;}
  ui.note={birdId,pathIndex,trigger:button};renderBirdDetail(view);
  els['bird-title'].focus({preventScroll:true});els['bird-detail'].scrollIntoView({block:'start',behavior:'instant'});
}
function handleBirdClose(){
  const trigger=ui.note?.trigger;ui.note=null;renderBirdDetail(engine.view());
  if(trigger?.isConnected){trigger.focus({preventScroll:true});trigger.scrollIntoView({block:'nearest',behavior:'instant'});}
}
function handleRetry(){
  if(!session.activeDate||!engine.restartRound())return;
  ui.note=null;ui.solutionShown=false;els.history.open=false;els['thumbnail-credits'].open=false;
  persist();renderScreen();firstTile()?.focus({preventScroll:true});scrollTop();announce('New attempt. Your best route is kept.');
}
function handleRouteClick(event){
  const button=event.target.closest('button');if(!button||!root.contains(button)||button.disabled)return;
  if(button.id==='archive-button'||button.dataset.action==='archive'){handleArchiveToggle();return;}
  if(button.id==='today-button'){handleToday();return;}
  if(button.id==='new-today-button'){handlePlayNewToday();return;}
  if(button.id==='help-button'){handleHelpToggle();return;}
  if(button.dataset.date){handleArchiveSelect(button.dataset.date);return;}
  if(button.dataset.birdId){handleBirdOpen(button);return;}
  if(button.dataset.action==='retry'){handleRetry();return;}
  if(button.dataset.action==='next-puzzle'){handleNextPuzzle();return;}
  if(button.dataset.action==='solution'){handleSolutionToggle();return;}
  if(button.dataset.action==='close-bird'){handleBirdClose();return;}
  if(!session.activeDate)return;
  let accepted=false;
  if(button.dataset.part)accepted=engine.setReplacement(button.dataset.part);
  else if(button.dataset.action==='cancel')accepted=engine.clearDraft();
  else if(button.dataset.action==='go')accepted=engine.commitBird();
  if(!accepted)return;
  persist();const view=renderScreen();
  if(button.dataset.part){
    button.focus({preventScroll:true});
    if(!reducedMotion.matches)els['next-name'].querySelector('.changed')?.classList.add('is-settling');
    announce(`Next bird: ${view.completeBird.name}. Press Go to make the move.`);
  }else if(view.won){
    els['next-puzzle-button'].focus({preventScroll:true});announce(`${view.perfect?'Perfect!':'You made it.'} ${moveText(view.moves)}.`);
  }else{
    firstTile()?.focus({preventScroll:true});announce(button.dataset.action==='cancel'?'Preview cleared.':`${view.current.name}. ${moveText(view.moves)}.`);
  }
}
root.addEventListener('click',handleRouteClick);
root.addEventListener('keydown',event=>{if(event.key==='Escape'&&ui.note){event.preventDefault();handleBirdClose();}});
selectFromLocation(true);
renderScreen();
scheduleMidnight();
window.addEventListener('popstate',handlePopState);
window.addEventListener('focus',handleRollover);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)handleRollover();});
window.addEventListener('pagehide',()=>clearTimeout(midnightTimer));
window.addEventListener('pageshow',handleRollover);
