/* Swipe2News website helpers (13 Nov 2026): language screen, breaking strip, More menu, mobile bottom nav */
(function(){
  var $ = function(id){ return document.getElementById(id); };
  var get = function(k,d){ try{ var v=localStorage.getItem('w2s.'+k); return v?JSON.parse(v):d; }catch(e){ return d; } };
  var set = function(k,v){ try{ localStorage.setItem('w2s.'+k, JSON.stringify(v)); }catch(e){} };
  var LANGS=[['te','తె','Telugu'],['hi','हि','Hindi'],['en','A','English'],['ta','த','Tamil'],['kn','ಕ','Kannada'],['ml','മ','Malayalam'],
    ['mr','म','Marathi'],['bn','বা','Bengali'],['gu','ગુ','Gujarati'],['or','ଓ','Odia'],['pa','ਪੰ','Punjabi'],['ur','ا','Urdu']];
  var READY=['te','en','hi'], NAME={te:'తెలుగు',en:'English',hi:'हिन्दी'};
  var cur=function(){ var p=get('prefs',{})||{}; return p.lang||'te'; };

  /* language screen */
  var scr=document.createElement('section'); scr.className='s2lsc'; scr.id='s2lsc'; scr.hidden=true;
  scr.setAttribute('role','dialog'); scr.setAttribute('aria-label','Choose your language');
  scr.innerHTML='<div class="in"><div class="lhd"><img src="/logo.png" alt="Swipe2News"></div><h1>Choose your language</h1>'+
    '<p class="lsub">Short news in your language. Change it anytime.</p><div class="lgrid" id="s2lgrid" role="radiogroup" aria-label="Language"></div>'+
    '<label class="lnm">మీ పేరు · Your name <small>(optional)</small><input id="s2lnm" maxlength="24" autocomplete="given-name" placeholder="Ganesh"></label>'+
    '<button class="lgo" id="s2lgo" type="button">Continue</button></div>';
  document.body.appendChild(scr);
  var pick=cur();
  function draw(){ $('s2lgrid').innerHTML=LANGS.map(function(l){ var ok=READY.indexOf(l[0])>=0, on=pick===l[0];
      return '<button class="lt'+(on?' on':'')+'" type="button" role="radio" aria-checked="'+on+'" data-l="'+l[0]+'"><span class="lg">'+l[1]+'</span><span class="ln">'+l[2]+'</span>'+(ok?'':'<span class="soon">SOON</span>')+'</button>'; }).join('');
    var c=LANGS.filter(function(l){return l[0]===pick;})[0]; $('s2lgo').textContent='Continue in '+(c?c[2]:'Telugu'); }
  $('s2lgrid').addEventListener('click',function(e){ var b=e.target.closest('.lt'); if(!b) return; var id=b.dataset.l;
    if(READY.indexOf(id)<0){ b.querySelector('.soon').textContent='త్వరలో · SOON'; return; } pick=id; draw(); });
  function open(){ pick=cur(); draw(); var n=$('s2lnm'); if(n) n.value=(get('prefs',{})||{}).name||''; scr.hidden=false; }
  $('s2lgo').onclick=function(){ var p=get('prefs',{})||{}; var chg=(p.lang||'te')!==pick; p.lang=pick; var n=$('s2lnm'); if(n){ p.name=n.value.replace(/[<>]/g,'').trim().slice(0,24); } set('prefs',p); set('langPicked',1); scr.hidden=true;
    if(chg){ location.reload(); return; } try{ window.dispatchEvent(new CustomEvent('s2prefs',{detail:p})); }catch(e){} };
  window.s2OpenLang=open;
  document.querySelectorAll('.s2lang').forEach(function(b){ var t=b.querySelector('span'); if(t) t.textContent=NAME[cur()]||'తెలుగు'; b.onclick=open; });
  try{ var q=new URLSearchParams(location.search); if(!get('langPicked',0) && !q.has('l') && !/bot|crawl|spider|Lighthouse/i.test(navigator.userAgent)) open(); }catch(e){}

  /* breaking strip: only when there is breaking news; pause control */
  var tick=document.querySelector('.tick'), row=$('tick');
  function chk(){ if(!tick||!row) return; var has=/BREAKING/.test(row.textContent||''); tick.classList.toggle('off',!has);
    if(has){ row.querySelectorAll('a').forEach(function(a){ if(!/BREAKING/.test(a.textContent)) a.remove(); }); } }
  if(tick){ tick.classList.add('off');
    var pb=document.createElement('button'); pb.type='button'; pb.className='tkpause'; pb.setAttribute('aria-label','Pause'); pb.innerHTML='❚❚';
    pb.onclick=function(){ var p=tick.classList.toggle('paused'); pb.innerHTML=p?'▶':'❚❚'; pb.setAttribute('aria-label',p?'Play':'Pause'); };
    var w=tick.querySelector('.wrap'); if(w) w.appendChild(pb);
    if(row && window.MutationObserver){ new MutationObserver(function(){ setTimeout(chk,0); }).observe(row,{childList:true}); } chk(); }

  /* More menu */
  document.addEventListener('click',function(e){ var m=e.target.closest('.s2more'); document.querySelectorAll('.s2more.open').forEach(function(x){ if(x!==m) x.classList.remove('open'); });
    if(m && e.target.closest('.s2more>button')){ e.preventDefault(); var o=m.classList.toggle('open');
      if(o){ var r=m.querySelector('button').getBoundingClientRect(), mn=m.querySelector('.menu'); mn.style.top=Math.round(r.bottom+4)+'px'; mn.style.right=Math.max(8,Math.round(innerWidth-r.right))+'px'; } } });

  /* mobile bottom navigation */
  var nav=document.createElement('nav'); nav.className='s2bnav'; nav.setAttribute('aria-label','Main');
  var isHome=location.pathname==='/'||location.pathname.indexOf('/web')===0;
  nav.innerHTML=
    '<a href="/web/" class="'+(isHome&&!/sec=|d=|q=/.test(location.search)?'on':'')+'"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 10.5L12 3l9 7.5V21h-6v-6H9v6H3z"/></svg>Home</a>'+
    '<a href="/?districts=1#dists"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>Districts</a>'+
    '<a href="/?cards=1" class="sw"><i><svg width="24" height="24" viewBox="0 0 100 100" aria-hidden="true"><g transform="rotate(8 60 46)"><rect x="42" y="18" width="34" height="56" rx="6" fill="#9C6E92"/></g><g transform="rotate(-4 44 54)"><path d="M28 24 h30 a5 5 0 0 1 5 5 v40 l-13 13 h-22 a5 5 0 0 1 -5 -5 v-48 a5 5 0 0 1 5 -5z" fill="#FFFDF5"/><path d="M63 69 L50 82 L50 69 Z" fill="#F5A23A"/></g></svg></i><span>Swipe</span></a>'+
    '<a href="/?cards=1&saved=1"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>Saved</a>';
  document.body.appendChild(nav);
  try{ if(new URLSearchParams(location.search).has('districts')){ var go=function(){ var d=$('dists'); if(d){ d.scrollIntoView({behavior:'smooth',block:'center'}); } }; setTimeout(go,1200); } }catch(e){}
})();
