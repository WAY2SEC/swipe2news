/* Swipe2News mandi prices: shared by /mandi/, the swipe-card app and the morning briefing.
   Data: /mandi.json (updated every evening by the newsroom task). Prices are ₹ per quintal. */
(function(){
const CROPS={
  paddy:{e:'🌾',te:'వరి (ధాన్యం)',en:'Paddy',hi:'धान'},
  cotton:{e:'☁️',te:'పత్తి',en:'Cotton',hi:'कपास'},
  chilli:{e:'🌶️',te:'ఎండు మిర్చి',en:'Dry chilli',hi:'सूखी मिर्च'},
  maize:{e:'🌽',te:'మొక్కజొన్న',en:'Maize',hi:'मक्का'},
  turmeric:{e:'🟡',te:'పసుపు',en:'Turmeric',hi:'हल्दी'},
  groundnut:{e:'🥜',te:'వేరుశనగ',en:'Groundnut',hi:'मूंगफली'},
  redgram:{e:'🫘',te:'కందులు',en:'Red gram (tur)',hi:'अरहर'},
  greengram:{e:'🫛',te:'పెసలు',en:'Green gram',hi:'मूंग'},
  blackgram:{e:'⚫',te:'మినుములు',en:'Black gram',hi:'उड़द'},
  soybean:{e:'🫘',te:'సోయాబీన్',en:'Soybean',hi:'सोयाबीन'},
  jowar:{e:'🌾',te:'జొన్నలు',en:'Jowar',hi:'ज्वार'},
  onion:{e:'🧅',te:'ఉల్లిపాయ',en:'Onion',hi:'प्याज'},
  tomato:{e:'🍅',te:'టమాటా',en:'Tomato',hi:'टमाटर'},
  potato:{e:'🥔',te:'బంగాళదుంప',en:'Potato',hi:'आलू'},
  greenchilli:{e:'🫑',te:'పచ్చి మిర్చి',en:'Green chilli',hi:'हरी मिर्च'},
  brinjal:{e:'🍆',te:'వంకాయ',en:'Brinjal',hi:'बैंगन'},
  coconut:{e:'🥥',te:'కొబ్బరి',en:'Coconut',hi:'नारियल'},
  banana:{e:'🍌',te:'అరటి',en:'Banana',hi:'केला'}
};
const ORDER=['paddy','cotton','chilli','maize','turmeric','groundnut','redgram','greengram','blackgram','soybean','jowar','onion','tomato','potato','greenchilli','brinjal','coconut','banana'];
const UI={
  te:{t:'మండీ ధరలు',sub:'ఈరోజు మార్కెట్ యార్డు ధరలు',q:'క్వింటాకు',kg:'కిలో',asof:'తేదీ',src:'మూలం',range:'కనిష్ఠం–గరిష్ఠం',all:'అన్నీ',
      warn:'ఇవి మార్కెట్ కమిటీలు ప్రభుత్వానికి పంపిన ధరలు. అమ్మే ముందు మీ యార్డులో ఒకసారి నిర్ధారించుకోండి.',more:'అన్ని ధరలు చూడండి →',
      near:'మీ జిల్లా',state:'రాష్ట్రం',none:'ఈ జిల్లాకు ఈరోజు ధరలు రాలేదు – రాష్ట్రంలోని ధరలు చూపిస్తున్నాం.',old:'పాత ధర',up:'పెరిగింది',down:'తగ్గింది',mkt:'మార్కెట్'},
  en:{t:'Mandi prices',sub:"Today's market-yard prices",q:'per quintal',kg:'kg',asof:'Date',src:'Source',range:'Min–Max',all:'All',
      warn:'Prices as reported by market committees to the government. Confirm at your yard before selling.',more:'See all prices →',
      near:'Your district',state:'State',none:'No prices from this district today – showing the state.',old:'older',up:'up',down:'down',mkt:'Market'},
  hi:{t:'मंडी भाव',sub:'आज के मंडी भाव',q:'प्रति क्विंटल',kg:'किलो',asof:'तारीख',src:'स्रोत',range:'न्यूनतम–अधिकतम',all:'सभी',
      warn:'ये भाव मंडी समितियों द्वारा सरकार को भेजे गए हैं। बेचने से पहले अपनी मंडी में पुष्टि करें।',more:'सभी भाव देखें →',
      near:'आपका ज़िला',state:'राज्य',none:'आज इस ज़िले से भाव नहीं आए – राज्य के भाव दिखा रहे हैं।',old:'पुराना',up:'बढ़ा',down:'घटा',mkt:'मंडी'}
};
const TG=[['hyderabad','హైదరాబాద్','Hyderabad'],['rangareddy','రంగారెడ్డి','Rangareddy'],['medchal','మేడ్చల్ మల్కాజిగిరి','Medchal–Malkajgiri'],['adilabad','ఆదిలాబాద్','Adilabad'],['bhadradri','భద్రాద్రి కొత్తగూడెం','Bhadradri Kothagudem'],['hanumakonda','హనుమకొండ','Hanumakonda'],['jagtial','జగిత్యాల','Jagtial'],['jangaon','జనగామ','Jangaon'],['bhupalpally','జయశంకర్ భూపాలపల్లి','Jayashankar Bhupalpally'],['gadwal','జోగులాంబ గద్వాల','Jogulamba Gadwal'],['kamareddy','కామారెడ్డి','Kamareddy'],['karimnagar','కరీంనగర్','Karimnagar'],['khammam','ఖమ్మం','Khammam'],['asifabad','కుమురం భీం ఆసిఫాబాద్','Kumuram Bheem Asifabad'],['mahabubabad','మహబూబాబాద్','Mahabubabad'],['mahabubnagar','మహబూబ్‌నగర్','Mahabubnagar'],['mancherial','మంచిర్యాల','Mancherial'],['medak','మెదక్','Medak'],['mulugu','ములుగు','Mulugu'],['nagarkurnool','నాగర్‌కర్నూల్','Nagarkurnool'],['nalgonda','నల్గొండ','Nalgonda'],['narayanpet','నారాయణపేట','Narayanpet'],['nirmal','నిర్మల్','Nirmal'],['nizamabad','నిజామాబాద్','Nizamabad'],['peddapalli','పెద్దపల్లి','Peddapalli'],['sircilla','రాజన్న సిరిసిల్ల','Rajanna Sircilla'],['sangareddy','సంగారెడ్డి','Sangareddy'],['siddipet','సిద్దిపేట','Siddipet'],['suryapet','సూర్యాపేట','Suryapet'],['vikarabad','వికారాబాద్','Vikarabad'],['wanaparthy','వనపర్తి','Wanaparthy'],['warangal','వరంగల్','Warangal'],['yadadri','యాదాద్రి భువనగిరి','Yadadri Bhuvanagiri']];
const MAX_AGE_DAYS=3;
function placeName(k,l){ const li=l==='te'?1:2; const t=TG.find(p=>p[0]===k)||(typeof AP_DISTRICTS!=='undefined'?AP_DISTRICTS:[]).find(p=>p[0]===k); return t?(t[li]||t[1]):k; }
function lang(){ try{ const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); return ['te','en','hi'].includes(p.lang)?p.lang:'te'; }catch(e){ return 'te'; } }
function prefs(){ try{ return JSON.parse(localStorage.getItem('w2s.prefs')||'{}')||{}; }catch(e){ return {}; } }
function istToday(){ return new Date(Date.now()+(330+new Date().getTimezoneOffset())*60000); }
function ageDays(d){ const t=istToday(); const a=Date.UTC(t.getFullYear(),t.getMonth(),t.getDate()); const [y,m,dd]=String(d).split('-').map(Number); return Math.round((a-Date.UTC(y,m-1,dd))/864e5); }
function fresh(r){ const a=ageDays(r.date); return a>=0 && a<=MAX_AGE_DAYS; }
const inr=n=>'₹'+Number(n).toLocaleString('en-IN');
function dmy(d,l){ const [y,m,dd]=String(d).split('-').map(Number); const M={te:['జన','ఫిబ్ర','మార్చి','ఏప్రి','మే','జూన్','జులై','ఆగ','సెప్టెం','అక్టో','నవం','డిసెం'],en:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],hi:['जन','फ़र','मार्च','अप्रै','मई','जून','जुला','अग','सित','अक्टू','नव','दिस']}[l||'te']; return dd+' '+M[m-1]; }
function cropName(k,l){ const c=CROPS[k]; return c?(c[l]||c.en):k; }
function stateOf(place){ return /^ap-/.test(place||'')||place==='AP'?'AP':'TG'; }
let cache=null;
async function load(){ if(cache) return cache; try{ const r=await fetch('/mandi.json?'+Math.floor(Date.now()/9e5),{cache:'no-store'}); cache=await r.json(); }catch(e){ cache={rows:[]}; } cache.rows=(cache.rows||[]).filter(fresh); return cache; }
/* best price per crop for a place: the reader's district first, then the state's highest-modal market */
function pick(data,place,limit){
  const st=stateOf(place), rows=data.rows.filter(r=>r.st===st);
  const local=rows.filter(r=>place&&r.place===place);
  const src=local.length?local:rows, out=[], seen=new Set();
  const byCrop={}; src.forEach(r=>{ (byCrop[r.crop]=byCrop[r.crop]||[]).push(r); });
  ORDER.concat(Object.keys(byCrop)).forEach(k=>{ if(seen.has(k)||!byCrop[k]) return; seen.add(k);
    const list=byCrop[k].slice().sort((a,b)=>b.date.localeCompare(a.date)||b.modal-a.modal); out.push(Object.assign({n:list.length},list[0])); });
  return {local:!!local.length, st, rows:out.slice(0,limit||99)};
}
function change(data,r){ const p=(data.prev||{})[r.st+'|'+r.place+'|'+r.mkt+'|'+r.crop]; if(!p||!r.modal) return 0; return r.modal-p; }
window.S2Mandi={TG,placeName,CROPS,ORDER,UI,load,pick,change,inr,dmy,cropName,stateOf,lang,prefs,fresh,ageDays};
})();
