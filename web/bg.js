/* Swipe2News website background: faint letters floating up, in the script of the reader's own place.
   Telangana / AP → Telugu, Karnataka → Kannada, Tamil Nadu → Tamil, Kerala → Malayalam, Maharashtra → Marathi,
   Gujarat → Gujarati, Odisha → Odia, Bengal / Assam → Bengali, Punjab → Gurmukhi, other states → Hindi.
   Outside Telugu states a few Telugu letters stay mixed in (our identity). Pauses when the tab is hidden;
   stays still for readers who turn off motion. */
(function(){
  if (window.__w2sBg) return; window.__w2sBg = 1;
  var SETS = {
    te: 'అఆఇఈఉఊఎఏఐఒఓఔకఖగచజటడణతదనపబమయరలవశసహళ',
    kn: 'ಅಆಇಈಉಊಎಏಐಒಓಔಕಖಗಚಜಟಡಣತದನಪಬಮಯರಲವಶಸಹಳ',
    ta: 'அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறன',
    ml: 'അആഇഈഉഊഎഏഐഒഓഔകഖഗചജടഡണതദനപബമയരലവശസഹളഴ',
    hi: 'अआइईउऊएऐओऔकखगचजटडणतदनपबमयरलवशसह',
    mr: 'अआइईउऊएऐओऔकखगचजटडणतदनपबमयरलवशसहळ',
    gu: 'અઆઇઈઉઊએઐઓઔકખગચજટડણતદનપબમયરલવશસહળ',
    or: 'ଅଆଇଈଉଊଏଐଓଔକଖଗଚଜଟଡଣତଦନପବମଯରଲଶସହ',
    bn: 'অআইঈউঊএঐওঔকখগচজটডণতদনপবমযরলশসহ',
    pa: 'ੳਅੲਸਹਕਖਗਘਚਛਜਝਟਠਡਢਣਤਥਦਧਨਪਫਬਭਮਯਰਲਵੜ'
  };
  var BY_STATE = {TG:'te',AP:'te',KA:'kn',TN:'ta',PY:'ta',KL:'ml',MH:'mr',GA:'mr',GJ:'gu',OD:'or',WB:'bn',AS:'bn',PB:'pa'};
  function prefs(){ try{ return JSON.parse(localStorage.getItem('w2s.prefs')||'{}')||{}; }catch(e){ return {}; } }
  function stateCode(p){
    if (p.st) return p.st; var k = p.place||'';
    if (!k || k==='TS') return k ? 'TG' : '';
    if (k==='AP' || k.indexOf('ap-')===0) return 'AP';
    if (k.indexOf('st-')===0) return k.slice(3);
    var m = /^([a-z]{2})-/.exec(k); if (m) return m[1].toUpperCase();
    return 'TG';
  }
  function script(){
    var st = stateCode(prefs());
    if (st) return BY_STATE[st] || 'hi';
    var nl = (navigator.language||'').slice(0,2).toLowerCase(); // first visit, place not chosen yet
    return SETS[nl] ? nl : 'te';
  }
  var cv = document.createElement('canvas'); cv.setAttribute('aria-hidden','true');
  cv.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;display:block';
  var ctx = cv.getContext('2d'); if (!ctx) return;
  var W=0, H=0, P=[], raf=0, KEY='';
  var reduce = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : {matches:false};
  function dark(){ var t=document.documentElement.getAttribute('data-theme'); return t ? t==='dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches); }
  var FONT = "'Noto Sans Telugu','Nirmala UI','Noto Sans Kannada','Noto Sans Tamil','Noto Sans Malayalam','Noto Sans Devanagari','Noto Sans Gujarati','Noto Sans Oriya','Noto Sans Bengali','Noto Sans Gurmukhi','Kohinoor Telugu',sans-serif";
  function build(){
    var dpr = Math.min(2, window.devicePixelRatio||1); W = innerWidth; H = innerHeight;
    cv.width = W*dpr; cv.height = H*dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
    KEY = script(); var main = Array.from(SETS[KEY]), te = Array.from(SETS.te);
    var n = Math.max(14, Math.min(70, Math.round(W*H/24000))); P = [];
    for (var i=0;i<n;i++){
      var useTe = KEY!=='te' && Math.random()<.25, set = useTe ? te : main;
      P.push({x:Math.random()*W, y:Math.random()*H, s:16+Math.random()*34, v:.12+Math.random()*.28,
              c:set[Math.random()*set.length|0], a:Math.random()*6.28, r:(Math.random()-.5)*.4});
    }
  }
  function draw(move){
    ctx.clearRect(0,0,W,H); var dk = dark();
    ctx.textAlign='center'; ctx.textBaseline='middle';
    for (var i=0;i<P.length;i++){ var p=P[i];
      if (move){ p.y-=p.v; p.a+=.003; if (p.y<-60){ p.y=H+60; p.x=Math.random()*W; } }
      ctx.save(); ctx.translate(p.x+Math.sin(p.a)*12, p.y); ctx.rotate(p.r);
      ctx.font = '800 '+p.s+'px '+FONT;
      ctx.fillStyle = dk ? 'rgba(255,213,74,'+(.07+p.s/600)+')' : 'rgba(18,40,74,'+(.06+p.s/700)+')';
      ctx.fillText(p.c,0,0); ctx.restore();
    }
  }
  function loop(){ draw(true); if (!document.hidden && !reduce.matches) raf = requestAnimationFrame(loop); }
  function start(){ cancelAnimationFrame(raf); if (reduce.matches) draw(false); else raf = requestAnimationFrame(loop); }
  function boot(){ document.body.appendChild(cv); build(); start(); }
  if (document.body) boot(); else document.addEventListener('DOMContentLoaded', boot);
  var rt; addEventListener('resize', function(){ clearTimeout(rt); rt=setTimeout(function(){ build(); start(); },200); });
  document.addEventListener('visibilitychange', function(){ if (!document.hidden){ if (script()!==KEY) build(); start(); } });
  addEventListener('storage', function(e){ if (e.key==='w2s.prefs'){ build(); start(); } }); // place changed in another tab
  window.w2sBgRefresh = function(){ build(); start(); }; // place changed on this page
})();
