// Authored daily calendar and save adapter. The route engine owns move validation.
import {createRouteEngine} from '../route/engine.js';

export const STORAGE_KEY='bird-to-bird:daily:1';
export const PLAYTEST_STORAGE_KEY='bird-to-bird:playtest:1';

function validDateKey(value){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
  const [year,month,day]=value.split('-').map(Number);
  if(year<1||month<1||month>12)return false;
  const leap=year%4===0&&(year%100!==0||year%400===0);
  return day>=1&&day<=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31][month-1];
}
function requireDate(date){
  if(!(date instanceof Date)||!Number.isFinite(date.getTime()))throw new TypeError('A valid local Date is required.');
  return date;
}
export function localDateKey(date){
  requireDate(date);
  const key=`${String(date.getFullYear()).padStart(4,'0')}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
  if(!validDateKey(key))throw new RangeError('The local date is outside the supported calendar.');
  return key;
}
export function nextMidnightDelay(date){
  requireDate(date);
  const midnight=new Date(date.getTime());
  // Calendar arithmetic respects 23- and 25-hour daylight-saving days.
  midnight.setHours(24,0,0,0);
  return Math.max(1,midnight.getTime()-date.getTime());
}

export function createDailySession({
  schedule,rounds,lexicon,sourceVersion,
  mode='daily',
  getStorage=()=>globalThis.localStorage,
  now=()=>new Date(),
}={}){
  if(mode!=='daily'&&mode!=='playtest')throw new Error('Unknown game mode.');
  const playtest=mode==='playtest',storageKey=playtest?PLAYTEST_STORAGE_KEY:STORAGE_KEY;
  if(!Array.isArray(schedule)||!schedule.length)throw new Error('The daily schedule is empty.');
  if(!Array.isArray(rounds)||!rounds.length)throw new Error('The daily puzzle bank is empty.');
  if(typeof sourceVersion!=='string'||!sourceVersion)throw new Error('A source version is required.');
  const bank=new Map();
  for(const round of rounds){
    if(!round||typeof round.id!=='string'||!round.id||bank.has(round.id))throw new Error('Invalid or duplicate daily puzzle.');
    bank.set(round.id,{...round,parts:Array.isArray(round.parts)?[...round.parts]:round.parts});
  }
  const dates=new Map();
  for(const entry of schedule){
    if(!entry||!validDateKey(entry.date)||dates.has(entry.date)||!bank.has(entry.puzzleId))throw new Error('Invalid or duplicate scheduled date.');
    dates.set(entry.date,{date:entry.date,puzzleId:entry.puzzleId});
  }
  const calendar=[...dates.values()].sort((a,b)=>a.date.localeCompare(b.date));
  const runtimeRounds=calendar.map(({date,puzzleId})=>({...bank.get(puzzleId),id:`${date}/${puzzleId}`}));
  // Creating one engine also validates the source vocabulary and each scheduled board.
  const engine=createRouteEngine(runtimeRounds,lexicon);
  const birds=new Map(lexicon.map(bird=>[bird.id,{...bird,parts:[...bird.parts]}]));
  const shortestByDate=new Map();
  const signatures=new Map(calendar.map(({date,puzzleId})=>{
    const round=bank.get(puzzleId);
    const induced=[...birds.values()].filter(bird=>bird.parts.length===2&&bird.parts.every(part=>round.parts.includes(part)))
      .sort((a,b)=>a.id.localeCompare(b.id)).map(bird=>[bird.id,bird.name,bird.parts]);
    const distance=new Map([[round.from,0]]),queue=[round.from];
    for(const id of queue){
      const current=birds.get(id);
      for(const [nextId,,parts]of induced){
        if(!distance.has(nextId)&&parts.filter((part,index)=>part!==current.parts[index]).length===1){
          distance.set(nextId,distance.get(id)+1);queue.push(nextId);
        }
      }
    }
    shortestByDate.set(date,distance.get(round.to));
    return [date,JSON.stringify([sourceVersion,puzzleId,round.from,round.to,round.parts,induced])];
  }));
  const indexByDate=new Map(calendar.map((entry,index)=>[entry.date,index]));
  let todayDate=localDateKey(now()),activeDate=null,storageUnavailable=false,saved=null;
  try{
    const raw=getStorage().getItem(storageKey);
    if(raw!==null){try{saved=JSON.parse(raw);}catch{saved=null;}}
  }catch{storageUnavailable=true;}
  const rawEntries=saved?.version===1&&saved.entries&&typeof saved.entries==='object'&&!Array.isArray(saved.entries)?saved.entries:{};
  // An older client must retain dates introduced by a newer prepared bank.
  // These values are never used as scores, routes or selectable puzzles here.
  const unknownEntries=Object.fromEntries(Object.entries(rawEntries).filter(([date])=>!dates.has(date)));
  const restored={version:1,rounds:{}};
  for(const [index,{date,puzzleId}]of calendar.entries()){
    const record=Object.hasOwn(rawEntries,date)?rawEntries[date]:null;
    if(!record||record.puzzleId!==puzzleId||record.signature!==signatures.get(date))continue;
    restored.rounds[runtimeRounds[index].id]={
      path:record.path,
      draft:Array.isArray(record.draft)&&record.draft.length===1?[]:record.draft,
      bestPath:record.bestPath,
    };
  }
  engine.restore(restored);
  let persistedStates=engine.serialize().rounds;
  let initialized=false;

  function stateFromRecord(index,record){
    const {date,puzzleId}=calendar[index];
    if(!record||record.puzzleId!==puzzleId||record.signature!==signatures.get(date))return null;
    const round=runtimeRounds[index];
    const induced=lexicon.filter(bird=>bird.parts.length===2&&bird.parts.every(part=>round.parts.includes(part)));
    const candidate={...record,draft:Array.isArray(record.draft)&&record.draft.length===1?[]:record.draft};
    const check=createRouteEngine([round],induced,{version:1,rounds:{[round.id]:candidate}});
    return check.serialize().rounds[round.id];
  }

  function persist(){
    const normalized=engine.serialize();
    let latestEntries=rawEntries;
    // A second tab may have saved another day since this session opened.
    try{
      const latest=JSON.parse(getStorage().getItem(storageKey));
      if(latest?.version===1&&latest.entries&&typeof latest.entries==='object'&&!Array.isArray(latest.entries))latestEntries=latest.entries;
    }catch{/* A failed read must not prevent a supported write. */}
    const entries={...unknownEntries,...latestEntries};
    let mergedBest=false;
    for(const [index,{date,puzzleId}]of calendar.entries()){
      const id=runtimeRounds[index].id,state=normalized.rounds[id];
      const changed=JSON.stringify(state)!==JSON.stringify(persistedStates[id]);
      if(date!==activeDate&&!changed&&Object.hasOwn(latestEntries,date))continue;
      const latestBest=stateFromRecord(index,latestEntries[date])?.bestPath;
      if(latestBest&&(!state.bestPath||latestBest.length<state.bestPath.length)){
        state.bestPath=latestBest;mergedBest=true;
      }
      entries[date]={puzzleId,signature:signatures.get(date),...state};
    }
    if(mergedBest)engine.restore(normalized);
    try{getStorage().setItem(storageKey,JSON.stringify({version:1,entries}));persistedStates=engine.serialize().rounds;storageUnavailable=false;return true;}
    catch{storageUnavailable=true;return false;}
  }
  function selectDate(date){
    // All gates precede navigation. Only the explicit playtest unlocks future dates.
    if(!validDateKey(date)||(!playtest&&date>todayDate)||!indexByDate.has(date))return false;
    const target=indexByDate.get(date);
    if(initialized&&date!==activeDate){
      const normalized=engine.serialize(),id=runtimeRounds[target].id,local=normalized.rounds[id];
      // Refresh a revisited date, but retain edits whose storage write failed.
      if(JSON.stringify(local)===JSON.stringify(persistedStates[id])){
        try{
          const saved=JSON.parse(getStorage().getItem(storageKey));
          const latest=saved?.version===1?stateFromRecord(target,saved.entries?.[date]):null;
          if(latest){
            if(local.bestPath&&(!latest.bestPath||local.bestPath.length<latest.bestPath.length))latest.bestPath=local.bestPath;
            normalized.rounds[id]=latest;engine.restore(normalized);
            persistedStates[id]=engine.serialize().rounds[id];
          }
        }catch{/* Navigation must remain available without storage. */}
      }
    }
    while(engine.view().index!==target){
      if(!engine.goToRound(target>engine.view().index?1:-1))return false;
    }
    activeDate=date;
    return true;
  }
  function selectPuzzle(id){
    const matches=calendar.filter(entry=>entry.puzzleId===id);
    return matches.length===1?selectDate(matches[0].date):false;
  }
  function openToday(){
    if(selectDate(playtest?calendar[0].date:todayDate))return true;
    activeDate=null;
    return false;
  }
  function refreshToday(){
    if(playtest)return false;
    const next=localDateKey(now()),changed=next!==todayDate;
    todayDate=next;
    return changed;
  }
  function calendarStatus(){
    if(playtest)return 'available';
    if(todayDate<calendar[0].date)return 'before-start';
    if(todayDate>calendar.at(-1).date)return 'after-end';
    return dates.has(todayDate)?'available':'unavailable';
  }
  function puzzleSummaries(){
    const normalized=engine.serialize();
    return calendar.filter(({date})=>playtest||date<=todayDate).map(({date,puzzleId})=>{
      const round=bank.get(puzzleId),state=normalized.rounds[`${date}/${puzzleId}`];
      const moves=state.path.length-1,bestMoves=state.bestPath?state.bestPath.length-1:null;
      const inProgress=state.path.at(-1)!==round.to&&(moves>0||state.draft.length>0);
      return {date,puzzleId,from:birds.get(round.from).name,to:birds.get(round.to).name,
        active:activeDate===date,moves,bestMoves,
        perfect:bestMoves!==null&&bestMoves===shortestByDate.get(date),
        status:inProgress?'in-progress':bestMoves!==null?'completed':'not-started'};
    }).reverse();
  }
  openToday();
  initialized=true;
  return {engine,persist,selectDate,selectPuzzle,openToday,refreshToday,calendarStatus,puzzleSummaries,
    get activeDate(){return activeDate;},get todayDate(){return todayDate;},
    get firstDate(){return calendar[0].date;},get lastDate(){return calendar.at(-1).date;},
    get storageUnavailable(){return storageUnavailable;}};
}
