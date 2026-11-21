/* Swipe2News editor – 📡 RSS tab (21 Nov 2026). No AI anywhere in this path.
   RSS candidates (tools/collect_feeds.py --candidates --post) wait here. The editor opens the source, writes the Telugu
   card, and approves ONE exact version. Only that text is published (tools/publish_approved.py). Editing an approved
   card withdraws the approval. Uses $, esc, call, toast from editor/index.html. */
(function(){
const ST={candidate:'🆕 కొత్తది',draft:'✏️ డ్రాఫ్ట్',approved:'✅ ఆమోదించారు – ప్రచురణకు సిద్ధం',published:'📢 ప్రచురించారు',rejected:'❌ వద్దన్నారు'};
const REG=[['telangana','తెలంగాణ'],['ap','ఆంధ్రప్రదేశ్'],['india','దేశం'],['world','ప్రపంచం']];
const LBL=[['fact','✅ వాస్తవం'],['claim','🟠 వాదన / ఆరోపణ'],['opinion','◻️ అభిప్రాయం'],['forecast','🔵 అంచనా']];
let RSS=[], PICS=null, OPEN=''; const SEEN=new Set();   // sources the editor opened in this session
const words=s=>String(s||'').trim().split(/\s+/).filter(Boolean).length;
const opts=(l,v)=>l.map(([k,t])=>`<option value="${esc(k)}"${k===v?' selected':''}>${esc(t)}</option>`).join('');
async function pics(){ if(PICS) return PICS; PICS=[]; try{ const md=await (await fetch('/tools/pictures.md')).text();
  md.split('\n').forEach(l=>{ const m=l.match(/^-\s+((?:c|o|i|n|s|cv|w|d)\/[a-z0-9-]+)\s*(?:[–-]\s*(.*))?$/); if(m) PICS.push([m[1],m[1]+(m[2]?' – '+m[2].slice(0,50):'')]); }); }catch(e){} return PICS; }
   // only the keys tools/check_news.py accepts (the newer e/ library isn't allowed by the checker yet)
window.__rss=()=>RSS;   // read-only peek for tests
window.loadRss=async function(){ try{ const j=await call({action:'rsslist'}); RSS=(j&&j.ok&&j.items)||[]; }catch(e){ RSS=[]; }
  const n=document.getElementById('nR'); if(n) n.textContent=RSS.filter(i=>i.status==='candidate'||i.status==='draft').length; };

window.renderRss=async function(){
  const P=await pics();
  const order={candidate:0,draft:0,approved:1,published:2,rejected:3};
  const l=RSS.slice().sort((a,b)=>(order[a.status]??9)-(order[b.status]??9));
  $('list').innerHTML=l.length?l.map(i=>{ const s=i.story||{}, ed=i.status==='candidate'||i.status==='draft', open=OPEN===i.id;
    return `<article class="card" data-rss="${esc(i.id)}"><div class="bd">
      <div class="meta"><span class="chip ${esc(i.status)}">${esc(ST[i.status]||i.status)}</span><span>📡 ${esc(i.source||s.src||'')}</span><span>🕒 ${esc(String(s.pub_src||i.time).replace('T',' ').slice(0,16))}</span>${i.link?`<a href="${esc(i.link)}" target="_blank" rel="noopener">🔗 వార్త</a>`:''}</div>
      <small style="color:var(--muted)">మూలం శీర్షిక: ${esc(s.title_src||i.headline)}</small>
      <a class="src2" href="${esc(i.url)}" target="_blank" rel="noopener nofollow" data-src="${esc(i.id)}">📰 అసలు వార్త తెరిచి సరిచూడండి →</a>
      ${s.h?`<h3>${esc(s.h)}</h3><p class="tx">${esc(s.p||'')}</p><div class="meta"><span>🖼️ ${esc(s.pic||'')}</span><span>${esc(s.stat||'')} ${esc(s.statl||'')}</span><span>${esc(s.lbl||'')}</span></div>`:''}
      ${i.hash?`<small style="color:var(--muted)">ఆమోదం: ${esc(i.by)} · ${esc(String(i.approvedat).slice(0,16).replace('T',' '))} · ${esc(String(i.hash).slice(0,19))}…</small>`:''}
      ${i.status==='approved'?`<button type="button" class="no" data-reopen="${esc(i.id)}" style="height:40px;border:0;border-radius:10px;font:800 13px var(--te)">✏️ మార్చాలి (ఆమోదం రద్దు)</button>`:''}
      ${ed&&!open?`<button type="button" class="yes" data-write="${esc(i.id)}" style="height:44px;border:0;border-radius:10px;font:800 14px var(--te)">✍️ తెలుగు కార్డు రాయండి</button>`:''}
      ${ed&&open?`<div class="pf" style="padding:0;box-shadow:none">
        <label>శీర్షిక<input type="text" id="rH" maxlength="90" value="${esc(s.h||'')}"></label>
        <label>సారాంశం<textarea id="rP" style="font:600 15px/1.6 var(--te);border:1.5px solid var(--line);border-radius:10px;padding:10px;min-height:120px">${esc(s.p||'')}</textarea><small id="rPn"></small></label>
        <label>పిక్చర్ లైన్ – సంఖ్య / అంశం<input type="text" id="rS" maxlength="20" value="${esc(s.stat||'')}"></label>
        <label>పిక్చర్ లైన్ – ఏం జరిగింది<input type="text" id="rL" maxlength="30" value="${esc(s.statl||'')}"></label>
        <label>వర్గం<select id="rR">${opts(REG,s.region||'telangana')}</select></label>
        <label>ప్రాంతం (ఐచ్ఛికం)<input type="text" id="rLoc" maxlength="40" value="${esc(s.loc||'')}"></label>
        <label>లేబుల్<select id="rB">${opts(LBL,s.lbl||'fact')}</select></label>
        <label>పిక్చర్<select id="rPic"><option value="">— ఎంచుకోండి —</option>${opts(P,s.pic||'')}</select></label>
        <label style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" id="rV" style="width:22px;height:22px"> అసలు వార్త తెరిచి, వాస్తవాలు సరిచూశాను</label>
        <label>మీ పేరు<input type="text" id="rBy" maxlength="40" value="${esc(localStorage.getItem('w2s.editorName')||'')}"></label>
        <div class="acts" style="padding:0"><button type="button" class="no" data-save="${esc(i.id)}">💾 సేవ్</button><button type="button" class="yes" data-approve="${esc(i.id)}">✅ ఈ వెర్షన్‌ను ఆమోదించు</button></div>
        <button type="button" data-reject="${esc(i.id)}" style="height:38px;border:1px solid var(--line);border-radius:10px;background:#fff;font:700 13px var(--te)">❌ ఈ వార్త వద్దు</button>
      </div>`:''}
    </div></article>`; }).join(''):'<div class="empty">RSS వార్తలు ఇంకా లేవు</div>';
  const p=$('rP'); if(p){ const c=()=>{ const n=words(p.value); $('rPn').textContent=n+' పదాలు (36–44 కావాలి)'; $('rPn').style.color=n&&(n<32||n>48)?'#B3261E':''; }; p.oninput=c; c(); }
};
function card(){ const v=i=>($(i)?$(i).value.trim():''); return {h:v('rH'),p:v('rP'),stat:v('rS'),statl:v('rL'),region:v('rR'),loc:v('rLoc'),lbl:v('rB'),pic:v('rPic')}; }
async function act(body,msg){ const j=await call(body); if(j&&j.ok){ toast(msg); OPEN=''; await loadRss(); renderRss(); } else toast('కుదరలేదు: '+((j&&j.error)||'')); return j; }
document.addEventListener('click',async e=>{
  const a=e.target.closest('a[data-src]'); if(a){ SEEN.add(a.dataset.src); return; }
  const t=e.target.closest('button[data-write],button[data-save],button[data-approve],button[data-reject],button[data-reopen]'); if(!t||F!=='rss') return;
  if(t.dataset.write){ OPEN=t.dataset.write; return renderRss(); }
  if(t.dataset.save) return act({action:'rssedit',id:t.dataset.save,story:card()},'💾 సేవ్ అయింది');
  if(t.dataset.reopen) return act({action:'rssedit',id:t.dataset.reopen,story:(RSS.find(x=>x.id===t.dataset.reopen)||{}).story},'ఆమోదం రద్దు – మళ్లీ ఎడిట్ చేయండి');
  if(t.dataset.reject) return act({action:'reviewdecide',id:t.dataset.reject,decision:'reject',note:'RSS: వద్దు'},'వద్దన్నారు');
  if(t.dataset.approve){
    const c=card(), n=words(c.p), by=$('rBy').value.trim();
    if(!SEEN.has(t.dataset.approve)||!$('rV').checked) return toast('ముందు అసలు వార్త తెరిచి సరిచూడండి');
    if(!c.h||n<32||n>48||!c.stat||!c.statl||!c.pic) return toast('శీర్షిక, 36–44 పదాల సారాంశం, పిక్చర్ లైన్, పిక్చర్ అన్నీ కావాలి');
    if(by.length<2) return toast('మీ పేరు రాయండి');
    localStorage.setItem('w2s.editorName',by);
    return act({action:'rssapprove',id:t.dataset.approve,story:c,verified:true,by},'✅ ఈ వెర్షన్ ఆమోదించారు');
  }
});
})();
