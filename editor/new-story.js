/* Swipe2News editor – ✍️ New story (manual publishing fallback, 20 Nov 2026).
   The editor writes a card here; it is queued in the newsroom Sheet ("Drafts") and goes live when the
   "Publish manual stories" GitHub Actions workflow is run. No GitHub token is ever in the browser.
   Uses $, esc, call, toast from editor/index.html. */
(function(){
const REGIONS=[['telangana','తెలంగాణ'],['ap','ఆంధ్రప్రదేశ్'],['india','దేశం (భారత్)'],['world','ప్రపంచం']];
const TOPICS=[['','— ప్రత్యేక విభాగం లేదు —'],['business','బిజినెస్ / ధరలు'],['education','విద్య'],['jobs','ఉద్యోగాలు'],['agri','వ్యవసాయం'],['weather','వాతావరణం'],['culture','సంస్కృతి / పండుగలు'],['sports','క్రీడలు'],['innovation','టెక్ / ఆవిష్కరణ'],['election','ఎన్నికలు / రాజకీయం']];
const LABELS=[['fact','✅ వాస్తవం (FACT)'],['claim','🟠 వాదన / ఆరోపణ (CLAIM)'],['opinion','◻️ అభిప్రాయం (OPINION)'],['forecast','🔵 అంచనా / సూచన (FORECAST)']];
const DST={queued:'⏳ వరుసలో – workflow నడిపితే ప్రచురణ',published:'✅ ప్రచురించారు',rejected:'❌ తిరస్కరించారు',cancelled:'⏹️ రద్దు చేశారు'};
let PICS=null, DRAFTS=[];
const words=s=>String(s||'').trim().split(/\s+/).filter(Boolean).length;
const newId=()=>'d'+new Date().toISOString().replace(/\D/g,'').slice(2,14)+'-'+Math.random().toString(36).slice(2,8);
let DID=newId();

async function pics(){
  if(PICS) return PICS;
  PICS=[];
  try{
    const md=await (await fetch('/tools/pictures.md?'+Date.now())).text(); let grp='';
    md.split('\n').forEach(l=>{ const g=l.match(/^##\s+(.*)/); if(g){ grp=g[1].trim(); return; }
      const m=l.match(/^-\s+((?:c|o|i|n|s|cv|w|d)\/[a-z0-9-]+)\s*(?:[–-]\s*(.*))?$/); if(m) PICS.push({k:m[1],d:(m[2]||'').trim(),g:grp}); });
  }catch(e){}
  return PICS;
}
function opts(list,sel){ return list.map(([v,l])=>`<option value="${esc(v)}"${v===sel?' selected':''}>${esc(l)}</option>`).join(''); }
function langBox(L,name){ return `<details id="x${L}"><summary>${name} (ఐచ్ఛికం)</summary>
  <label>Headline<input type="text" id="${L}H" maxlength="90"></label>
  <label>Summary<textarea id="${L}P"></textarea><span class="cnt" id="${L}Pn"></span></label>
  <div class="two"><label>Picture line – number / topic<input type="text" id="${L}S" maxlength="30"></label><label>Picture line – what happened<input type="text" id="${L}L" maxlength="40"></label></div>
  <label>Place<input type="text" id="${L}Loc" maxlength="40"></label></details>`; }

window.renderNew=async function(){
  $('list').innerHTML=`<div class="pf" id="nsf">
    <div class="rule">✍️ <b>కొత్త వార్త రాయండి.</b> "వరుసలో పెట్టు" నొక్కితే Sheet లో సేవ్ అవుతుంది. GitHub లో <b>Publish manual stories → Run workflow</b> నొక్కినప్పుడు సైట్‌లో వస్తుంది. మీ సొంత మాటల్లో రాయండి, మూలం లింక్ తప్పనిసరి.</div>
    <label>శీర్షిక (తెలుగు)<input type="text" id="nsH" maxlength="90" placeholder="ఏ సంఘటనో పేరుతో చెప్పండి"><span class="cnt" id="nsHn"></span></label>
    <label>సారాంశం (తెలుగు)<textarea id="nsP" placeholder="సుమారు 40 పదాలు – ఎవరు, ఏమిటి, ఎక్కడ, ఎప్పుడు"></textarea><span class="cnt" id="nsPn"></span></label>
    <div class="two"><label>పిక్చర్ లైన్ – సంఖ్య / అంశం<input type="text" id="nsS" maxlength="20" placeholder="ఉదా: ₹500 కోట్లు"></label><label>పిక్చర్ లైన్ – ఏం జరిగింది<input type="text" id="nsL" maxlength="30" placeholder="ఉదా: కొత్త రోడ్లకు"></label></div>
    <div class="two"><label>వర్గం<select id="nsR">${opts(REGIONS,'telangana')}</select></label><label>విభాగం<select id="nsT">${opts(TOPICS,'')}</select></label></div>
    <div class="two"><label>ప్రాంతం (ఐచ్ఛికం)<input type="text" id="nsLoc" maxlength="40" placeholder="ఉదా: సిద్దిపేట"></label><label>లేబుల్<select id="nsB">${opts(LABELS,'fact')}</select></label></div>
    <div class="two"><label>మూలం పేరు<input type="text" id="nsSrc" maxlength="60" placeholder="ఉదా: PIB, The Hindu"></label><label>మూలం లింక్<input type="url" id="nsU" placeholder="https://…"></label></div>
    <label>పిక్చర్ (లైబ్రరీ నుంచి)<input type="search" id="nsQ" placeholder="వెతకండి: education, rain, bus…"><select id="nsPic"><option value="">— లోడ్ అవుతోంది… —</option></select></label>
    <img class="prev" id="nsPv" hidden alt="">
    <label>ముఖ్యాంశాలు (ఐచ్ఛికం – ఒక్కో లైన్‌లో ఒకటి)<textarea id="nsPts" placeholder="2–3 చిన్న పాయింట్లు"></textarea></label>
    <label>ఎందుకు ముఖ్యం (ఐచ్ఛికం)<input type="text" id="nsW" maxlength="160"></label>
    ${langBox('en','English')}${langBox('hi','हिन्दी (Hindi)')}
    <div class="err" id="nsE" hidden></div>
    <button type="button" class="go" id="nsGo">📥 వరుసలో పెట్టు</button>
    <small>ఒకే వార్తను రెండుసార్లు పంపినా ఒక్కటే సేవ్ అవుతుంది. ప్రచురించే ముందు వార్త తనిఖీ (check_news.py) జరుగుతుంది; తప్పులుంటే ఇక్కడ "తిరస్కరించారు" అని కారణంతో కనిపిస్తుంది.</small>
  </div>
  <h3 style="margin:6px 2px 0">నా డ్రాఫ్ట్‌లు</h3><div class="dl" id="nsList"><div class="empty">లోడ్ అవుతోంది…</div></div>`;
  const P=await pics();
  const fill=q=>{ q=(q||'').toLowerCase(); const cur=$('nsPic').value; const l=P.filter(x=>!q||(x.k+' '+x.d+' '+x.g).toLowerCase().includes(q));
    const by={}; l.forEach(x=>(by[x.g]=by[x.g]||[]).push(x));
    $('nsPic').innerHTML='<option value="">— పిక్చర్ ఎంచుకోండి ('+l.length+') —</option>'+Object.keys(by).map(g=>`<optgroup label="${esc(g)}">${by[g].map(x=>`<option value="${esc(x.k)}"${x.k===cur?' selected':''}>${esc(x.k)}${x.d?' – '+esc(x.d.slice(0,60)):''}</option>`).join('')}</optgroup>`).join(''); };
  fill('');
  $('nsQ').oninput=e=>fill(e.target.value);
  $('nsPic').onchange=()=>{ const k=$('nsPic').value, im=$('nsPv'); if(!k){ im.hidden=true; return; } im.onerror=()=>{ im.onerror=null; im.src='/art/'+k+'.jpg'; }; im.src='/art/'+k+'.webp'; im.hidden=false; };
  const cnt=()=>{ const h=$('nsH').value.trim(), n=words($('nsP').value);
    $('nsHn').textContent=h.length+' అక్షరాలు (≤ 38 మంచిది)'; $('nsHn').className='cnt'+(h.length>38?' bad':'');
    $('nsPn').textContent=n+' పదాలు (36–44 కావాలి)'; $('nsPn').className='cnt'+(n&&(n<32||n>48)?' bad':'');
    ['en','hi'].forEach(L=>{ const k=words($(L+'P').value); $(L+'Pn').textContent=k?k+' words':''; }); };
  ['nsH','nsP','enP','hiP'].forEach(i=>$(i).oninput=cnt); cnt();
  $('nsGo').onclick=send;
  loadDrafts();
};

function collect(){
  const v=i=>$(i).value.trim();
  const s={h:v('nsH'),p:v('nsP'),stat:v('nsS'),statl:v('nsL'),region:v('nsR'),topic:v('nsT'),loc:v('nsLoc'),lbl:v('nsB'),src:v('nsSrc'),url:v('nsU'),pic:v('nsPic'),
    pts:v('nsPts').split('\n').map(x=>x.trim()).filter(Boolean).slice(0,4),why:v('nsW')};
  ['en','hi'].forEach(L=>{ const t={h:v(L+'H'),p:v(L+'P'),stat:v(L+'S'),statl:v(L+'L'),loc:v(L+'Loc')}; if(t.h||t.p) s[L]=t; });
  const e=[];
  if(!s.h) e.push('శీర్షిక రాయండి');
  const n=words(s.p); if(!s.p) e.push('సారాంశం రాయండి'); else if(n<32||n>48) e.push('సారాంశం '+n+' పదాలు – 36–44 పదాలు ఉండాలి');
  if(!s.stat||!s.statl) e.push('పిక్చర్ లైన్ రెండు భాగాలూ నింపండి (సంఖ్య/అంశం + ఏం జరిగింది)');
  if(!s.src) e.push('మూలం పేరు రాయండి');
  if(!/^https:\/\/[^\s]+\.[^\s]+/.test(s.url)) e.push('మూలం లింక్ https:// తో ఉండాలి');
  if(!s.pic) e.push('లైబ్రరీ నుంచి ఒక పిక్చర్ ఎంచుకోండి');
  ['en','hi'].forEach(L=>{ if(s[L]&&(!s[L].h||!s[L].p)) e.push((L==='en'?'English':'Hindi')+': headline మరియు summary రెండూ రాయండి, లేదా రెండూ ఖాళీగా ఉంచండి'); });
  return [s,e];
}
async function send(){
  const [s,e]=collect(), box=$('nsE');
  if(e.length){ box.innerHTML=e.map(esc).join('<br>'); box.hidden=false; return; } box.hidden=true;
  const b=$('nsGo'); b.disabled=true; b.textContent='పంపుతోంది…';
  try{ const j=await call({action:'draft',id:DID,story:s});
    if(j.ok){ toast(j.dup?'ఈ డ్రాఫ్ట్ ఇప్పటికే వరుసలో ఉంది':'📥 వరుసలో పెట్టారు'); DID=newId(); renderNew(); return; }
    box.textContent=j.error==='not allowed'?'న్యూస్‌రూమ్‌లో ఈ ఫీచర్ ఇంకా అప్‌డేట్ కాలేదు (Apps Script).':'కుదరలేదు: '+(j.error||''); box.hidden=false; }
  catch(x){ box.textContent='ఇంటర్నెట్ సమస్య – మళ్లీ నొక్కండి (డ్రాఫ్ట్ రెండుసార్లు సేవ్ కాదు)'; box.hidden=false; }
  b.disabled=false; b.textContent='📥 వరుసలో పెట్టు';
}
async function loadDrafts(){
  try{ const j=await call({action:'draftlist'}); DRAFTS=(j&&j.ok&&j.items)||[]; }catch(e){ DRAFTS=[]; }
  const el=$('nsList'); if(!el) return;
  el.innerHTML=DRAFTS.length?DRAFTS.map(d=>{ const s=d.story||{}; return `<article class="card"><div class="bd">
    <div class="meta"><span class="chip ${esc(d.status)}">${esc(DST[d.status]||d.status)}</span><span>🕒 ${esc(d.time)}</span>${d.link?`<a href="${esc(d.link)}" target="_blank" rel="noopener">🔗 వార్త చూడండి</a>`:''}</div>
    <h3>${esc(s.h||d.headline)}</h3><p class="tx">${esc(s.p||'')}</p>
    <div class="meta"><span>🖼️ ${esc(s.pic||'')}</span><span>📰 ${esc(s.src||'')}</span></div>
    ${d.note?`<small style="color:var(--muted)">📝 ${esc(d.note)}</small>`:''}
    ${d.status==='queued'?`<button type="button" class="no" data-cancel="${esc(d.id)}" style="height:40px;border:0;border-radius:10px;background:#F3E3E1;color:#8C1D18;font:800 13px var(--te)">⏹️ రద్దు చేయి</button>`:''}
  </div></article>`; }).join(''):'<div class="empty">ఇంకా డ్రాఫ్ట్‌లు లేవు</div>';
  el.querySelectorAll('[data-cancel]').forEach(b=>b.onclick=async()=>{ b.disabled=true; try{ const j=await call({action:'draftcancel',id:b.dataset.cancel}); toast(j.ok?'రద్దు చేశారు':'కుదరలేదు: '+(j.error||'')); }catch(e){ toast('ఇంటర్నెట్ సమస్య'); } loadDrafts(); });
}
})();
