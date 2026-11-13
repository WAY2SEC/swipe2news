/* Swipe2News website: shared script for article pages (built into web/site.js by tools/build_previews.py) */
(function(){
const ART = {
  voters:'<path d="M20 120H160"/><rect x="30" y="120" width="120" height="70" rx="6"/><path d="M70 120h40"/><g transform="rotate(-8 90 80)"><rect x="72" y="40" width="36" height="70" rx="4"/><path d="M80 75l7 9 14-18"/></g>',
  deadline:'<rect x="40" y="40" width="120" height="140" rx="10"/><path d="M40 72H160M70 26v26M130 26v26"/><circle cx="125" cy="130" r="16"/><path d="M60 100h10M90 100h10M60 130h10M90 130h10M60 158h10M90 158h10"/>',
  land:'<path d="M10 190L60 125H180L165 190Z"/><path d="M35 158H172M100 125L92 190"/><path d="M110 105c-16-20-24-32-24-44a24 24 0 0 1 48 0c0 12-8 24-24 44z"/><circle cx="110" cy="61" r="8"/>',
  economy:'<path d="M20 190v-45h22v45M52 190v-75h26v75M88 190v-105h30v105M128 190v-60h22v60M160 190v-85h26v85"/><path d="M20 80l35-20 30 10 40-35 45-20"/><path d="M152 12l18 3-5 17"/>',
  water:'<path d="M100 20C100 20 60 75 60 105a40 40 0 0 0 80 0C140 75 100 20 100 20Z"/><path d="M0 170q20-12 40 0t40 0 40 0 40 0 40 0"/><path d="M0 190q20-12 40 0t40 0 40 0 40 0 40 0"/>',
  rain:'<path d="M50 90a28 28 0 0 1 54-10a24 24 0 0 1 16 46H56a22 22 0 0 1-6-36z"/><path d="M62 145l-8 18M90 145l-8 18M118 145l-8 18M76 172l-6 14M104 172l-6 14"/>',
  power:'<path d="M100 10L78 190M100 10L122 190M60 45H140M68 80H132M84 160H116M88 120H112M80 45L122 80M120 45L78 80"/><path d="M60 45q-40 25-60 15M140 45q20 15 40 15"/>',
  court:'<path d="M30 70L100 30L170 70Z"/><path d="M30 70H170M45 80v80M75 80v80M125 80v80M155 80v80M25 170H175M20 188H180"/>',
  farm:'<path d="M10 180H190"/><path d="M40 180l15-20 10 12 15-18M120 180l12-16 14 10"/><path d="M100 180V120"/><path d="M100 140c-20 0-30-12-32-28 18 0 30 10 32 28zM100 128c18 0 28-12 30-28-18 0-28 10-30 28z"/>',
  campus:'<path d="M100 40L180 75L100 110L20 75Z"/><path d="M55 92v40c25 20 65 20 90 0V92"/><path d="M175 77v50"/><circle cx="175" cy="132" r="5"/>',
  unity:'<circle cx="100" cy="100" r="62"/><circle cx="100" cy="100" r="10"/><path d="M100 38v124M38 100h124M56 56l88 88M144 56l-88 88"/>',
  job:'<rect x="28" y="66" width="144" height="104" rx="12"/><path d="M74 66V50a10 10 0 0 1 10-10h32a10 10 0 0 1 10 10v16M28 112h144"/><rect x="88" y="102" width="24" height="20" rx="4"/>'
};
const $=id=>document.getElementById(id);
const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const sid=s=>{if(s._sid)return s._sid;let h=5381;const t=(s.url||'')+'|'+(s.h||'');for(let i=0;i<t.length;i++)h=((h<<5)+h+t.charCodeAt(i))|0;return (h>>>0).toString(36)};
const tsOf=s=>{const m=/^(\d\d)\.(\d\d)\.(\d{4})$/.exec(s.d||''),t=/^(\d\d):(\d\d)$/.exec(s.t||'');return m?Date.parse(`${m[3]}-${m[2]}-${m[1]}T${t?t[1]:'12'}:${t?t[2]:'00'}:00+05:30`):0};
const store={get(k,d){try{const v=localStorage.getItem('w2s.'+k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem('w2s.'+k,JSON.stringify(v))}catch(e){}}};
const te=v=>/[ఀ-౿]/.test(v||'');
const here=location.pathname.replace(/\.html$/,'').split('/').pop();

(()=>{const W=['ఆదివారం','సోమవారం','మంగళవారం','బుధవారం','గురువారం','శుక్రవారం','శనివారం'],M=['జనవరి','ఫిబ్రవరి','మార్చి','ఏప్రిల్','మే','జూన్','జులై','ఆగస్టు','సెప్టెంబర్','అక్టోబర్','నవంబర్','డిసెంబర్'];
 const d=new Date(Date.now()+(330+new Date().getTimezoneOffset())*60000); const el=$('today'); if(el) el.textContent=`📅 ${W[d.getDay()]}, ${d.getDate()} ${M[d.getMonth()]} ${d.getFullYear()}`;})();
/* chosen place in the top strip (change it on the home page) */
(()=>{ const p=store.get('prefs',{})||{}, el=document.getElementById('myPlaceTx'), b=document.getElementById('myPlace'); if(!b) return;
  if(el && (p.place||p.village)){ const k=p.place||'TS'; const n=k==='TS'?'తెలంగాణ':k==='AP'?'ఆంధ్రప్రదేశ్':(typeof placeLabel==='function'&&placeLabel(k))||''; el.textContent=(p.village?p.village+', ':'')+(n||'తెలంగాణ'); }
  b.onclick=()=>{ location.href='/?pick=1'; }; })();
/* theme */
function applyTheme(t){const r=document.documentElement; if(!t||t==='auto') r.removeAttribute('data-theme'); else r.setAttribute('data-theme',t);}
applyTheme((store.get('prefs',{})||{}).theme);
const tb=$('theme'); if(tb) tb.onclick=()=>{const r=document.documentElement,cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'),nx=cur==='dark'?'light':'dark';applyTheme(nx);const p=store.get('prefs',{})||{};p.theme=nx;store.set('prefs',p);};

/* article in the reader's language (English / Hindi when the story has it) */
const LANG=w2sLang(); w2sLangSwitch();
document.querySelectorAll('nav.secs').forEach(w2sNavFit); if(document.fonts) document.fonts.ready.then(()=>document.querySelectorAll('nav.secs').forEach(w2sNavFit));
(()=>{ const el=$('w2sTr'); if(!el||LANG==='te') return; let T; try{ T=JSON.parse(el.textContent)[LANG]; }catch(e){} if(!T||!T.h) return;
  const ar=document.querySelector('.ar'); if(!ar) return; const ui=W2S_UI[LANG];
  document.documentElement.lang=LANG; ar.setAttribute('lang',LANG);
  const h1=ar.querySelector('h1'); if(h1) h1.textContent=T.h; document.title=T.h+' | Swipe2News';
  const ld=ar.querySelector('.alead'); if(ld&&T.p) ld.textContent=T.p;
  const ul=ar.querySelector('.pts'); if(ul&&Array.isArray(T.pts)) ul.innerHTML=T.pts.map(x=>`<li>${esc(x)}</li>`).join('');
  const cr=ar.querySelector('.corr span'); if(cr&&T.corr) cr.textContent=T.corr;
  const cb=ar.querySelector('.corr b'); if(cb&&T.corrl) cb.textContent=T.corrl;
  const wy=ar.querySelector('.why'); if(wy&&T.why) wy.innerHTML=`<small>${esc(ui.why)}</small>${esc(T.why)}`;
  const sl=ar.querySelector('.statl'); if(sl&&T.statl) sl.textContent=T.statl;
  const st=ar.querySelector('.stat'); if(st&&T.stat){ st.textContent=T.stat; st.classList.toggle('te',/[\u0C00-\u0C7F\u0900-\u097F]/.test(T.stat)); }
  const cp=ar.querySelector('.pnl .chips .chip:not(.brk)'); if(cp&&T.cat) cp.textContent=T.cat;
  ar.querySelectorAll('table.jd tr[data-k]').forEach(r=>{ const k=r.dataset.k, th=r.querySelector('th'), td=r.querySelector('td');
    if(th&&ui.rows[k]) th.textContent=ui.rows[k]; if(td&&T[k]) td.textContent=T[k]; });
  const wj=ar.querySelector('.warnj'); if(wj) wj.textContent=ui.warn;
  if(ar.querySelector('table.jd')){ const sa=ar.querySelector('.src a'); if(sa) sa.textContent=ui.off; }
  const ch=ar.querySelector('.chips .chip:not(.brk)'); if(ch&&T.cat) ch.textContent=T.cat;
  const rd=ar.querySelector('.src a'); if(rd&&!ar.querySelector('table.jd')) rd.textContent=ui.read;
  const wa=ar.querySelector('.cta.wa'); if(wa){ wa.textContent=ui.wa; wa.href='https://wa.me/?text='+encodeURIComponent(T.h+'\n'+location.origin+location.pathname+'?l='+LANG); }
  if($('listen')) $('listen').textContent=ui.listen;
})();
/* story drawing in the article header */
document.querySelectorAll('svg[data-art]').forEach(s=>{ s.innerHTML=ART[s.dataset.art]||ART.unity; });

/* listen in Telugu */
const lb=$('listen'); if(lb) lb.onclick=()=>{ const sy=window.speechSynthesis; if(!sy) return; if(sy.speaking){ sy.cancel(); return; }
  const t=[...document.querySelectorAll('.ar h1,.ar .alead,.ar .pts li,.ar .why')].map(n=>n.textContent).join('. ');
  const u=new SpeechSynthesisUtterance(t); const sl=W2S_UI[LANG].speech; u.lang=sl; u.rate=.95; const v=sy.getVoices().find(v=>v.lang.replace('_','-').toLowerCase().startsWith(sl.slice(0,2))); if(v) u.voice=v; sy.speak(u); };

function card(s){ const col=s.col||'--c-gov';
  return `<a class="card" href="/s/${sid(s)}" style="--hl:var(${col});--hlink:var(${col})"><div class="pnl">${sceneSVG(s,'scene')}${s.brk?'<span class="chip brk">🔴 BREAKING</span>':`<span class="chip">${esc(s.cat||'వార్త')}</span>`}<div class="stat${te(s.stat)?' te':''}">${esc(s.stat||'')}</div></div><div class="bd"><h3>${esc(s.h)}</h3><div class="m">${esc(s.src||'')} · ${esc(s.d||'')}${s.t?' · '+esc(s.t):''}</div></div></a>`; }
function daysLeft(j){const m=/^(\d\d)\.(\d\d)\.(\d{4})$/.exec(j.last||'');if(!m)return null;return Math.floor((new Date(+m[3],+m[2]-1,+m[1],23,59,59)-Date.now())/864e5)}
async function getJSON(u){ try{ const r=await fetch(u+'?t='+Date.now(),{cache:'no-store'}); return r.ok?await r.json():null; }catch(e){ return null; } }

(async()=>{
  const [news,jobs]=await Promise.all([getJSON('/news.json'),getJSON('/jobs.json')]);
  const all=((news&&news.stories)||[]).filter(s=>!s.wd).map(s=>w2sTr(s,sid)).sort((a,b)=>tsOf(b)-tsOf(a)).filter(s=>sid(s)!==here);
  const tk=$('tick'); if(tk) tk.innerHTML=(t=>t+t)(all.slice(0,10).map(s=>`<a href="/s/${sid(s)}"><b>${s.brk?'🔴 BREAKING':esc(s.t||'')}</b>${esc(s.h)}</a>`).join(''));
  const lt=$('latest'); if(lt) lt.innerHTML=all.slice(0,6).map(s=>`<a class="it" href="/s/${sid(s)}"><span class="tm">${esc(s.t||'')}</span><span class="hd">${esc(s.h)}</span></a>`).join('');
  const mo=$('more'); if(mo){ const rel=new Set([...document.querySelectorAll('.sec .card')].map(a=>a.getAttribute('href').split('/').pop()));
    mo.innerHTML=all.filter(s=>!rel.has(sid(s))).slice(6,14).map(card).join(''); }
  const J=((jobs&&jobs.jobs)||[]).map(j=>w2sJob(j,LANG)).map(j=>[j,daysLeft(j)]).filter(x=>x[1]!==null&&x[1]>=0).sort((a,b)=>a[1]-b[1]).slice(0,5);
  if(J.length && $('railJobs')){ $('railJobs').hidden=false;
    $('railJobsList').innerHTML=J.map(([j,d])=>`<a class="rj" href="/s/${sid({url:j.url||j.apply||'',h:j._h0||j.h})}">${esc(j.h)}<small>${d===0?W2S_UI[LANG].today:W2S_UI[LANG].left(d)} · ${esc(j.org||'')}</small></a>`).join(''); }
})();
})();
