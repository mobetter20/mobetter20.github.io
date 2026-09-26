import {initialState,transition,conserved,changeCoins,hasOutstandingProperty} from './model.mjs';
import {getShop,firmnessOptions} from './shops.mjs';
import {words} from './vocabulary.mjs';
import {PRINT_DURATION_MS,setSoundEnabled,playMechanismSound,stopMechanismSounds} from './sound.mjs';
const $=s=>document.querySelector(s);
const money=n=>`¥${n.toLocaleString('en-US')}`;
let state=initialState(),cash=1000,epoch=0,sound=false,soundRequest=0,lastInspectedControl=null,inspectedAnchorId=null;
let learning={activeId:'insert-instructions',pinned:false,controlTerms:[]};
const encountered=new Set();
const messages={
 inserted:'Credit added. Lit menu buttons are available to buy.',
 printing:'Ticket printing. The price has been deducted.',
 printed:'Your ticket is in the outlet. You can buy another item or collect it.',
 returned:'Collect your unspent money from the change outlet. Your purchased tickets remain valid.',
 'tickets-collected':'Tickets collected. Hand bowl and topping tickets to the staff.',
 'change-collected':'Change collected.',
 insufficient:'Not enough credit for that button. Add money first.',
 'sold-out':'That item is sold out. Choose another button.',
 unsupported:'This note is not accepted. Check the denominations printed by the note slot.',
 busy:'A ticket is printing. Wait for it to finish.',
 'no-credit':'No credit remains. Check the ticket and change outlets.',
 'no-tickets':'There are no tickets in the outlet. Buy an item to print a ticket.',
 'no-change':'There is no change here yet. Press おつり・返却 to return your remaining credit.',
 'left-behind':'Return your remaining credit and collect the tickets and change still in the machine.',
 'empty-hand':'Collect your ticket before handing it to the staff.',
 'handed-over':'The staff has your order. You have already paid. Follow their seating instructions.',
 'extras-only':'These tickets are for extras or sides. You have not ordered a bowl of ramen.',
 'ask-firmness':'The staff asks how firm you would like the noodles.',
 'ask-refill-firmness':'Choose the firmness for this noodle refill.',
 'refill-requested':'The staff has your refill ticket. Keep your remaining broth for the extra noodles.',
 'refill-without-bowl':'This ticket buys only extra noodles. Buy a bowl of ramen first; your refill ticket stays in your hand.',
 finished:'This order is already with the staff. Start again for a new visit.',
 reset:'Insert money to enable menu buttons.'
};
function renderMenu(){
 const shop=getShop(state.shopId);
 $('#machine').dataset.shop=shop.id;
 for(const option of document.querySelectorAll('[data-choose-shop]')){const current=option.dataset.chooseShop===shop.id;option.setAttribute('aria-current',String(current));option.querySelector('.shop-choice-state').textContent=current?'Current shop':'→';}
 $('#shop-name').textContent=shop.jp;$('#shop-name').dataset.globalWord=shop.word;
 $('#handoff-notice').textContent=words[shop.notice].jp;$('#handoff-notice').dataset.word=shop.notice;
 $('#refill-notice').hidden=!shop.extraNotice;
 $('#menu').innerHTML=shop.menu.map((item,i)=>`<button class="key ${item.size||''} ${i===1?'second':''} ${item.soldOut?'sold':''} ${!item.size&&item.name.length>5?'long':''}" data-item="${item.id}" data-terms="${item.id} ${item.bandWord} yen${item.soldOut?' sold':''}"><span class="band" data-glossary="${item.bandWord}">${item.band}</span><b data-glossary="${item.id}">${item.name}</b><span class="price" data-glossary="yen">${item.price.toLocaleString()}円</span><i class="light" ${item.soldOut?'data-glossary="sold"':''}>${item.soldOut?'売切':''}</i></button>`).join('')+'<div class="key blank" aria-hidden="true"></div>'.repeat(shop.blankKeys);
 $('.shop-context').textContent=shop.firmness?'Give bowl and topping tickets to the staff. Keep refill tickets until you want more noodles. The staff asks about noodle firmness.':'Give your tickets to the staff, then follow their seating instructions.';
}
function showWord(id,{manual=false,terms=[],scroll=false}={}){
 if(!words[id])throw new Error(`Missing explanation: ${id}`);
 if(!manual&&learning.pinned)return;
 learning={activeId:id,pinned:manual,controlTerms:[...new Set(terms.length?terms:[id])]};
 encountered.add(id);const w=words[id];
 $('#word-card').innerHTML=`${manual?'<p class="word-pin">Reading this label. Stays open until your next action.</p>':''}<h2 class="word-title" lang="ja">${w.jp}</h2><p class="word-reading"><span lang="ja">${w.reading}</span> · ${w.roman}</p><p class="word-meaning">${w.meaning}</p>${w.photo?'<img class="bowl-photo" src="assets/shoyu.png" width="1254" height="1254" alt="Illustration of this shop’s shoyu ramen with pork, bamboo shoots, nori and spring onion.">':''}<p class="word-detail">${w.detail}</p>${w.extra?`<details><summary>A useful connection</summary><p>${w.extra}</p></details>`:''}${learning.controlTerms.length>1?`<div class="term-options"><span class="term-options-label">Labels on this control</span>${learning.controlTerms.map(term=>`<button data-read-term="${term}" lang="ja" aria-pressed="${term===id}">${words[term].jp}</button>`).join('')}</div>`:''}`;
 $('#word-announcement').textContent=`${w.jp}. ${w.reading}. ${w.meaning}`;
 prepareReaderNotes(manual);if(manual&&isMobileReader())$('.context').scrollTop=0;refreshReader();if(scroll)requestAnimationFrame(revealInspectedControl);
}
function inspectControl(button,target){
 const keyboard=button.matches(':focus-visible'),anchorId=button.id||null;
 if(isMobileReader()&&!state.inspect)setInspect(true);
 lastInspectedControl=button;inspectedAnchorId=anchorId;
 const terms=(button.dataset.terms||button.dataset.word||button.dataset.globalWord||button.dataset.item).split(/\s+/);
 const id=target||button.dataset.item||button.dataset.word||button.dataset.globalWord||terms[0];
 showWord(id,{manual:true,terms,scroll:true});
 // Move keyboard focus to the explanation so its secondary terms are next in Tab order.
 if(keyboard){ $('#word-card').tabIndex=-1;$('#word-card').focus({preventScroll:true}); }
}
function announce(message){$('#feedback').textContent=message;$('#cash-instruction').textContent=message;}
function render(){
 const shop=getShop(state.shopId);
 $('#balance').textContent=state.balance.toLocaleString('en-US');
 for(const button of document.querySelectorAll('[data-item]')){
  const item=shop.menu.find(x=>x.id===button.dataset.item);
  const available=!item.soldOut&&state.balance>=item.price&&!state.pending&&state.stage==='machine';
  button.classList.toggle('on',available);
  button.setAttribute('aria-label',`${item.name} ${item.price}円. ${state.inspect?'Read all labels on this button':item.soldOut?'Sold out. Press for explanation':state.pending?'Printing. Please wait':state.stage!=='machine'?'Order is with staff':available?'Available':`Insufficient credit. ${money(item.price-state.balance)} more needed`}`);
 }
 document.body.classList.toggle('reading-mode',state.inspect);
 $('#inspect-toggle').setAttribute('aria-pressed',String(state.inspect));$('#inspect-banner').hidden=!state.inspect;$('#resume-buying').hidden=!state.inspect;
 const promptId=state.pending?'printing':state.balance?'choose-button':'insert-instructions';
 $('#machine-prompt').dataset.word=promptId;$('#machine-prompt').dataset.terms=state.pending?'printing wait':promptId;
 $('#machine-prompt').innerHTML=state.pending?'<span data-glossary="printing">発券中</span>　<span data-glossary="wait">しばらくお待ちください</span>':words[promptId].jp;
 $('#tickets').classList.toggle('printing',Boolean(state.pending));$('#tickets').classList.toggle('has-content',Boolean(state.outlet.length));
 const t=state.outlet[0];
 $('#ticket-slot').innerHTML=t?`<span class="paper-ticket"><strong data-glossary="${t.id}">${t.name}</strong><span data-glossary="yen">${t.price}円</span>　<span data-glossary="ticket">食券</span></span>`:'';
 $('#ticket-count').innerHTML=t?`<span data-glossary="sheet-counter">${state.outlet.length}枚</span>　<span data-glossary="take">お取りください</span>`:'取り忘れにご注意ください';
 $('#ticket-count').dataset.glossary=t?'take':'forget-warning';
 $('#tickets').dataset.terms=t?`ticket outlet ${t.id} yen sheet-counter take`:'ticket outlet forget-warning';
 $('#tickets').setAttribute('aria-label',state.inspect?'Read ticket outlet labels':t?`Collect ${state.outlet.length} meal tickets`:'食券 取出口. Ticket outlet empty');
 $('#change').classList.toggle('has-content',Boolean(state.changeTray));
 $('#change-slot').innerHTML=changeCoins(state.changeTray).map(({denomination,count})=>`<span class="coin-group" aria-hidden="true"><span class="currency-coin yen-${denomination}">${denomination}</span>${count>1?`<small>×${count}</small>`:''}</span>`).join('');
 $('#change-count').innerHTML=state.changeTray?`<span data-glossary="yen">${state.changeTray.toLocaleString()}円</span>　<span data-glossary="take">お取りください</span>`:'硬貨';
 $('#change-count').dataset.glossary=state.changeTray?'take':'coin';
 $('#change').dataset.terms=state.changeTray?'change outlet yen take':'change outlet coin';
 $('#change').setAttribute('aria-label',state.inspect?'Read change outlet labels':state.changeTray?`Collect ${state.changeTray} yen change`:'おつり 取出口. Change outlet empty');
 $('#held-count').textContent=state.held.length?`${state.held.length} ticket${state.held.length===1?'':'s'}`:'no tickets';
 $('#held-tickets').innerHTML=state.held.map(t=>`<div class="held-ticket"><div><button id="held-${t.number}-item" data-global-word="${t.id}" lang="ja">${t.name}</button><span><button id="held-${t.number}-ticket" data-global-word="ticket" lang="ja">食券</button>　No. ${String(t.number).padStart(3,'0')}</span>${t.kind==='refill'?'<span class="refill-tag">Keep for your noodle refill</span>':''}</div><div>${money(t.price)}</div></div>`).join('');
 $('#returned-money').textContent=state.collectedChange?`${money(state.collectedChange)} change collected`:'';
 $('#handoff').disabled=!state.held.length||state.stage!=='machine';
 const choosing=['firmness','refill-firmness'].includes(state.stage);
 $('#firmness-panel').hidden=!choosing;
 if(choosing){
  const number=state.pendingRefill??state.firmnessQueue[0],ticket=state.purchases.find(t=>t.number===number);
  $('#firmness-context').textContent=`${ticket.name} · Ticket ${String(number).padStart(3,'0')}. ${state.pendingRefill?'Choose the firmness for this refill.':'Choose how you want these noodles cooked.'}`;
  $('#firmness-options').className='firmness-options';
  $('#firmness-options').innerHTML=firmnessOptions.map(f=>`<button class="firmness-choice" data-firmness="${f.id}"><strong lang="ja">${f.jp}</strong><small>${f.reading} · ${f.meaning}</small></button>`).join('');
 }
 $('#completion').hidden=state.stage!=='served';
 if(state.stage==='served'){
  const bowls=state.staff.filter(t=>t.kind==='bowl');
  $('#completion-text').textContent=bowls.length?`${state.staff.map(t=>`${t.name}${state.firmness[t.number]||state.refillFirmness[t.number]?` (${firmnessOptions.find(f=>f.id===(state.firmness[t.number]||state.refillFirmness[t.number])).meaning.toLowerCase()})`:''}`).join(' + ')}. Total paid: ${money(state.purchases.reduce((v,t)=>v+t.price,0))}.${state.collectedChange?` Change collected: ${money(state.collectedChange)}.`:''}`:'Your tickets are for extras or sides only. Staff may check whether you also want a bowl of ramen.';
  $('#refill-actions').innerHTML=state.held.length?'<p class="refill-note">When you have eaten the noodles, keep some broth and give the staff one refill ticket.</p>'+state.held.map(t=>`<button class="refill-action" data-refill="${t.number}">Request ${t.name} · Ticket ${String(t.number).padStart(3,'0')} →</button>`).join(''):'';
  $('#word-recap').innerHTML=['ticket','change','please'].filter(id=>encountered.has(id)).map(id=>`<div class="recap-word"><button id="recap-${id}" data-global-word="${id}" lang="ja">${words[id].jp}</button> ${words[id].meaning}</div>`).join('');
 }
 refreshReader();const other=getShop(state.shopId==='shoyu'?'hakata':'shoyu');$('#try-other-shop').hidden=state.stage!=='served'||hasOutstandingProperty(state);$('#try-other-shop').textContent=`Try ${other.id==='hakata'?'the Hakata shop':'the shoyu / shio shop'} →`;
 $('#selected-cash').textContent=`${money(cash)} ${cash>=1000?'note':'coin'} selected → ${cash>=1000?'紙幣':'硬貨'}`;
 for(const b of document.querySelectorAll('[data-money]'))b.setAttribute('aria-pressed',String(Number(b.dataset.money)===cash));
}
function act(action,word){
 if(state.inspect){showWord(word||'insert-instructions',{manual:true,scroll:true});return;}
 learning.pinned=false;const previous=state;
 const result=transition(state,action);state=result.state;
 if(!conserved(state))throw new Error('Cash or ticket conservation failed');
 const mapping={unsupported:'bill','sold-out':'sold',insufficient:'credit',busy:'printing',returned:'change',printed:'ticket','tickets-collected':'ticket','change-collected':'outlet','handed-over':'please','extras-only':'please','ask-firmness':'firmness','ask-refill-firmness':'firmness','refill-requested':'kaedama','refill-without-bowl':'kaedama'};
 showWord(mapping[result.reason]||word||learning.activeId);
 announce(messages[result.reason]||'Check the machine before continuing.');render();
 if(result.ok){
  if(action.type==='purchase')playMechanismSound('purchase');
  if(action.type==='insert')playMechanismSound(action.value>=1000?'note':'coin');
  if(action.type==='return')playMechanismSound('return',{coinCount:changeCoins(previous.balance).reduce((n,c)=>n+c.count,0)});
  if(['purchase','return'].includes(action.type)&&navigator.vibrate)navigator.vibrate(12);
 }
 if(result.reason==='printing'){
  const version=epoch,number=state.pending.number;
  setTimeout(()=>{if(epoch!==version)return;const r=transition(state,{type:'finish',number});if(!r.ok)return;state=r.state;announce(messages.printed);render();},PRINT_DURATION_MS);
 }
 if(result.ok&&['firmness','refill-firmness','served'].includes(state.stage))$(state.stage==='served'?'#completion':'#firmness-panel').focus();
}
function setInspect(enabled){if(enabled&&!state.inspect){lastInspectedControl=null;inspectedAnchorId=null;}state=transition(state,{type:'inspect',enabled}).state;render();announce(enabled?'Reading mode: select a label or control for its explanation. Buying is paused.':'Buying mode. Your money and tickets are unchanged.');}
function insertAt(slot){
 if((cash>=1000)!==(slot==='bill')){learning.pinned=false;showWord(slot);announce(`Use the ${cash>=1000?'wide 紙幣 banknote':'round 硬貨 coin'} slot for ${money(cash)}.`);return;}
 act({type:'insert',value:cash},slot);
}
function reset(shopId=state.shopId){
 epoch++;stopMechanismSounds();lastInspectedControl=null;inspectedAnchorId=null;state=initialState(shopId);cash=1000;encountered.clear();learning={activeId:'insert-instructions',pinned:false,controlTerms:[]};
 renderMenu();render();showWord('insert-instructions');announce(messages.reset);
 $('#bill-input').focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});
}
$('#money-options').innerHTML=[1000,500,100,50].map(n=>`<button aria-pressed="${n===cash}" data-money="${n}">${money(n)}</button>`).join('')+'<button class="other-money" id="other-money" aria-expanded="false">Other cash +</button><span id="other-denoms" class="other-denoms" hidden>'+[10,2000,5000,10000].map(n=>`<button aria-pressed="false" data-money="${n}">${money(n)}</button>`).join('')+'</span>';
$('#machine').addEventListener('click',event=>{
 if(!state.inspect)return;const button=event.target.closest('button');if(!button)return;
 event.preventDefault();event.stopImmediatePropagation();inspectControl(button,event.target.closest('[data-glossary]')?.dataset.glossary);
},true);
$('#machine').addEventListener('click',event=>{
 const button=event.target.closest('button');if(!button)return;
 if(button.dataset.item)act({type:'purchase',id:button.dataset.item},button.dataset.item);
 else if(button.dataset.word)inspectControl(button,event.target.closest('[data-glossary]')?.dataset.glossary);
});
$('#word-card').addEventListener('click',event=>{
 const button=event.target.closest('[data-read-term]');if(!button)return;
 const id=button.dataset.readTerm;showWord(id,{manual:true,terms:learning.controlTerms});
 $(`[data-read-term="${id}"]`).focus({preventScroll:true});
});
document.addEventListener('click',event=>{const b=event.target.closest('[data-global-word]');if(b)inspectControl(b);});
$('#bill-input').onclick=()=>insertAt('bill');$('#coin-input').onclick=()=>insertAt('coin');
$('#money-options').addEventListener('click',event=>{
 const b=event.target.closest('[data-money]');if(!b)return;cash=Number(b.dataset.money);render();learning.pinned=false;showWord(cash>=1000?'bill':'coin');announce(state.inspect?'Reading mode is on. Switch back to buying to insert cash.':`${money(cash)} selected. Tap the ${cash>=1000?'紙幣 banknote':'硬貨 coin'} slot.`);
});
$('#other-money').onclick=()=>{const open=$('#other-denoms').hidden;$('#other-denoms').hidden=!open;$('#other-money').setAttribute('aria-expanded',String(open));$('#other-money').textContent=open?'Less cash −':'Other cash +';};
$('#return').onclick=()=>act({type:'return'},'change');$('#tickets').onclick=()=>act({type:'tickets'},'outlet');$('#change').onclick=()=>act({type:'change'},'change');$('#handoff').onclick=()=>act({type:'handoff'},'please');
$('#firmness-options').onclick=event=>{const b=event.target.closest('[data-firmness]');if(b)act({type:state.stage==='firmness'?'firmness':'refill-firmness',number:state.firmnessQueue[0],value:b.dataset.firmness},'firmness');};
$('#refill-actions').onclick=event=>{const b=event.target.closest('[data-refill]');if(b)act({type:'begin-refill',number:Number(b.dataset.refill)},'kaedama');};
$('#inspect-toggle').onclick=()=>state.inspect?closeReader():setInspect(true);$('#inspect-done').onclick=()=>closeReader();$('#reader-close').onclick=()=>closeReader();
$('#read-controls').onclick=()=>{setInspect(true);$('#inspect-toggle').focus();$('#machine').scrollIntoView({behavior:'instant',block:'start'});};
$('#resume-buying').onclick=()=>closeReader();
$('#reset').onclick=()=>reset();$('#again').onclick=()=>reset();
$('#change-shop').onclick=()=>$('#shop-picker').showModal();
$('#shop-picker-close').onclick=()=>$('#shop-picker').close();
$('#shop-picker').addEventListener('click',event=>{
 const option=event.target.closest('[data-choose-shop]');
 if(!option){if(event.target===$('#shop-picker'))$('#shop-picker').close();return;}
 const shopId=option.dataset.chooseShop;
 if(shopId===state.shopId){$('#shop-picker').close();return;}
 if(hasOutstandingProperty(state)&&!confirm('Change restaurants and start again? Your practice money and tickets from this visit will be cleared.'))return;
 $('#shop-picker').close();reset(shopId);$('#change-shop').focus({preventScroll:true});
});
$('#sound').onclick=async()=>{
 sound=!sound;const version=++soundRequest;
 $('#sound').setAttribute('aria-pressed',String(sound));$('#sound').textContent=sound?'Sound on':'Sound off';
 try{await setSoundEnabled(sound);}catch(error){if(version!==soundRequest)return;sound=false;$('#sound').setAttribute('aria-pressed','false');$('#sound').textContent='Sound off';announce(error.message);}
};
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.inspect&&!$('#shop-picker').open){event.preventDefault();closeReader();}});
renderMenu();render();showWord('insert-instructions');
// Read-only progressive enhancement. No browser dependency or transaction access.
if(document.modelContext?.registerTool){
 const lifecycle=new AbortController();
 const tool={name:'read_ticket_machine',title:'Read the ticket machine',description:'Read this practice machine’s shop, credit, menu availability, ticket locations, change and explained Japanese phrase. Does not buy or move anything.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:false},execute(input){if(!input||typeof input!=='object'||Object.keys(input).length)throw new Error('Expected an empty object');return {shop:state.shopId,balance:state.balance,printing:Boolean(state.pending),menu:getShop(state.shopId).menu.map(x=>({name:x.name,price:x.price,soldOut:Boolean(x.soldOut),affordable:state.balance>=x.price})),ticketsInOutlet:state.outlet.length,ticketsInHand:state.held.length,changeInOutlet:state.changeTray,changeCollected:state.collectedChange,readingMode:state.inspect,phrase:words[learning.activeId],stage:state.stage};}};
 try{Promise.resolve(document.modelContext.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}
 window.addEventListener('pagehide',()=>{lifecycle.abort();stopMechanismSounds();},{once:true});
}

// Use the host site's existing analytics only on the published site.
if(location.hostname==='ajin.im'){const script=document.createElement('script');script.src='/analytics.js';script.defer=true;document.head.append(script);}

// Reuse the same explanation on mobile, keeping its machine control in view.
function isMobileReader(){return matchMedia('(max-width:760px)').matches;}
function prepareReaderNotes(manual){
 if(!isMobileReader()||!manual||$('#word-card .reader-notes'))return;
 const card=$('#word-card'),notes=document.createElement('details');
 notes.className='reader-notes';notes.innerHTML='<summary>More about this label</summary>';
 for(const node of [...card.children])if(node.matches('.bowl-photo,.word-detail,details'))notes.append(node);
 card.append(notes);notes.addEventListener('toggle',()=>requestAnimationFrame(revealInspectedControl));
}
function restoreReaderNotes(){
 const notes=$('#word-card .reader-notes');if(!notes)return;
 const card=$('#word-card'),before=card.querySelector('.term-options')||notes;
 for(const node of [...notes.children])if(node.tagName!=='SUMMARY')card.insertBefore(node,before);
 notes.remove();
}
function resolveInspectedControl(){
 if(inspectedAnchorId)lastInspectedControl=document.getElementById(inspectedAnchorId);
 if(!lastInspectedControl?.isConnected)lastInspectedControl=null;
 return lastInspectedControl;
}
function refreshReader(){
 const reading=state.inspect&&isMobileReader(),hasTarget=Boolean(resolveInspectedControl());
 if(!reading)restoreReaderNotes();else if(hasTarget)prepareReaderNotes(true);
 document.body.classList.toggle('reader-selected',reading&&hasTarget);
 $('.reader-label').textContent=reading?'READING · BUYING PAUSED':'HELP';
 for(const node of document.querySelectorAll('.inspected-control,.inspected-term'))node.classList.remove('inspected-control','inspected-term');
 if(reading&&hasTarget){
  lastInspectedControl.classList.add('inspected-control');
  const term=[...lastInspectedControl.querySelectorAll('[data-glossary]')].find(node=>node.dataset.glossary===learning.activeId);
  term?.classList.add('inspected-term');
 }
 if(!reading)document.documentElement.style.removeProperty('--reader-height');
 if(reading)requestAnimationFrame(()=>{if(state.inspect&&isMobileReader())document.documentElement.style.setProperty('--reader-height',`${$('.context').getBoundingClientRect().height+24}px`);});
}
function revealInspectedControl(){
 if(!state.inspect||!isMobileReader()||!resolveInspectedControl())return;
 const reader=$('.context'),height=reader.getBoundingClientRect().height;
 const visibleBottom=innerHeight-height-24;
 const rect=lastInspectedControl.getBoundingClientRect();
 const targetTop=Math.max(16,(visibleBottom-rect.height)/2);
 if(rect.top<16||rect.bottom>visibleBottom){
  window.scrollTo({top:Math.max(0,scrollY+rect.top-targetTop),behavior:'instant'});
 }
 document.documentElement.style.setProperty('--reader-height',`${height+24}px`);
}
function closeReader(){
 setInspect(false);
 const control=resolveInspectedControl()||$('#inspect-toggle');
 control.focus({preventScroll:true});
 if(isMobileReader()){
  const rect=control.getBoundingClientRect(),bottom=innerHeight-$('.wallet').getBoundingClientRect().height-24;
  if(rect.top<16||rect.bottom>bottom)window.scrollTo({top:Math.max(0,scrollY+rect.top-Math.max(16,(bottom-rect.height)/2)),behavior:'instant'});
 }
}
$('#try-other-shop').onclick=()=>{if(state.stage!=='served'||hasOutstandingProperty(state))return;reset(state.shopId==='shoyu'?'hakata':'shoyu');$('#shop-name').focus({preventScroll:true});};
window.addEventListener('resize',()=>{refreshReader();requestAnimationFrame(revealInspectedControl);});
$('#word-card').addEventListener('click',event=>{if(event.target.closest('[data-read-term]'))requestAnimationFrame(revealInspectedControl);});
