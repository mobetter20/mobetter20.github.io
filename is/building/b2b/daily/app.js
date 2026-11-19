import {createDailySession,nextMidnightDelay} from './state.js?v=daily-9';
import {SOURCE,LEXICON} from '../route/world-lexicon.js';

async function loadData(){
    return await Promise.all(['content.json','notes.json','media.json'].map(async file=>{
      const response=await fetch(new URL(`${file}?v=daily-9`,import.meta.url));
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
const ui={screen:'puzzle',helpOpen:false,menuOpen:false,solutionShown:false,note:null,rolloverNotice:false};
const els=Object.fromEntries([...root.querySelectorAll('[id]')].map(el=>[el.id,el]));
const nameBoard=root.querySelector('.name-board');
const tiles=new Map();
const mediaBase=new URL('./',import.meta.url);
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
let boardId=null,pathSignature='',currentSignature='',historySignature='',mediaBirdId=null,currentPhoto=null;

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
function discardLegacyDraft(){
  // Only the active date may have just been refreshed from another tab. Clearing
  // other dates here could overwrite newer routes that this tab has not loaded.
  if(session.activeDate&&engine.clearDraft())persist();
}
function announce(message){text(els.status,message);}
function dateLabel(date,options={day:'numeric',month:'long',year:'numeric'}){return new Intl.DateTimeFormat('en-GB',options).format(new Date(`${date}T12:00:00`));}
function currentView(){return session.activeDate?engine.view():null;}
function puzzleIndex(date=session.activeDate){return calendar.findIndex(entry=>entry.date===date);}
function puzzleLabel(date){return isPlaytest?`Puzzle ${puzzleIndex(date)+1}`:dateLabel(date);}
function puzzleUrl(date,playtest=isPlaytest){
  const url=new URL(location.href);url.search='';url.hash='';url.searchParams.set('v','daily-9');
  if(playtest){url.searchParams.set('mode','playtest');url.searchParams.set('puzzle',(calendar.find(entry=>entry.date===date)||calendar[0]).puzzleId);}
  else if(date)url.searchParams.set('date',date);
  return url;
}
function scrollTop(){window.scrollTo({top:0,behavior:'instant'});}
function firstTile(){return els['word-box'].querySelector('.tile:not(:disabled)');}
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
  const rows=unique.map(bird=>{
    const media=NAME_NOTE_IMAGES[bird.id],row=document.createElement('li');
    row.className='credit-row';row.dataset.birdId=bird.id;
    const heading=document.createElement('h3');heading.textContent=bird.name;
    const creator=document.createElement('p');creator.className='credit-creator';creator.textContent=media.creator;
    const actions=document.createElement('div');actions.className='credit-actions';
    const details=document.createElement('details');details.className='credit-details';
    const summary=document.createElement('summary');summary.textContent='Details';
    const title=document.createElement('p');title.textContent=media.title||bird.name;
    const changes=document.createElement('p');changes.textContent=media.changes;
    details.append(summary,title,changes);
    if(media.licenseNotice){
      const notice=document.createElement('p');notice.append(media.licenseNotice,' ',link('License history',media.licenseNoticeSource));details.append(notice);
    }
    actions.append(link('Source photo',media.sourcePage),link(media.license,media.licenseUrl),details);
    row.append(heading,creator,actions);return row;
  });
  els['thumbnail-credit-list'].replaceChildren(...rows);
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
  if(!note){renderPhoto(null);els['bird-source-details'].open=false;els['bird-sources'].replaceChildren();return;}
  text(els['bird-title'],note.name);text(els['bird-latin'],note.scientificName);text(els['bird-copy'],note.text);
  renderPhoto(id);
  // Leave focused source anchors in place when other controls change.
  if(els['bird-sources'].dataset.birdId!==id||!els['bird-sources'].childElementCount){
    els['bird-source-details'].open=false;
    els['bird-sources'].dataset.birdId=id;
    els['bird-sources'].replaceChildren(...note.sources.map(s=>link(s.title,s.url)));
  }
}
function renderResult(view){
  els.result.hidden=!view.won;
  els.result.classList.toggle('is-perfect',view.won&&view.perfect);
  if(!view.won||ui.screen!=='puzzle')els['result-bird'].classList.remove('is-celebrating');
  if(!view.won){
    ui.solutionShown=false;ui.note=null;pathSignature='';
    els['finished-path'].replaceChildren();els['thumbnail-credit-list'].replaceChildren();
    els['thumbnail-credits'].hidden=true;els['thumbnail-credits'].open=false;
    renderBirdDetail(view);return;
  }
  text(els['result-title'],view.perfect?'Perfect!':'You made it.');
  text(els['result-count'],moveText(view.moves));
  const betterBest=view.bestMoves!==null&&view.bestMoves<view.moves;
  text(els['result-description'],view.perfect?'That’s a shortest route.':betterBest?`Shortest: ${view.shortest} · Your best: ${view.bestMoves}`:`A shortest route takes ${moveText(view.shortest)}.`);
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
    const words=new Set(view.round.parts),firstWords=new Set();
    // Match the two name halves using every bird in this board, including detours.
    for(const bird of LEXICON){
      if(bird.parts.length===2&&bird.parts.every(part=>words.has(part)))firstWords.add(bird.parts[0]);
    }
    const columns=[0,1].map(index=>{
      const column=document.createElement('div');column.className='tile-column';column.dataset.position=String(index);
      column.setAttribute('role','group');column.setAttribute('aria-label',index===0?'First word':'Second word');return column;
    });
    for(const part of [...view.round.parts].sort()){
      const button=document.createElement('button');button.type='button';button.className='tile';button.dataset.part=part;
      button.textContent=part.charAt(0)+part.slice(1).toLowerCase();tiles.set(part,button);
      columns[firstWords.has(part)?0:1].append(button);
    }
    els['word-box'].replaceChildren(...columns);
  }
  text(els['goal-name'],view.target.name);text(els.moves,moveText(view.moves));
  els['goal-reach'].hidden=view.won;els['goal-complete'].hidden=!view.won;
  els.goal.classList.toggle('is-complete',view.won);
  els.best.hidden=view.bestMoves===null;text(els.best,view.bestMoves===null?'':`Best: ${moveText(view.bestMoves)}`);
  els.play.hidden=view.won;els.history.hidden=view.won;
  const available=new Set(view.replacements.map(r=>r.part));
  for(const [part,tile]of tiles)tile.disabled=view.won||!available.has(part);
  els['restart-button'].disabled=view.moves===0;
  const signature=`${view.round.id}|${view.current.id}`;
  if(signature!==currentSignature){
    currentSignature=signature;
    const bird=view.current,fragment=document.createDocumentFragment();
    let cursor=0;
    for(const part of bird.parts){
      const start=bird.name.toUpperCase().indexOf(part,cursor),piece=document.createElement('span');
      piece.className='name-part';piece.classList.toggle('long-name',part.length>=10);
      piece.textContent=bird.name.slice(start,start+part.length);
      fragment.append(piece);cursor=start+part.length;
    }
    els['current-name'].replaceChildren(fragment);
    els['current-name'].setAttribute('aria-label',`Current bird: ${bird.name}`);
  }
  text(els['history-label'],'Your route');
  const history=`${view.round.id}|${view.path.map(b=>b.id).join('|')}`;
  if(history!==historySignature){historySignature=history;els['history-path'].replaceChildren(...makePath(view.path));}
  renderResult(view);
  updateNameLayout();
  requestAnimationFrame(updateNameLayout);
}
function updateNameLayout(){
  const [first,second]=els['current-name'].children;
  nameBoard.classList.toggle('is-stacked',Boolean(first&&second&&second.offsetTop>first.offsetTop));
}
function handleResize(){renderMenu();updateNameLayout();}
function renderMenu(){
  els['game-menu'].hidden=!ui.menuOpen;
  els['menu-button'].setAttribute('aria-expanded',String(ui.menuOpen));
  if(ui.menuOpen){
    const header=root.querySelector('.masthead');
    els['game-menu'].style.top=`${header.offsetTop+header.offsetHeight+12}px`;
  }
}
function closeMenu({restoreFocus=false}={}){
  if(!ui.menuOpen)return;
  ui.menuOpen=false;renderMenu();
  if(restoreFocus)els['menu-button'].focus({preventScroll:true});
}
function handleMenuToggle(){
  ui.menuOpen=!ui.menuOpen;ui.helpOpen=false;renderHelp();renderMenu();
}
function handleDocumentPointerDown(event){
  if(!ui.menuOpen||els['game-menu'].contains(event.target)||els['menu-button'].contains(event.target))return;
  closeMenu({restoreFocus:els['game-menu'].contains(document.activeElement)});
}
function handleRootKeydown(event){
  // Enter can commit a word and move focus to another word or Next puzzle.
  // A held key must not activate that newly focused button repeatedly.
  if(event.repeat&&(event.key==='Enter'||event.key===' ')&&event.target.closest('button')){event.preventDefault();return;}
  if(event.key!=='Escape')return;
  if(ui.menuOpen){event.preventDefault();closeMenu({restoreFocus:true});}
  else if(ui.helpOpen){event.preventDefault();handleHelpClose();}
  else if(ui.note){event.preventDefault();handleBirdClose();}
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
    const inProgress=puzzle.status==='in-progress'&&puzzle.moves>0;
    status.textContent=inProgress?`In progress · ${moveText(puzzle.moves)}`:puzzle.bestMoves!==null?`${puzzle.perfect?'Perfect':'Best'} · ${moveText(puzzle.bestMoves)}`:'Not started';
    if(inProgress&&puzzle.bestMoves!==null){const best=document.createElement('small');best.textContent=`Best · ${moveText(puzzle.bestMoves)}`;status.append(' ',best);}
    button.append(title,status);row.append(button);list.append(row);
  }
  els['archive-list'].replaceChildren(fragment);
}
function renderDateAndNotice(){
  const active=session.activeDate;
  if(isPlaytest){
    text(els['round-label'],`${puzzleLabel(active)} of ${calendar.length}`);
    text(els['today-button'],'Daily');els['today-button'].hidden=false;els['today-button'].disabled=false;els['today-button'].removeAttribute('aria-current');els['daily-notice'].hidden=true;return;
  }
  text(els['round-label'],active?`${active===session.todayDate?'Today · ':''}${dateLabel(active)}`:dateLabel(session.todayDate));
  els['today-button'].hidden=false;text(els['today-button'],'Daily');
  els['today-button'].disabled=active===session.todayDate&&ui.screen==='puzzle';
  if(active===session.todayDate)els['today-button'].setAttribute('aria-current','page');else els['today-button'].removeAttribute('aria-current');
  const available=content.schedule.some(entry=>entry.date===session.todayDate);
  els['daily-notice'].hidden=!ui.rolloverNotice||active===session.todayDate;
  text(els['daily-notice-copy'],available?'Today’s puzzle is ready.':'The date has changed. Your route is still here.');
  text(els['new-today-button'],available?'Play today':'Today');
}
function renderScreen(){
  discardLegacyDraft();
  const view=currentView(),archive=ui.screen==='archive';
  els['puzzle-screen'].hidden=archive||!view;els['archive-screen'].hidden=!archive;els['empty-screen'].hidden=archive||Boolean(view);
  text(els['archive-button'],'Puzzles');
  els['archive-button'].setAttribute('aria-expanded',String(archive));
  renderDateAndNotice();renderHelp();renderMenu();
  if(view)renderBoard(view);
  else{
    ui.note=null;clearPhoto();els['restart-button'].disabled=true;
    text(els['empty-heading'],session.calendarStatus()==='before-start'?'The first puzzle is coming.':'No puzzle for today');
    text(els['empty-copy'],session.calendarStatus()==='before-start'?`The first puzzle is on ${dateLabel(session.firstDate)}.`:'There isn’t a puzzle for this date. You can still play earlier puzzles in the archive.');
  }
  if(archive)renderArchive();showStorageStatus();return view;
}
function clearTransient(){ui.screen='puzzle';ui.helpOpen=false;ui.menuOpen=false;ui.solutionShown=false;ui.note=null;els.history.open=false;els['thumbnail-credits'].open=false;els['result-bird'].classList.remove('is-celebrating');}
function focusCurrent(){if(session.activeDate)focusPuzzleHeading();else{els['empty-heading'].focus({preventScroll:true});scrollTop();}}
function writeLocation(date,replace=false){
  const url=puzzleUrl(date);
  history[replace?'replaceState':'pushState']({date},'',url);
}
function handleArchiveToggle(){
  closeMenu();
  ui.screen=ui.screen==='archive'?'puzzle':'archive';ui.helpOpen=false;ui.note=null;renderScreen();
  if(ui.screen==='archive'){els['archive-heading'].focus({preventScroll:true});scrollTop();}else focusCurrent();
}
function handleArchiveSelect(date){
  if((!isPlaytest&&date>=session.todayDate)||!session.selectDate(date))return;
  clearTransient();ui.rolloverNotice=false;writeLocation(date);renderScreen();focusCurrent();
  announce(`${puzzleLabel(date)}. ${engine.view().start.name} to ${engine.view().target.name}.`);
}
function handleNextPuzzle(){
  closeMenu();
  const next=calendar[puzzleIndex()+1];
  if(!isPlaytest){location.assign(puzzleUrl((next||calendar[0]).date,true));return;}
  if(!next){handleArchiveToggle();return;}
  if(!session.selectPuzzle(next.puzzleId))return;
  clearTransient();writeLocation(next.date);renderScreen();focusCurrent();
  announce(`${puzzleLabel(next.date)}. ${engine.view().start.name} to ${engine.view().target.name}.`);
}
function handleToday(){
  closeMenu();
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
  closeMenu();
  if(ui.screen==='archive'){ui.screen='puzzle';renderScreen();}
  ui.helpOpen=!ui.helpOpen;renderHelp();
}
function handleHelpClose(){ui.helpOpen=false;renderHelp();els['help-button'].focus({preventScroll:true});}
function handleSolutionToggle(){
  const view=currentView();if(!view?.won||view.perfect)return;
  ui.solutionShown=!ui.solutionShown;renderResult(view);
  announce(ui.solutionShown?'One shortest route is shown.':'Shortest route hidden.');
}
function handleBirdOpen(button){
  const view=engine.view(),birdId=button.dataset.birdId,pathIndex=Number(button.dataset.pathIndex);
  if(!session.activeDate||!view.won||view.path[pathIndex]?.id!==birdId||!hasBirdDetail(birdId))return;
  if(ui.note?.pathIndex===pathIndex){handleBirdClose();return;}
  ui.note={birdId,pathIndex,trigger:button,scrollX:window.scrollX,scrollY:window.scrollY};renderBirdDetail(view);
  els['bird-title'].focus({preventScroll:true});els['bird-detail'].scrollIntoView({block:'start',behavior:'instant'});
}
function handleBirdClose(){
  const openedDetail=ui.note;if(!openedDetail)return;
  ui.note=null;renderBirdDetail(engine.view());
  if(openedDetail.trigger?.isConnected)openedDetail.trigger.focus({preventScroll:true});
  // Restore the view that opened the article, including the result actions.
  window.scrollTo({left:openedDetail.scrollX,top:openedDetail.scrollY,behavior:'instant'});
}
function handleRetry(){
  closeMenu();
  if(!session.activeDate||!engine.restartRound())return;
  ui.screen='puzzle';ui.helpOpen=false;
  ui.note=null;ui.solutionShown=false;els.history.open=false;els['thumbnail-credits'].open=false;
  persist();renderScreen();firstTile()?.focus({preventScroll:true});scrollTop();announce('New attempt. Your best route is kept.');
}
function handleWordCommit(part){
  if(!session.activeDate)return;
  // A stale draft from an older client must never make the first same-word tap a no-op.
  const discarded=engine.clearDraft();
  const changedIndex=engine.view().replacements.find(choice=>choice.part===part)?.index;
  if(!engine.setReplacement(part)){
    if(discarded){persist();renderScreen();}
    return;
  }
  if(!engine.commitBird()){
    engine.clearDraft();persist();renderScreen();return;
  }
  persist();const view=renderScreen();
  if(view.won){
    els['next-puzzle-button'].focus({preventScroll:true});
    const resultBounds=els['result-heading'].getBoundingClientRect();
    if(resultBounds.top<0||resultBounds.bottom>window.innerHeight)els['result-heading'].scrollIntoView({block:'start',behavior:'instant'});
    announce(`${view.perfect?'Perfect!':'You made it.'} ${moveText(view.moves)}.`);
    if(view.perfect&&!reducedMotion.matches)els['result-bird'].classList.add('is-celebrating');
  }else{
    firstTile()?.focus({preventScroll:true});announce(`${view.current.name}. ${moveText(view.moves)}.`);
    if(!reducedMotion.matches&&changedIndex!==undefined)els['current-name'].children[changedIndex]?.classList.add('is-changed');
  }
}
function handleRouteClick(event){
  const button=event.target.closest('button');if(!button||!root.contains(button)||button.disabled)return;
  if(button.id==='archive-button'||button.dataset.action==='archive'){handleArchiveToggle();return;}
  if(button.id==='today-button'){handleToday();return;}
  if(button.id==='new-today-button'){handlePlayNewToday();return;}
  if(button.id==='help-button'){handleHelpToggle();return;}
  if(button.id==='help-close'){handleHelpClose();return;}
  if(button.id==='menu-button'){handleMenuToggle();return;}
  if(button.dataset.date){handleArchiveSelect(button.dataset.date);return;}
  if(button.dataset.birdId){handleBirdOpen(button);return;}
  if(button.dataset.action==='retry'){handleRetry();return;}
  if(button.dataset.action==='next-puzzle'){handleNextPuzzle();return;}
  if(button.dataset.action==='solution'){handleSolutionToggle();return;}
  if(button.dataset.action==='close-bird'){handleBirdClose();return;}
  if(button.dataset.part)handleWordCommit(button.dataset.part);
}
root.addEventListener('click',handleRouteClick);
root.addEventListener('keydown',handleRootKeydown);
els['result-bird'].addEventListener('animationend',()=>els['result-bird'].classList.remove('is-celebrating'));
reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches)els['result-bird'].classList.remove('is-celebrating');});
document.addEventListener('pointerdown',handleDocumentPointerDown);
window.addEventListener('resize',handleResize);
document.fonts.ready.then(updateNameLayout);
selectFromLocation(true);
renderScreen();
const nameLayoutObserver=typeof ResizeObserver==='function'?new ResizeObserver(updateNameLayout):null;
nameLayoutObserver?.observe(els['current-name']);
scheduleMidnight();
window.addEventListener('popstate',handlePopState);
window.addEventListener('focus',handleRollover);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)handleRollover();});
window.addEventListener('pagehide',()=>clearTimeout(midnightTimer));
window.addEventListener('pageshow',handleRollover);
