import {getShop,firmnessOptions} from './shops.mjs';
export const menu=getShop('shoyu').menu;
export const accepted = [10,50,100,500,1000,2000];
export const initialState = (shopId='shoyu') => ({shopId:getShop(shopId).id,firmnessQueue:[],firmness:{},pendingRefill:null,refillFirmness:{},balance:0, inserted:0, changeTray:0, collectedChange:0, purchases:[], pending:null, outlet:[], held:[], staff:[], inspect:false, nextTicket:1, stage:'machine'});
export function transition(previous, action) {
 const s=structuredClone(previous);
 const result=(ok,reason)=>({state:s,ok,reason});
 if(action.type==='reset') return {state:initialState(previous.shopId),ok:true,reason:'reset'};
 if(action.type==='inspect') {s.inspect=Boolean(action.enabled);return result(true,'inspect');}
 if(s.inspect && ['insert','purchase','return','tickets','change','handoff','firmness','begin-refill','refill-firmness'].includes(action.type))return result(false,'inspect-only');
 if(s.stage!=='machine' && !['finish','firmness','begin-refill','refill-firmness'].includes(action.type))return result(false,'finished');
 if(s.pending && ['insert','purchase','return','handoff'].includes(action.type))return result(false,'busy');
 switch(action.type){
 case 'insert':
  if(!accepted.includes(action.value))return result(false,'unsupported');
  s.balance+=action.value;s.inserted+=action.value;return result(true,'inserted');
 case 'purchase':{
  const item=getShop(s.shopId).menu.find(x=>x.id===action.id);
  if(!item)return result(false,'unknown');
  if(item.soldOut)return result(false,'sold-out');
  if(s.balance<item.price)return result(false,'insufficient');
  const ticket={number:s.nextTicket++,id:item.id,name:item.name,price:item.price,kind:item.kind};
  s.balance-=item.price;s.purchases.push(ticket);s.pending=ticket;return result(true,'printing');}
 case 'finish':
  if(!s.pending || action.number!==s.pending.number)return result(false,'stale');
  s.outlet.push(s.pending);s.pending=null;return result(true,'printed');
 case 'return':
  if(!s.balance)return result(false,'no-credit');
  s.changeTray+=s.balance;s.balance=0;return result(true,'returned');
 case 'tickets':
  if(!s.outlet.length)return result(false,'no-tickets');
  s.held.push(...s.outlet);s.outlet=[];return result(true,'tickets-collected');
 case 'change':
  if(!s.changeTray)return result(false,'no-change');
  s.collectedChange+=s.changeTray;s.changeTray=0;return result(true,'change-collected');
 case 'handoff':
  if(s.balance || s.changeTray || s.outlet.length)return result(false,'left-behind');
  if(!s.held.length)return result(false,'empty-hand');
  {
   const initial=s.held.filter(t=>t.kind!=='refill');
   const hasBowl=initial.some(t=>t.kind==='bowl')||s.staff.some(t=>t.kind==='bowl');
   if(s.held.some(t=>t.kind==='refill')&&!hasBowl)return result(false,'refill-without-bowl');
   s.staff.push(...initial);s.held=s.held.filter(t=>t.kind==='refill');
   s.firmnessQueue=getShop(s.shopId).firmness?initial.filter(t=>t.kind==='bowl').map(t=>t.number):[];
   s.stage=s.firmnessQueue.length?'firmness':'served';
   return result(true,s.firmnessQueue.length?'ask-firmness':s.staff.some(t=>t.kind==='bowl')?'handed-over':'extras-only');
  }
 case 'firmness':
  if(s.stage!=='firmness'||!firmnessOptions.some(x=>x.id===action.value)||action.number!==s.firmnessQueue[0])return result(false,'invalid-firmness');
  s.firmness[action.number]=action.value;s.firmnessQueue.shift();s.stage=s.firmnessQueue.length?'firmness':'served';return result(true,s.firmnessQueue.length?'ask-firmness':'handed-over');
 case 'begin-refill':
  if(s.stage!=='served'||!s.staff.some(t=>t.kind==='bowl')||!s.held.some(t=>t.number===action.number&&t.kind==='refill'))return result(false,'invalid-refill');
  s.pendingRefill=action.number;s.stage='refill-firmness';return result(true,'ask-refill-firmness');
 case 'refill-firmness':{
  if(s.stage!=='refill-firmness'||!firmnessOptions.some(x=>x.id===action.value))return result(false,'invalid-firmness');
  const index=s.held.findIndex(t=>t.number===s.pendingRefill&&t.kind==='refill');if(index<0)return result(false,'invalid-refill');
  s.refillFirmness[s.pendingRefill]=action.value;s.staff.push(...s.held.splice(index,1));s.pendingRefill=null;s.stage='served';return result(true,'refill-requested');}

 default:return result(false,'unknown');
 }
}
export function conserved(s){
 const money=s.inserted===s.balance+s.changeTray+s.collectedChange+s.purchases.reduce((v,t)=>v+t.price,0);
 const tickets=[...s.outlet,...s.held,...s.staff,...(s.pending?[s.pending]:[])];
 return money && s.balance>=0 && tickets.length===s.purchases.length && new Set(tickets.map(t=>t.number)).size===tickets.length;
}

export function changeCoins(amount){
 if(!Number.isSafeInteger(amount)||amount<0||amount%10)throw new Error('Change must be a nonnegative multiple of 10 yen');
 const coins=[];
 for(const denomination of [500,100,50,10]){const count=Math.floor(amount/denomination);if(count)coins.push({denomination,count});amount%=denomination;}
 return coins;
}

export function hasOutstandingProperty(s){return Boolean(s.balance||s.pending||s.outlet.length||s.changeTray||s.held.length||s.pendingRefill||s.firmnessQueue.length);}
