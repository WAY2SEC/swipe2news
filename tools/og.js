/* Swipe2News link-preview picture (1200x630) for one story or job.
   Loaded by tools/build_previews.py into index.html, so it can use ART, COLS, wrap, rrect, loadImg, teDate. */
window.ogImage = async function(s){
  const W=1200, H=630, L=460, P=44;
  const TE="'Noto Sans Telugu',sans-serif", DI="'Archivo Black',sans-serif";
  const col = COLS[s.col] || COLS['--c-gov'];
  const c=document.createElement('canvas'); c.width=W; c.height=H; const x=c.getContext('2d');
  x.fillStyle='#FFFDF5'; x.fillRect(0,0,W,H);

  // left colour panel
  x.fillStyle=col; x.fillRect(0,0,L,H);
  const hasPh=await drawStoryPhoto(x,s,0,0,L,H);
  if(!hasPh){
  try{ const a=await loadImg('data:image/svg+xml;charset=utf-8,'+encodeURIComponent(sceneSVG(s,'og'))); x.globalAlpha=.27; x.drawImage(a,-40,H-300,L+80,270); x.globalAlpha=1; }catch(e){} }
  x.fillStyle='#fff'; x.strokeStyle='#fff'; x.lineWidth=3; x.textBaseline='middle';
  x.font=`800 26px ${TE}`; let chip=s.cat||'వార్త'; if(x.measureText(chip).width>L-2*P-44){ while(x.measureText(chip+'…').width>L-2*P-44 && chip.length>4) chip=chip.slice(0,-1); chip=chip.trim()+'…'; }
  const cw=x.measureText(chip).width+44; rrect(x,P,P,cw,52,26); x.stroke(); x.fillText(chip,P+22,P+27);
  x.textBaseline='alphabetic';
  const stat=String(s.stat||''), te=/[ఀ-౿]/.test(stat);
  let ss=te?(hasPh?44:96):(hasPh?56:130); const sf=()=>{ x.font=te?`800 ${ss}px ${TE}`:`400 ${ss}px ${DI}`; }; sf();
  while(x.measureText(stat).width>L-2*P && ss>44){ ss-=6; sf(); }
  x.font=`800 ${hasPh?24:32}px ${TE}`; const sl=wrap(x,s.statl||'',L-2*P).slice(0,2);
  let y=H-P-(sl.length-1)*(hasPh?32:42); sl.forEach((t,k)=>x.fillText(t,P,y+k*(hasPh?32:42)));
  sf(); x.fillText(stat,P,y-(hasPh?38:50)-(te?Math.round(ss*0.3):0));

  // right: brand bar
  const R=L, RW=W-L;
  x.fillStyle='#2E0827'; x.fillRect(R,0,RW,92);
  let bx=R+P;
  try{ const lg=await loadImg('logo-light.png'); const lh=50, lw=lg.width*lh/lg.height; x.drawImage(lg,bx,(92-lh)/2,lw,lh); bx+=lw+30;
       x.strokeStyle='rgba(255,255,255,.25)'; x.lineWidth=2; x.beginPath(); x.moveTo(bx-15,22); x.lineTo(bx-15,70); x.stroke(); }catch(e){}
  x.font=`800 30px ${TE}`; x.fillStyle='#F5A23A'; x.textBaseline='middle'; x.fillText(s.kind==='job'?'జాబ్స్ – ఉద్యోగ సమాచారం':'ఒక్క స్వైప్‌లో వార్తలు!',bx,48); x.textBaseline='alphabetic';

  // headline (shrinks to fit 4 lines)
  let hs=50, hl; do{ x.font=`800 ${hs}px ${TE}`; hl=wrap(x,s.h||'',RW-2*P); if(hl.length<=4) break; hs-=4; }while(hs>32);
  hl=hl.slice(0,4); x.fillStyle=col; let hy=92+40+hs; hl.forEach(t=>{ x.fillText(t,R+P,hy); hy+=Math.round(hs*1.42); });

  // meta line
  const meta = s.kind==='job'
    ? [s.last&&('చివరి తేదీ: '+s.last), s.qual&&('అర్హత: '+s.qual)].filter(Boolean).join(' · ')
    : [s.d, s.t].filter(Boolean).join(' · ') + (s.src?'  ·  Source: '+s.src:'');
  x.font=`600 26px ${TE}`; x.fillStyle='#5E5246'; const ml=wrap(x,meta,RW-2*P).slice(0,2);
  let my=Math.min(hy+8, H-150); ml.forEach(t=>{ x.fillText(t,R+P,my); my+=36; });
  // first lines of the story in the free space
  const body = s.kind==='job' ? (s.sum||'') : (s.p||'');
  x.font=`400 25px ${TE}`; x.fillStyle='#2A231C';
  let by=my+14; const lim=H-P-58-22; const bl=wrap(x,body,RW-2*P);
  for(let k=0;k<bl.length && by<=lim;k++){ let t=bl[k]; if(by+38>lim && k<bl.length-1) t=t.replace(/\s*\S*$/,'')+' …'; x.fillText(t,R+P,by); by+=38; }

  // footer: site pill + call to action
  x.font=`800 26px ${TE}`; const site='swipe2news.com', pw=x.measureText(site).width+40;
  x.fillStyle='#4A0E3F'; rrect(x,R+P,H-P-58,pw,52,26); x.fill(); x.fillStyle='#fff'; x.textBaseline='middle'; x.fillText(site,R+P+20,H-P-31);
  x.fillStyle='#2E0827'; x.font=`800 26px ${TE}`; x.fillText(s.kind==='job'?'వివరాలు చూడండి →':'పూర్తి వార్త చదవండి →',R+P+pw+22,H-P-31);
  x.textBaseline='alphabetic';
  const g=x.createLinearGradient(0,0,W,0); g.addColorStop(0,'#4A0E3F'); g.addColorStop(.6,'#FF6A3D'); g.addColorStop(1,'#F5A23A');
  x.fillStyle=g; x.fillRect(0,H-8,W,8);
  return c.toDataURL('image/jpeg',0.78);
};
