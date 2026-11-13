/* Swipe2News website: shared script for article pages (built into web/site.js by tools/build_previews.py) */
(function(){
/*ART*/
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
