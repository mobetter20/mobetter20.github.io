// CC0 field recordings. Provenance and edit times: docs/sound-sources.md.
export const PRINT_DURATION_MS = 2320;
const files={printer:'printer',note:'note-feed',coin:'coin',button:'button'};
let context,enabled=false,generation=0,ready;
const buffers=new Map(),active=new Set();
export function stopMechanismSounds(){generation++;for(const source of active){try{source.stop();}catch{}}active.clear();}
export async function setSoundEnabled(value){
 enabled=value;stopMechanismSounds();
 if(!enabled)return;
 try{
  context ||=new(window.AudioContext||window.webkitAudioContext)();
  await context.resume();
  ready ||=Promise.all(Object.entries(files).map(async([id,file])=>{const response=await fetch(`assets/sound/${file}.mp3`);if(!response.ok)throw new Error('Sound unavailable');buffers.set(id,await context.decodeAudioData(await response.arrayBuffer()));}));
  await ready;
 }catch{ready=null;enabled=false;throw new Error('Sound could not be loaded. The machine still works without it.');}
}
function sample(id,delay=0,volume=.6){
 const buffer=buffers.get(id);if(!buffer)return;
 const source=context.createBufferSource(),gain=context.createGain();source.buffer=buffer;gain.gain.value=volume;source.connect(gain);gain.connect(context.destination);active.add(source);source.onended=()=>{active.delete(source);source.disconnect();gain.disconnect();};source.start(context.currentTime+delay);
}
export async function playMechanismSound(eventName,{coinCount=1}={}){
 if(!enabled)return;const version=generation;
 try{await ready;if(!enabled||version!==generation)return;
  if(eventName==='purchase'){sample('button',0,.45);sample('printer',.10,.65);}
  else if(eventName==='return'){sample('button',0,.40);for(let i=0;i<Math.min(coinCount,10);i++)sample('coin',.12+i*.12,.36);}
  else if(eventName==='coin')sample('coin',0,.6);
  else if(eventName==='note')sample('note',0,.50);
  else if(eventName==='button')sample('button',0,.4);
 }catch{/* Sound failure must not change a transaction. */}
}
