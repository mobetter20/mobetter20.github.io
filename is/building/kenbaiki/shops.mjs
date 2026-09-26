const shoyuMenu=[
 {id:'shoyu',name:'醤油らーめん',price:850,band:'おすすめ',bandWord:'recommended',kind:'bowl',size:'large'},
 {id:'shio',name:'塩らーめん',price:850,band:'鶏だし',bandWord:'chicken-stock',kind:'bowl',size:'large'},
 {id:'egg-shoyu',name:'味玉醤油',price:1000,band:'味玉入り',bandWord:'egg-included',kind:'bowl'},
 {id:'egg-shio',name:'味玉塩',price:1000,band:'味玉入り',bandWord:'egg-included',kind:'bowl'},
 {id:'special-shoyu',name:'特製醤油',price:1150,band:'特製',bandWord:'special',kind:'bowl'},
 {id:'special-shio',name:'特製塩',price:1150,band:'特製',bandWord:'special',kind:'bowl'},
 {id:'egg',name:'味玉',price:150,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'nori',name:'のり',price:100,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'menma',name:'メンマ',price:150,band:'トッピング',bandWord:'topping',kind:'extra',soldOut:true},
 {id:'large',name:'大盛',price:150,band:'麺増量',bandWord:'more-noodles',kind:'extra'},
 {id:'rice',name:'ライス',price:150,band:'ごはん',bandWord:'rice-heading',kind:'side'},
 {id:'small-rice',name:'小ライス',price:100,band:'ごはん',bandWord:'rice-heading',kind:'side'}
];
const hakataMenu=[
 {id:'tonkotsu',name:'豚骨ラーメン',price:900,band:'定番',bandWord:'standard',kind:'bowl',size:'large'},
 {id:'chashu-bowl',name:'チャーシュー麺',price:1150,band:'肉増し',bandWord:'more-pork',kind:'bowl',size:'large'},
 {id:'hakata-egg',name:'味玉豚骨',price:1050,band:'味玉入り',bandWord:'egg-included',kind:'bowl'},
 {id:'hakata-negi',name:'ねぎ豚骨',price:1050,band:'ねぎ増し',bandWord:'more-negi',kind:'bowl'},
 {id:'black',name:'黒ラーメン',price:1000,band:'黒マー油',bandWord:'mayu',kind:'bowl'},
 {id:'red',name:'赤ラーメン',price:1000,band:'辛味',bandWord:'spicy',kind:'bowl'},
 {id:'kaedama',name:'替玉',price:150,band:'麺のおかわり',bandWord:'noodle-refill',kind:'refill',size:'wide'},
 {id:'half-kaedama',name:'半替玉',price:100,band:'麺のおかわり',bandWord:'noodle-refill',kind:'refill',size:'wide'},
 {id:'kikurage',name:'きくらげ',price:100,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'negi',name:'ねぎ',price:150,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'egg',name:'味玉',price:150,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'chashu',name:'チャーシュー',price:250,band:'トッピング',bandWord:'topping',kind:'extra'},
 {id:'mentai-rice',name:'明太ごはん',price:350,band:'ごはん',bandWord:'rice-heading',kind:'side'},
 {id:'white-rice',name:'白ごはん',price:150,band:'ごはん',bandWord:'rice-heading',kind:'side'},
 {id:'gyoza',name:'餃子',price:350,band:'一口餃子',bandWord:'bite-gyoza',kind:'side',soldOut:true},
 {id:'beer',name:'瓶ビール',price:500,band:'お飲み物',bandWord:'drinks',kind:'side'}
];
export const shops={
 shoyu:{id:'shoyu',label:'Shoyu / shio ramen shop',jp:'中華そば',word:'shoyu-shop',menu:shoyuMenu,firmness:false,notice:'notice',extraNotice:null,blankKeys:2},
 hakata:{id:'hakata',label:'Hakata tonkotsu ramen shop',jp:'博多とんこつ',word:'hakata-shop',menu:hakataMenu,firmness:true,notice:'firmness-notice',extraNotice:'refill-notice',blankKeys:0}
};
export function getShop(id){const shop=shops[id];if(!shop)throw new Error('Unknown shop');return shop;}
export const firmnessOptions=[{id:'soft',jp:'やわめ',reading:'yawame',meaning:'Soft'},{id:'regular',jp:'ふつう',reading:'futsū',meaning:'Regular'},{id:'firm',jp:'かため',reading:'katame',meaning:'Firm'},{id:'extra-firm',jp:'バリカタ',reading:'barikata',meaning:'Extra firm'}];
