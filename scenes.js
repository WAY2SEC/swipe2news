/* Swipe2News place & topic illustrations (drawn by hand as vector art, 400x200, white silhouettes).
   Used behind the big number on every card. Layers: far (faint), mid, near. */
const SCENES = {
  hyderabad: `
    <g opacity=".35"><path d="M0 200V150h18v-22h14v22h10v-40h16v40h12v-28h20v28h8v-52h18v52h10v-18h14v18H0z"/><path d="M290 200v-58h16v-20h14v20h10v-34h18v34h12v-24h16v24h24v58z"/></g>
    <g>
      <rect x="150" y="128" width="100" height="72"/>
      <path d="M150 128h100v-8H150z"/>
      <path d="M200 74c-10 0-18 9-18 18h36c0-9-8-18-18-18zM198 60h4v14h-4z"/>
      <rect x="184" y="92" width="32" height="28"/>
      ${[148,238].map(x=>`<rect x="${x}" y="44" width="14" height="156"/><rect x="${x-3}" y="78" width="20" height="5"/><rect x="${x-3}" y="104" width="20" height="5"/><path d="M${x} 44c0-9 3-16 7-20 4 4 7 11 7 20z"/><rect x="${x+6}" y="12" width="2" height="12"/>`).join('')}
    </g>
    <path fill="#000" fill-opacity=".001" d="M0 0"/>
    <g fill="var(--hole,#000)" opacity="0"></g>`,
  hyderabadHole: `<path d="M178 200v-38c0-14 10-24 22-24s22 10 22 24v38z"/><path d="M160 200v-26c0-7 4-11 8-11s8 4 8 11v26zM224 200v-26c0-7 4-11 8-11s8 4 8 11v26z"/>`,
  warangal: `
    <g opacity=".35"><path d="M0 200c40-30 80-36 120-30s60 24 80 30H0z"/><path d="M220 200c30-24 80-38 180-26v26z"/></g>
    <g>
      <path d="M120 74c10-16 26-18 34-10l-6 10c-6-4-14-2-20 6z"/><path d="M280 74c-10-16-26-18-34-10l6 10c6-4 14-2 20 6z"/>
      <rect x="128" y="74" width="144" height="14" rx="3"/>
      <rect x="140" y="62" width="120" height="8" rx="2"/>
      <path d="M150 88h100v10H150z"/>
      <rect x="150" y="98" width="18" height="102"/><rect x="232" y="98" width="18" height="102"/>
      <rect x="144" y="188" width="30" height="12"/><rect x="226" y="188" width="30" height="12"/>
      <path d="M168 98h64c0 22-14 36-32 40-18-4-32-18-32-40z" opacity=".55"/>
      <circle cx="200" cy="81" r="4" opacity=".6"/>
    </g>`,
  temple: `
    <g opacity=".35"><path d="M0 200c30-40 70-60 110-60s70 30 90 60z"/><path d="M250 200c20-30 60-44 100-40s50 20 50 40z"/></g>
    <g>
      <path d="M150 200h100l-6-30H156z"/>
      <path d="M156 170h88l-8-26H164z"/>
      <path d="M164 144h72l-8-24H172z"/>
      <path d="M172 120h56l-8-22H180z"/>
      <path d="M180 98h40l-7-18h-26z"/>
      <path d="M187 80h26c0-9-6-14-13-14s-13 5-13 14z"/>
      <rect x="198" y="48" width="4" height="18"/><circle cx="200" cy="46" r="5"/>
      <path d="M190 200v-22c0-6 4-10 10-10s10 4 10 10v22z" opacity=".5"/>
      <rect x="60" y="176" width="10" height="24"/><path d="M52 176h26l-13-14z"/>
      <rect x="330" y="176" width="10" height="24"/><path d="M322 176h26l-13-14z"/>
    </g>`,
  fort: `
    <g opacity=".35"><path d="M0 200c50-70 120-96 200-96s150 26 200 96z"/></g>
    <g>
      <path d="M60 200v-62h10v-8h10v8h10v-8h10v8h10v-8h10v8h10v62z"/>
      <path d="M210 200v-62h10v-8h10v8h10v-8h10v8h10v-8h10v8h10v62z"/>
      <path d="M130 200v-48h80v48z"/>
      <path d="M124 152h92v-8h-8v-8h-8v8h-10v-8h-8v8h-10v-8h-8v8h-10v-8h-8v8h-8v-8h-8v8h-6z"/>
      <circle cx="96" cy="128" r="12"/><circle cx="244" cy="128" r="12"/>
      <path d="M156 200v-26c0-8 6-14 14-14s14 6 14 14v26z" opacity=".5"/>
      <path d="M300 200v-34h10v-6h8v6h8v-6h8v6h10v34z" opacity=".7"/>
    </g>`,
  mine: `
    <g opacity=".35"><path d="M0 200v-26l60-20 70 14 60-24 80 18 70-20 60 16v42z"/></g>
    <g>
      <path d="M130 200l40-130h10l40 130h-12l-33-110-33 110z"/>
      <path d="M146 150h68v6h-68zM158 112h44v6h-44z"/>
      <circle cx="175" cy="64" r="18" fill="none" stroke="#fff" stroke-width="6"/><circle cx="175" cy="64" r="4"/>
      <path d="M175 64l70 136h-8l-66-128z" opacity=".7"/>
      <rect x="250" y="150" width="90" height="50"/><rect x="262" y="120" width="12" height="30"/><rect x="290" y="128" width="10" height="22"/>
      <path d="M40 200v-20h60v20z"/><circle cx="54" cy="200" r="6"/><circle cx="86" cy="200" r="6"/>
    </g>`,
  forest: `
    <g opacity=".35"><path d="M0 200c40-50 90-70 140-70s80 30 110 30 90-40 150-30v70z"/></g>
    <g>
      ${[[40,1],[90,.8],[140,1.15],[200,.9],[250,1.25],[310,.85],[360,1.05]].map(([x,s])=>`<path d="M${x} ${200-120*s}l${22*s} ${40*s}h-${10*s}l${20*s} ${34*s}h-${12*s}l${22*s} ${38*s}h-${104*s}l${22*s}-${38*s}h-${12*s}l${20*s}-${34*s}h-${10*s}z" transform="translate(${-0*s} 0)"/><rect x="${x-3}" y="${200-8*s}" width="6" height="${8*s}"/>`).join('')}
    </g>`,
  river: `
    <g opacity=".35"><path d="M0 120c60-20 120-24 200-10s140 10 200-6v96H0z"/></g>
    <g>
      <path d="M0 148h400v10H0z"/>
      ${[0,1,2,3,4].map(i=>`<path d="M${20+i*76} 200v-30c0-18 14-30 30-30s30 12 30 30v30h-10v-28c0-12-9-20-20-20s-20 8-20 20v28z"/>`).join('')}
      <path d="M0 178q25-10 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v6q-25-10-50 0t-50 0-50 0-50 0-50 0-50 0-50 0-50 0z" opacity=".6"/>
      <path d="M0 192q25-10 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v8H0z" opacity=".45"/>
    </g>`,
  village: `
    <g opacity=".35"><path d="M0 170c80-20 160-24 240-14s120 10 160 4v40H0z"/></g>
    <g>
      <path d="M70 200v-36h52v36z"/><path d="M62 166l34-30 34 30z"/>
      <path d="M150 200v-28h40v28z"/><path d="M144 174l26-24 26 24z"/>
      <path d="M86 200v-16h14v16z" opacity=".5"/>
      ${[[250,1],[300,.8],[30,.75]].map(([x,s])=>`<path d="M${x} 200c-2-40 0-80 6-${110*s}" stroke="#fff" stroke-width="${5*s}" fill="none"/><path d="M${x+6} ${200-110*s}c-20 0-34 10-40 22 14-8 28-12 40-10-18 4-30 14-34 26 12-12 24-18 34-18 0 12-6 24-14 32 12-8 18-20 20-30 6 10 18 18 32 22-8-8-14-18-16-28 12 2 26 8 34 18-4-12-16-22-32-26 10-2 24 0 36 8-6-12-22-18-40-18z"/>`).join('')}
      <path d="M200 200l40-24 40 24M240 200v-24" stroke="#fff" stroke-width="3" fill="none" opacity=".6"/>
      <path d="M330 200h70v-6h-70zM320 188h80v-4h-80zM340 178h60v-3h-60z" opacity=".55"/>
    </g>`,
  city: `
    <g opacity=".35"><path d="M0 200v-60h24v-20h20v80zM50 200v-90h26v90zM300 200v-70h20v-24h22v94zM350 200v-50h50v50z"/></g>
    <g>
      <path d="M86 200V96h34v104z"/><path d="M126 200V64l20-14 20 14v136z"/><rect x="172" y="110" width="30" height="90"/>
      <path d="M208 200V80h40v120z"/><path d="M254 200v-88l18-18 18 18v88z"/>
      <rect x="226" y="58" width="4" height="22"/><rect x="144" y="28" width="4" height="22"/>
      ${[100,112].map(y=>`<rect x="92" y="${y}" width="22" height="4" opacity=".5"/>`).join('')}
      ${[90,104,118,132,146,160].map(y=>`<rect x="214" y="${y}" width="28" height="4" opacity=".5"/>`).join('')}
    </g>`,
  india: `
    <g opacity=".35"><path d="M0 200c60-24 140-30 200-24s140 10 200-4v28z"/></g>
    <g>
      <path d="M140 200V96h120v104h-30v-56c0-16-14-28-30-28s-30 12-30 28v56z"/>
      <rect x="132" y="84" width="136" height="12"/><rect x="146" y="72" width="108" height="12"/>
      <rect x="176" y="58" width="48" height="14"/><path d="M186 58c0-8 6-14 14-14s14 6 14 14z"/>
      <rect x="50" y="168" width="60" height="32" opacity=".7"/><rect x="290" y="168" width="60" height="32" opacity=".7"/>
    </g>`,
  world: `
    <g>
      <circle cx="200" cy="200" r="150" fill="none" stroke="#fff" stroke-width="6"/>
      <ellipse cx="200" cy="200" rx="60" ry="150" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>
      <ellipse cx="200" cy="200" rx="110" ry="150" fill="none" stroke="#fff" stroke-width="3" opacity=".5"/>
      <path d="M50 160h300M66 110h268M100 70h200" stroke="#fff" stroke-width="3" fill="none" opacity=".6"/>
      <path d="M120 120c20-10 40 0 50 14s30 10 40 0 30-4 34 10-10 26-30 26-34 14-54 10-44-30-40-60z" opacity=".55"/>
      <path d="M250 90c16-8 40-4 52 10s4 24-12 24-30-8-40-18z" opacity=".55"/>
    </g>`,
  tech: `
    <g opacity=".5" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round">
      <path d="M0 160h80l20-20h60M0 120h50l20 20M400 150h-80l-20-20h-50M400 110h-40l-20 20M200 0v40M160 0v30l10 10M240 0v30l-10 10"/>
      <circle cx="80" cy="160" r="5"/><circle cx="320" cy="150" r="5"/><circle cx="50" cy="120" r="4"/><circle cx="360" cy="110" r="4"/>
    </g>
    <g>
      <rect x="150" y="60" width="100" height="100" rx="12"/>
      ${[0,1,2,3].map(i=>`<rect x="${162+i*22}" y="44" width="8" height="16" rx="2"/><rect x="${162+i*22}" y="160" width="8" height="16" rx="2"/><rect x="134" y="${72+i*22}" width="16" height="8" rx="2"/><rect x="250" y="${72+i*22}" width="16" height="8" rx="2"/>`).join('')}
      <path d="M175 140l20-60h10l20 60h-12l-4-14h-18l-4 14zM192 116h12l-6-20z" fill="var(--hl,#16406E)"/>
    </g>
    <g opacity=".35"><path d="M0 200h400v-14H0z"/></g>`,
  sports: `
    <g opacity=".35"><path d="M0 200c60-40 140-56 200-56s140 16 200 56z"/></g>
    <g>
      <path d="M60 200c10-50 70-80 140-80s130 30 140 80h-20c-10-38-60-60-120-60s-110 22-120 60z"/>
      ${[80,120,160,200,240,280,320].map(x=>`<rect x="${x}" y="90" width="4" height="${30+Math.abs(200-x)/6}" opacity=".6"/>`).join('')}
      <circle cx="200" cy="174" r="12"/><path d="M190 168q10 6 20 0M190 180q10-6 20 0" stroke="var(--hl,#1F6B3A)" stroke-width="2" fill="none"/>
      <rect x="150" y="150" width="5" height="50"/><rect x="160" y="150" width="5" height="50"/><rect x="170" y="150" width="5" height="50"/><rect x="148" y="146" width="29" height="4"/>
    </g>`
};
/* more drawings: coast, palaces, monuments, rivers, hills */
Object.assign(SCENES, {
  beach: `
    <circle cx="300" cy="110" r="34" opacity=".55"/>
    <g opacity=".35"><path d="M0 150h400v50H0z"/></g>
    <g>
      <path d="M0 160q25-8 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v8q-25-8-50 0t-50 0-50 0-50 0-50 0-50 0-50 0-50 0z"/>
      <path d="M0 182q25-8 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v18H0z"/>
      <path d="M70 160c-2-30 2-62 10-84" stroke="#fff" stroke-width="6" fill="none"/>
      <path d="M80 76c-22-2-38 8-44 20 14-8 30-10 44-8-20 6-32 16-36 28 14-12 28-18 38-18-2 12-10 22-18 30 14-8 22-18 24-30 6 12 18 20 34 24-8-10-16-20-18-30 14 2 30 10 38 20-4-14-18-24-36-28 12-2 26 2 38 10-8-14-26-20-44-18z"/>
      <path d="M330 160v-70h14v70z"/><path d="M326 90h22l-4-10h-14z"/><path d="M332 80h10v-8h-10z"/>
      <path d="M200 150l30-10 6 10z" opacity=".7"/>
    </g>`,
  palace: `
    <g opacity=".35"><path d="M0 200v-30h400v30z"/></g>
    <g>
      <rect x="60" y="130" width="280" height="70"/>
      ${[80,120,160,224,264,304].map(x=>`<path d="M${x} 200v-30c0-8 6-14 13-14s13 6 13 14v30z" fill="var(--hl,#000)" opacity=".35"/>`).join('')}
      <rect x="170" y="92" width="60" height="38"/>
      <path d="M176 92c0-22 11-36 24-36s24 14 24 36z"/><rect x="198" y="40" width="4" height="16"/>
      ${[60,326].map(x=>`<rect x="${x}" y="104" width="14" height="26"/><path d="M${x-2} 104c0-10 4-16 9-16s9 6 9 16z"/>`).join('')}
      ${[130,256].map(x=>`<rect x="${x}" y="110" width="14" height="20"/><path d="M${x-2} 110c0-8 4-13 9-13s9 5 9 13z"/>`).join('')}
    </g>`,
  gateway: `
    <g opacity=".35"><path d="M0 178q25-8 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v22H0z"/></g>
    <g>
      <path d="M130 186V96h140v90h-40v-44c0-17-13-30-30-30s-30 13-30 30v44z"/>
      <rect x="124" y="86" width="152" height="10"/>
      ${[130,170,214,254].map(x=>`<rect x="${x}" y="58" width="16" height="28"/><path d="M${x-2} 58c0-10 5-16 10-16s10 6 10 16z"/>`).join('')}
      <path d="M180 78h40v8h-40z"/>
    </g>`,
  redfort: `
    <g opacity=".35"><path d="M0 200v-20h400v20z"/></g>
    <g>
      <path d="M20 200v-60${[...Array(18)].map((_,i)=>`h10v-8h10v8`).join('')}h0v60z"/>
      <path d="M150 200v-90h100v90h-26v-36c0-14-10-24-24-24s-24 10-24 24v36z"/>
      <rect x="144" y="100" width="112" height="10"/>
      ${[150,226].map(x=>`<rect x="${x}" y="78" width="24" height="22"/><path d="M${x-4} 78c0-12 8-20 16-20s16 8 16 20z"/>`).join('')}
      <path d="M186 100c0-14 6-24 14-24s14 10 14 24z"/>
      ${[30,350].map(x=>`<rect x="${x}" y="110" width="20" height="30"/><path d="M${x-3} 110c0-10 6-16 13-16s13 6 13 16z"/>`).join('')}
    </g>`,
  bridge: `
    <g opacity=".35"><path d="M0 176q25-8 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v24H0z"/></g>
    <g>
      <rect x="0" y="150" width="400" height="10"/>
      ${[110,290].map(x=>`<path d="M${x-14} 160V40h28v120z"/><rect x="${x-20}" y="36" width="40" height="8"/>`).join('')}
      <path d="M0 150L96 60M124 60L200 120L276 60M304 60L400 150" stroke="#fff" stroke-width="7" fill="none"/>
      <path d="M40 150L96 100M150 150L124 100M250 150L276 100M360 150L304 100M200 120v30" stroke="#fff" stroke-width="4" fill="none" opacity=".7"/>
    </g>`,
  taj: `
    <g opacity=".35"><path d="M0 200v-18h400v18z"/></g>
    <g>
      <rect x="120" y="170" width="160" height="12"/>
      <rect x="150" y="110" width="100" height="60"/>
      <path d="M200 112h-40c0-30 18-50 40-62 22 12 40 32 40 62z"/><rect x="198" y="34" width="4" height="18"/>
      <path d="M186 170v-30c0-8 6-14 14-14s14 6 14 14v30z" fill="var(--hl,#000)" opacity=".35"/>
      ${[160,226].map(x=>`<rect x="${x}" y="98" width="14" height="12"/><path d="M${x-2} 98c0-8 4-13 9-13s9 5 9 13z"/>`).join('')}
      ${[110,282].map(x=>`<rect x="${x}" y="66" width="8" height="104"/><path d="M${x-2} 66c0-8 3-12 6-12s6 4 6 12z"/><rect x="${x-2}" y="96" width="12" height="3"/><rect x="${x-2}" y="130" width="12" height="3"/>`).join('')}
    </g>`,
  boat: `
    <g opacity=".35"><path d="M0 150h400v50H0z"/></g>
    <g>
      <path d="M0 170q25-8 50 0t50 0 50 0 50 0 50 0 50 0 50 0 50 0v30H0z" opacity=".6"/>
      <path d="M120 160h170c-10 14-30 20-50 20h-80c-20 0-34-8-40-20z"/>
      <path d="M150 160c0-24 20-40 52-40s52 16 52 40z"/>
      <path d="M296 150c-2-30 2-60 10-80" stroke="#fff" stroke-width="5" fill="none"/>
      <path d="M306 70c-20-2-34 8-40 18 12-6 26-8 40-6-18 6-28 14-32 24 12-10 24-14 34-14-2 10-8 20-16 26 12-6 20-16 22-26 6 10 16 18 30 22-6-8-14-18-16-26 12 2 26 8 34 18-4-12-16-22-32-26 10-2 22 2 34 8-8-12-24-18-40-16z"/>
      <path d="M40 150c-2-24 0-46 6-64" stroke="#fff" stroke-width="4" fill="none" opacity=".8"/>
    </g>`,
  hills: `
    <g opacity=".35"><path d="M0 200L70 90l50 60 60-100 70 90 50-50 100 110z"/></g>
    <g>
      <path d="M0 200l60-70 40 40 70-90 60 80 50-40 120 80z"/>
      <path d="M170 80l-14 18 14-6 14 8z" fill="var(--hl,#000)" opacity=".4"/>
      ${[40,320,360].map(x=>`<path d="M${x} 150l14 24h-8l12 20h-36l12-20h-8z"/>`).join('')}
    </g>`,
  dam: `
    <g opacity=".35"><path d="M0 110h400v20H0z"/></g>
    <g>
      <path d="M0 120h400l-30 80H30z"/>
      ${[...Array(9)].map((_,i)=>`<rect x="${52+i*34}" y="132" width="18" height="40" rx="2" fill="var(--hl,#000)" opacity=".35"/>`).join('')}
      <rect x="0" y="112" width="400" height="8"/>
      <path d="M40 200q20-10 40 0t40 0 40 0 40 0 40 0 40 0 40 0 40 0" stroke="#fff" stroke-width="4" fill="none" opacity=".7"/>
    </g>`,
  /* festival wishes: a row of clay diyas with flames, hanging lanterns and sparkles */
  diya: `
    <g opacity=".45">${[[30,40],[96,22],[318,30],[372,58],[250,14],[150,60]].map(([x,y])=>`<path d="M${x} ${y-7}l2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/>`).join('')}</g>
    <g opacity=".55">${[70,330].map(x=>`<path d="M${x} 0v26" stroke="#fff" stroke-width="2"/><path d="M${x-12} 30h24l-4 30h-16z"/><rect x="${x-14}" y="26" width="28" height="5" rx="2"/><path d="M${x-4} 60h8l-4 10z"/>`).join('')}</g>
    <g>${[[110,1],[200,1.35],[290,1]].map(([x,k])=>`<g transform="translate(${x} 200) scale(${k})">
      <path d="M-44-34q0 34 44 34t44-34z"/><path d="M38-38q14 0 22-8-6 14-22 14z"/>
      <path d="M44-46c-6-8-4-18 4-28 2 12 12 14 8 24-2 6-8 8-12 4z" opacity=".95"/>
      <path d="M48-52c-2-4-1-9 2-13 1 6 5 7 3 11z" fill="var(--hl,#000)" opacity=".45"/>
      <path d="M-30-30q30 10 60 0" stroke="var(--hl,#000)" stroke-width="3" fill="none" opacity=".35"/></g>`).join('')}</g>
    <path d="M0 196h400" stroke="#fff" stroke-width="6" opacity=".6"/>`
});

/* Places: India → state → district (Telangana + Andhra Pradesh now; other states state-level) → town/village (story "loc") */
const STATES = [
  ['TG','తెలంగాణ','Telangana'],['AP','ఆంధ్రప్రదేశ్','Andhra Pradesh'],['KA','కర్ణాటక','Karnataka'],['TN','తమిళనాడు','Tamil Nadu'],
  ['MH','మహారాష్ట్ర','Maharashtra'],['KL','కేరళ','Kerala'],['DL','ఢిల్లీ','Delhi'],['OD','ఒడిశా','Odisha'],['CG','ఛత్తీస్‌గఢ్','Chhattisgarh'],
  ['GJ','గుజరాత్','Gujarat'],['RJ','రాజస్థాన్','Rajasthan'],['UP','ఉత్తరప్రదేశ్','Uttar Pradesh'],['MP','మధ్యప్రదేశ్','Madhya Pradesh'],
  ['WB','పశ్చిమ బెంగాల్','West Bengal'],['BR','బిహార్','Bihar'],['JH','జార్ఖండ్','Jharkhand'],['PB','పంజాబ్','Punjab'],['HR','హరియాణా','Haryana'],
  ['HP','హిమాచల్ ప్రదేశ్','Himachal Pradesh'],['UK','ఉత్తరాఖండ్','Uttarakhand'],['JK','జమ్మూ కశ్మీర్','Jammu & Kashmir'],['LA','లద్దాఖ్','Ladakh'],
  ['GA','గోవా','Goa'],['AS','అస్సాం','Assam'],['NE','ఈశాన్య రాష్ట్రాలు','North-East states'],['PY','పుదుచ్చేరి','Puducherry'],['AN','అండమాన్ నికోబార్','Andaman & Nicobar']
];
const AP_DISTRICTS = [
  ['ap-srikakulam','శ్రీకాకుళం','Srikakulam'],['ap-manyam','పార్వతీపురం మన్యం','Parvathipuram Manyam'],['ap-vizianagaram','విజయనగరం','Vizianagaram'],
  ['ap-visakhapatnam','విశాఖపట్నం','Visakhapatnam'],['ap-asr','అల్లూరి సీతారామరాజు','Alluri Sitharama Raju'],['ap-anakapalli','అనకాపల్లి','Anakapalli'],
  ['ap-kakinada','కాకినాడ','Kakinada'],['ap-eastgodavari','తూర్పు గోదావరి','East Godavari'],['ap-konaseema','కోనసీమ','Konaseema'],['ap-eluru','ఏలూరు','Eluru'],
  ['ap-westgodavari','పశ్చిమ గోదావరి','West Godavari'],['ap-ntr','ఎన్టీఆర్ (విజయవాడ)','NTR (Vijayawada)'],['ap-krishna','కృష్ణా','Krishna'],['ap-palnadu','పల్నాడు','Palnadu'],
  ['ap-guntur','గుంటూరు','Guntur'],['ap-bapatla','బాపట్ల','Bapatla'],['ap-prakasam','ప్రకాశం','Prakasam'],['ap-nellore','నెల్లూరు','SPS Nellore'],
  ['ap-kurnool','కర్నూలు','Kurnool'],['ap-nandyal','నంద్యాల','Nandyal'],['ap-anantapur','అనంతపురం','Anantapur'],['ap-sathyasai','శ్రీ సత్యసాయి','Sri Sathya Sai'],
  ['ap-kadapa','వైఎస్ఆర్ కడప','YSR Kadapa'],['ap-annamayya','అన్నమయ్య','Annamayya'],['ap-tirupati','తిరుపతి','Tirupati'],['ap-chittoor','చిత్తూరు','Chittoor']
];
const PLACE_SCENE = {hyderabad:'hyderabad', rangareddy:'city', medchal:'city', sangareddy:'city',
  warangal:'warangal', hanumakonda:'warangal', jangaon:'warangal',
  bhadradri:'temple', yadadri:'temple', sircilla:'temple', jagtial:'temple', mulugu:'temple',
  khammam:'fort', medak:'fort', nizamabad:'fort', suryapet:'village', siddipet:'village', kamareddy:'village',
  peddapalli:'mine', mancherial:'mine', bhupalpally:'mine', karimnagar:'river',
  adilabad:'forest', asifabad:'forest', nirmal:'forest', nalgonda:'dam',
  mahabubnagar:'river', gadwal:'river', wanaparthy:'river', nagarkurnool:'river', narayanpet:'village', vikarabad:'forest', mahabubabad:'village',
  'ap-srikakulam':'beach','ap-manyam':'hills','ap-vizianagaram':'fort','ap-visakhapatnam':'beach','ap-asr':'hills','ap-anakapalli':'village',
  'ap-kakinada':'beach','ap-eastgodavari':'boat','ap-konaseema':'boat','ap-eluru':'boat','ap-westgodavari':'boat','ap-ntr':'dam','ap-krishna':'river',
  'ap-palnadu':'dam','ap-guntur':'city','ap-bapatla':'beach','ap-prakasam':'beach','ap-nellore':'beach','ap-kurnool':'fort','ap-nandyal':'temple',
  'ap-anantapur':'fort','ap-sathyasai':'temple','ap-kadapa':'fort','ap-annamayya':'hills','ap-tirupati':'temple','ap-chittoor':'temple', AP:'river'};
const STATE_SCENE = {TG:'village',AP:'river',KA:'palace',TN:'temple',MH:'gateway',KL:'boat',DL:'redfort',OD:'temple',CG:'forest',GJ:'city',RJ:'fort',
  UP:'taj',MP:'forest',WB:'bridge',BR:'village',JH:'forest',PB:'village',HR:'city',HP:'hills',UK:'hills',JK:'hills',LA:'hills',GA:'beach',AS:'hills',NE:'hills',PY:'beach',AN:'beach'};

/* district lists for other states (key = state code + "-" + short English name) */
const STATE_DISTRICTS = {
 OD: [['od-angul','అంగుల్','Angul'],['od-balangir','బలాంగీర్','Balangir'],['od-balasore','బాలాసోర్','Balasore'],['od-bargarh','బర్గఢ్','Bargarh'],['od-bhadrak','భద్రక్','Bhadrak'],['od-boudh','బౌధ్','Boudh'],['od-cuttack','కటక్','Cuttack'],['od-deogarh','దేవ్‌గఢ్','Deogarh'],['od-dhenkanal','ఢెంకనాల్','Dhenkanal'],['od-gajapati','గజపతి','Gajapati'],['od-ganjam','గంజాం (బరంపురం)','Ganjam'],['od-jagatsinghpur','జగత్‌సింగ్‌పూర్','Jagatsinghpur'],['od-jajpur','జాజ్‌పూర్','Jajpur'],['od-jharsuguda','ఝార్సుగూడ','Jharsuguda'],['od-kalahandi','కలహండి','Kalahandi'],['od-kandhamal','కంధమాల్','Kandhamal'],['od-kendrapara','కేంద్రపడా','Kendrapara'],['od-kendujhar','కెందుఝర్','Kendujhar'],['od-khordha','ఖోర్ధా (భువనేశ్వర్)','Khordha'],['od-koraput','కోరాపుట్','Koraput'],['od-malkangiri','మల్కన్‌గిరి','Malkangiri'],['od-mayurbhanj','మయూర్‌భంజ్','Mayurbhanj'],['od-nabarangpur','నబరంగ్‌పూర్','Nabarangpur'],['od-nayagarh','నయాగఢ్','Nayagarh'],['od-nuapada','నువాపడా','Nuapada'],['od-puri','పూరి','Puri'],['od-rayagada','రాయగడ','Rayagada'],['od-sambalpur','సంబల్‌పూర్','Sambalpur'],['od-subarnapur','సుబర్ణపూర్','Subarnapur'],['od-sundargarh','సుందర్‌గఢ్ (రౌర్కెలా)','Sundargarh']],
 DL: [['dl-central','సెంట్రల్ ఢిల్లీ','Central Delhi'],['dl-east','తూర్పు ఢిల్లీ','East Delhi'],['dl-newdelhi','న్యూఢిల్లీ','New Delhi'],['dl-north','ఉత్తర ఢిల్లీ','North Delhi'],['dl-northeast','ఈశాన్య ఢిల్లీ','North East Delhi'],['dl-northwest','వాయవ్య ఢిల్లీ','North West Delhi'],['dl-shahdara','షాహ్‌దరా','Shahdara'],['dl-south','దక్షిణ ఢిల్లీ','South Delhi'],['dl-southeast','ఆగ్నేయ ఢిల్లీ','South East Delhi'],['dl-southwest','నైరుతి ఢిల్లీ','South West Delhi'],['dl-west','పశ్చిమ ఢిల్లీ','West Delhi']],
 KL: [['kl-thiruvananthapuram','తిరువనంతపురం','Thiruvananthapuram'],['kl-kollam','కొల్లం','Kollam'],['kl-pathanamthitta','పతనంతిట్ట','Pathanamthitta'],['kl-alappuzha','అలప్పుళ','Alappuzha'],['kl-kottayam','కొట్టాయం','Kottayam'],['kl-idukki','ఇడుక్కి','Idukki'],['kl-ernakulam','ఎర్నాకుళం (కొచ్చి)','Ernakulam'],['kl-thrissur','త్రిస్సూర్','Thrissur'],['kl-palakkad','పాలక్కాడ్','Palakkad'],['kl-malappuram','మలప్పురం','Malappuram'],['kl-kozhikode','కోళికోడ్','Kozhikode'],['kl-wayanad','వయనాడ్','Wayanad'],['kl-kannur','కన్నూర్','Kannur'],['kl-kasaragod','కాసరగోడ్','Kasaragod']],
 CG: [['cg-balod','బాలోద్','Balod'],['cg-balodabazar','బలోదా బజార్','Baloda Bazar'],['cg-balrampur','బలరాంపూర్','Balrampur'],['cg-bastar','బస్తర్ (జగదల్‌పూర్)','Bastar'],['cg-bemetara','బేమెతరా','Bemetara'],['cg-bijapur','బీజాపూర్','Bijapur'],['cg-bilaspur','బిలాస్‌పూర్','Bilaspur'],['cg-dantewada','దంతెవాడ','Dantewada'],['cg-dhamtari','ధమ్‌తరీ','Dhamtari'],['cg-durg','దుర్గ్ (భిలాయ్)','Durg'],['cg-gariaband','గరియాబంద్','Gariaband'],['cg-gpm','గౌరేలా-పెండ్రా-మర్వాహీ','Gaurela-Pendra-Marwahi'],['cg-janjgirchampa','జాంజ్‌గీర్-చాంపా','Janjgir-Champa'],['cg-jashpur','జశ్‌పూర్','Jashpur'],['cg-kabirdham','కబీర్‌ధామ్ (కవర్ధా)','Kabirdham'],['cg-kanker','కాంకేర్','Kanker'],['cg-kcg','ఖైరాగఢ్-ఛుయీఖదాన్-గండై','Khairagarh-Chhuikhadan-Gandai'],['cg-kondagaon','కొండగావ్','Kondagaon'],['cg-korba','కోర్బా','Korba'],['cg-korea','కొరియా','Korea'],['cg-mahasamund','మహాసముంద్','Mahasamund'],['cg-mcb','మనేంద్రగఢ్-చిర్మిరి-భరత్‌పూర్','Manendragarh-Chirmiri-Bharatpur'],['cg-mma','మోహ్లా-మాన్‌పూర్-అంబాగఢ్ చౌకీ','Mohla-Manpur-Ambagarh Chowki'],['cg-mungeli','ముంగేలీ','Mungeli'],['cg-narayanpur','నారాయణ్‌పూర్','Narayanpur'],['cg-raigarh','రాయ్‌గఢ్','Raigarh'],['cg-raipur','రాయ్‌పూర్','Raipur'],['cg-rajnandgaon','రాజ్‌నంద్‌గావ్','Rajnandgaon'],['cg-sakti','సక్తీ','Sakti'],['cg-sarangarh','సారంగఢ్-బిలాయిగఢ్','Sarangarh-Bilaigarh'],['cg-sukma','సుక్మా','Sukma'],['cg-surajpur','సూరజ్‌పూర్','Surajpur'],['cg-surguja','సర్గుజా (అంబికాపూర్)','Surguja']],
 GJ: [['gj-ahmedabad','అహ్మదాబాద్','Ahmedabad'],['gj-amreli','అమ్రేలీ','Amreli'],['gj-anand','ఆనంద్','Anand'],['gj-aravalli','ఆరావళి','Aravalli'],['gj-banaskantha','బనాస్‌కాంఠా (పాలన్‌పూర్)','Banaskantha'],['gj-bharuch','భరూచ్','Bharuch'],['gj-bhavnagar','భావ్‌నగర్','Bhavnagar'],['gj-botad','బోటాద్','Botad'],['gj-chhotaudaipur','ఛోటా ఉదయ్‌పూర్','Chhota Udaipur'],['gj-dahod','దాహోద్','Dahod'],['gj-dang','డాంగ్','Dang'],['gj-devbhumidwarka','దేవభూమి ద్వారక','Devbhumi Dwarka'],['gj-gandhinagar','గాంధీనగర్','Gandhinagar'],['gj-girsomnath','గిర్ సోమనాథ్','Gir Somnath'],['gj-jamnagar','జామ్‌నగర్','Jamnagar'],['gj-junagadh','జునాగఢ్','Junagadh'],['gj-kheda','ఖేడా','Kheda'],['gj-kutch','కచ్','Kutch'],['gj-mahisagar','మహీసాగర్','Mahisagar'],['gj-mehsana','మెహసానా','Mehsana'],['gj-morbi','మోర్బీ','Morbi'],['gj-narmada','నర్మదా','Narmada'],['gj-navsari','నవసారీ','Navsari'],['gj-panchmahal','పంచమహల్','Panchmahal'],['gj-patan','పాటణ్','Patan'],['gj-porbandar','పోర్‌బందర్','Porbandar'],['gj-rajkot','రాజ్‌కోట్','Rajkot'],['gj-sabarkantha','సాబర్‌కాంఠా','Sabarkantha'],['gj-surat','సూరత్','Surat'],['gj-surendranagar','సురేంద్రనగర్','Surendranagar'],['gj-tapi','తాపీ','Tapi'],['gj-vadodara','వడోదరా','Vadodara'],['gj-valsad','వల్సాడ్','Valsad'],['gj-vavtharad','వావ్-థరాద్','Vav-Tharad']],
 UP: [['up-agra','ఆగ్రా','Agra'],['up-aligarh','అలీగఢ్','Aligarh'],['up-ambedkarnagar','అంబేడ్కర్ నగర్','Ambedkar Nagar'],['up-amethi','అమేఠీ','Amethi'],['up-amroha','అమ్రోహా','Amroha'],['up-auraiya','ఔరైయా','Auraiya'],['up-ayodhya','అయోధ్య','Ayodhya'],['up-azamgarh','ఆజంగఢ్','Azamgarh'],['up-baghpat','బాగ్‌పత్','Baghpat'],['up-bahraich','బహరాయిచ్','Bahraich'],['up-ballia','బలియా','Ballia'],['up-balrampur','బలరాంపూర్','Balrampur'],['up-banda','బాందా','Banda'],['up-barabanki','బారాబంకీ','Barabanki'],['up-bareilly','బరేలీ','Bareilly'],['up-basti','బస్తీ','Basti'],['up-bhadohi','భదోహీ','Bhadohi'],['up-bijnor','బిజ్నోర్','Bijnor'],['up-budaun','బదాయూఁ','Budaun'],['up-bulandshahr','బులంద్‌షహర్','Bulandshahr'],['up-chandauli','చందౌలీ','Chandauli'],['up-chitrakoot','చిత్రకూట్','Chitrakoot'],['up-deoria','దేవరియా','Deoria'],['up-etah','ఏటా','Etah'],['up-etawah','ఇటావా','Etawah'],['up-farrukhabad','ఫర్రుఖాబాద్','Farrukhabad'],['up-fatehpur','ఫతేపూర్','Fatehpur'],['up-firozabad','ఫిరోజాబాద్','Firozabad'],['up-gautambuddhanagar','గౌతమ్ బుద్ధ నగర్ (నోయిడా)','Gautam Buddh Nagar'],['up-ghaziabad','ఘజియాబాద్','Ghaziabad'],['up-ghazipur','ఘాజీపూర్','Ghazipur'],['up-gonda','గోండా','Gonda'],['up-gorakhpur','గోరఖ్‌పూర్','Gorakhpur'],['up-hamirpur','హమీర్‌పూర్','Hamirpur'],['up-hapur','హాపుడ్','Hapur'],['up-hardoi','హర్దోయీ','Hardoi'],['up-hathras','హాథ్రస్','Hathras'],['up-jalaun','జాలౌన్','Jalaun'],['up-jaunpur','జౌన్‌పూర్','Jaunpur'],['up-jhansi','ఝాన్సీ','Jhansi'],['up-kannauj','కన్నౌజ్','Kannauj'],['up-kanpurdehat','కాన్పూర్ దేహాత్','Kanpur Dehat'],['up-kanpur','కాన్పూర్ నగర్','Kanpur Nagar'],['up-kasganj','కాస్‌గంజ్','Kasganj'],['up-kaushambi','కౌశాంబీ','Kaushambi'],['up-kushinagar','కుశీనగర్','Kushinagar'],['up-lakhimpurkheri','లఖింపూర్ ఖేరీ','Lakhimpur Kheri'],['up-lalitpur','లలిత్‌పూర్','Lalitpur'],['up-lucknow','లక్నో','Lucknow'],['up-maharajganj','మహారాజ్‌గంజ్','Maharajganj'],['up-mahoba','మహోబా','Mahoba'],['up-mainpuri','మైన్‌పురీ','Mainpuri'],['up-mathura','మథుర','Mathura'],['up-mau','మౌ','Mau'],['up-meerut','మీరట్','Meerut'],['up-mirzapur','మీర్జాపూర్','Mirzapur'],['up-moradabad','మొరాదాబాద్','Moradabad'],['up-muzaffarnagar','ముజఫర్‌నగర్','Muzaffarnagar'],['up-pilibhit','పీలీభీత్','Pilibhit'],['up-pratapgarh','ప్రతాప్‌గఢ్','Pratapgarh'],['up-prayagraj','ప్రయాగ్‌రాజ్','Prayagraj'],['up-raebareli','రాయ్‌బరేలీ','Raebareli'],['up-rampur','రాంపూర్','Rampur'],['up-saharanpur','సహారన్‌పూర్','Saharanpur'],['up-sambhal','సంభల్','Sambhal'],['up-santkabirnagar','సంత్ కబీర్ నగర్','Sant Kabir Nagar'],['up-shahjahanpur','షాజహాన్‌పూర్','Shahjahanpur'],['up-shamli','షామ్లీ','Shamli'],['up-shravasti','శ్రావస్తి','Shravasti'],['up-siddharthnagar','సిద్ధార్థ్‌నగర్','Siddharthnagar'],['up-sitapur','సీతాపూర్','Sitapur'],['up-sonbhadra','సోన్‌భద్ర','Sonbhadra'],['up-sultanpur','సుల్తాన్‌పూర్','Sultanpur'],['up-unnao','ఉన్నావ్','Unnao'],['up-varanasi','వారణాసి','Varanasi']],

 KA: [['ka-bagalkot','బాగల్‌కోట్','Bagalkot'],['ka-ballari','బళ్లారి','Ballari'],['ka-belagavi','బెళగావి','Belagavi'],['ka-bengalururural','బెంగళూరు గ్రామీణ','Bengaluru Rural'],
  ['ka-bengaluru','బెంగళూరు అర్బన్','Bengaluru Urban'],['ka-bengalurusouth','బెంగళూరు సౌత్ (రామనగర)','Bengaluru South (Ramanagara)'],['ka-bidar','బీదర్','Bidar'],['ka-chamarajanagar','చామరాజనగర్','Chamarajanagar'],
  ['ka-chikkaballapur','చిక్కబళ్లాపూర్','Chikkaballapur'],['ka-chikkamagaluru','చిక్కమగళూరు','Chikkamagaluru'],['ka-chitradurga','చిత్రదుర్గ','Chitradurga'],['ka-dakshinakannada','దక్షిణ కన్నడ (మంగళూరు)','Dakshina Kannada'],
  ['ka-davanagere','దావణగెరె','Davanagere'],['ka-dharwad','ధార్వాడ్ (హుబ్లీ)','Dharwad'],['ka-gadag','గదగ్','Gadag'],['ka-hassan','హాసన్','Hassan'],['ka-haveri','హావేరి','Haveri'],
  ['ka-kalaburagi','కలబురగి','Kalaburagi'],['ka-kodagu','కొడగు','Kodagu'],['ka-kolar','కోలార్','Kolar'],['ka-koppal','కొప్పళ','Koppal'],['ka-mandya','మండ్య','Mandya'],['ka-mysuru','మైసూరు','Mysuru'],
  ['ka-raichur','రాయచూరు','Raichur'],['ka-shivamogga','శివమొగ్గ','Shivamogga'],['ka-tumakuru','తుమకూరు','Tumakuru'],['ka-udupi','ఉడుపి','Udupi'],['ka-uttarakannada','ఉత్తర కన్నడ','Uttara Kannada'],
  ['ka-vijayapura','విజయపుర','Vijayapura'],['ka-vijayanagara','విజయనగర (హంపి)','Vijayanagara'],['ka-yadgir','యాదగిరి','Yadgir']],
 TN: [['tn-ariyalur','అరియలూరు','Ariyalur'],['tn-chengalpattu','చెంగల్పట్టు','Chengalpattu'],['tn-chennai','చెన్నై','Chennai'],['tn-coimbatore','కోయంబత్తూరు','Coimbatore'],['tn-cuddalore','కడలూరు','Cuddalore'],
  ['tn-dharmapuri','ధర్మపురి','Dharmapuri'],['tn-dindigul','దిండిగల్','Dindigul'],['tn-erode','ఈరోడ్','Erode'],['tn-kallakurichi','కళ్లకురిచ్చి','Kallakurichi'],['tn-kanchipuram','కాంచీపురం','Kanchipuram'],
  ['tn-kanyakumari','కన్యాకుమారి','Kanyakumari'],['tn-karur','కరూర్','Karur'],['tn-krishnagiri','కృష్ణగిరి','Krishnagiri'],['tn-madurai','మదురై','Madurai'],['tn-mayiladuthurai','మయిలాడుతురై','Mayiladuthurai'],
  ['tn-nagapattinam','నాగపట్నం','Nagapattinam'],['tn-namakkal','నామక్కల్','Namakkal'],['tn-nilgiris','నీలగిరి (ఊటీ)','Nilgiris'],['tn-perambalur','పెరంబలూరు','Perambalur'],['tn-pudukkottai','పుదుక్కోట్టై','Pudukkottai'],
  ['tn-ramanathapuram','రామనాథపురం','Ramanathapuram'],['tn-ranipet','రాణిపేట్','Ranipet'],['tn-salem','సేలం','Salem'],['tn-sivaganga','శివగంగ','Sivaganga'],['tn-tenkasi','తెన్‌కాశి','Tenkasi'],
  ['tn-thanjavur','తంజావూరు','Thanjavur'],['tn-theni','తేని','Theni'],['tn-thoothukudi','తూత్తుకుడి','Thoothukudi'],['tn-tiruchirappalli','తిరుచిరాపల్లి','Tiruchirappalli'],['tn-tirunelveli','తిరునెల్వేలి','Tirunelveli'],
  ['tn-tirupathur','తిరుపత్తూరు','Tirupathur'],['tn-tiruppur','తిరుప్పూర్','Tiruppur'],['tn-tiruvallur','తిరువళ్లూరు','Tiruvallur'],['tn-tiruvannamalai','తిరువణ్ణామలై','Tiruvannamalai'],
  ['tn-tiruvarur','తిరువారూర్','Tiruvarur'],['tn-vellore','వేలూరు','Vellore'],['tn-viluppuram','విల్లుపురం','Viluppuram'],['tn-virudhunagar','విరుదునగర్','Virudhunagar']],
 MH: [['mh-ahilyanagar','అహిల్యానగర్ (అహ్మద్‌నగర్)','Ahilyanagar (Ahmednagar)'],['mh-akola','అకోలా','Akola'],['mh-amravati','అమరావతి (మహారాష్ట్ర)','Amravati'],['mh-sambhajinagar','ఛత్రపతి శంభాజీనగర్ (ఔరంగాబాద్)','Chhatrapati Sambhajinagar'],
  ['mh-beed','బీడ్','Beed'],['mh-bhandara','భండారా','Bhandara'],['mh-buldhana','బుల్ధానా','Buldhana'],['mh-chandrapur','చంద్రపూర్','Chandrapur'],['mh-dharashiv','ధారాశివ్ (ఉస్మానాబాద్)','Dharashiv (Osmanabad)'],
  ['mh-dhule','ధులే','Dhule'],['mh-gadchiroli','గడ్చిరోలి','Gadchiroli'],['mh-gondia','గోండియా','Gondia'],['mh-hingoli','హింగోలి','Hingoli'],['mh-jalgaon','జల్గావ్','Jalgaon'],['mh-jalna','జాల్నా','Jalna'],
  ['mh-kolhapur','కొల్హాపూర్','Kolhapur'],['mh-latur','లాతూర్','Latur'],['mh-mumbai','ముంబై సిటీ','Mumbai City'],['mh-mumbaisuburban','ముంబై సబర్బన్','Mumbai Suburban'],['mh-nagpur','నాగ్‌పూర్','Nagpur'],
  ['mh-nanded','నాందేడ్','Nanded'],['mh-nandurbar','నందుర్బార్','Nandurbar'],['mh-nashik','నాశిక్','Nashik'],['mh-palghar','పాల్ఘర్','Palghar'],['mh-parbhani','పర్భణి','Parbhani'],['mh-pune','పుణె','Pune'],
  ['mh-raigad','రాయగఢ్','Raigad'],['mh-ratnagiri','రత్నగిరి','Ratnagiri'],['mh-sangli','సాంగ్లీ','Sangli'],['mh-satara','సతారా','Satara'],['mh-sindhudurg','సింధుదుర్గ్','Sindhudurg'],['mh-solapur','షోలాపూర్','Solapur'],
  ['mh-thane','ఠాణె','Thane'],['mh-wardha','వార్ధా','Wardha'],['mh-washim','వాశిమ్','Washim'],['mh-yavatmal','యవత్మాల్','Yavatmal']]
};
/* other names the news may use for the same district */
const PLACE_ALIAS = {'mh-ahmednagar':'mh-ahilyanagar','mh-aurangabad':'mh-sambhajinagar','mh-chhatrapatisambhajinagar':'mh-sambhajinagar','mh-osmanabad':'mh-dharashiv',
  'mh-mumbaicity':'mh-mumbai','ka-ramanagara':'ka-bengalurusouth','ka-bengaluruurban':'ka-bengaluru','ka-bangalore':'ka-bengaluru','ka-mysore':'ka-mysuru','ka-mangaluru':'ka-dakshinakannada',
  'ka-hubballi':'ka-dharwad','tn-trichy':'tn-tiruchirappalli','tn-ooty':'tn-nilgiris','tn-thenilgiris':'tn-nilgiris','tn-tuticorin':'tn-thoothukudi','ka-gulbarga':'ka-kalaburagi','ka-belgaum':'ka-belagavi'};
const normPlace = k => PLACE_ALIAS[k] || k;
Object.assign(PLACE_SCENE, {'ka-bengaluru':'city','ka-bengalururural':'city','ka-bengalurusouth':'city','ka-mysuru':'palace','ka-kodagu':'hills','ka-chikkamagaluru':'hills','ka-udupi':'beach',
  'ka-dakshinakannada':'beach','ka-uttarakannada':'beach','ka-vijayanagara':'fort','ka-vijayapura':'fort','ka-bidar':'fort','ka-chitradurga':'fort','ka-mandya':'dam',
  'tn-chennai':'beach','tn-kanyakumari':'beach','tn-thoothukudi':'beach','tn-nagapattinam':'beach','tn-ramanathapuram':'beach','tn-cuddalore':'beach','tn-madurai':'temple','tn-thanjavur':'temple',
  'tn-kanchipuram':'temple','tn-tiruvannamalai':'temple','tn-nilgiris':'hills','tn-theni':'hills','tn-coimbatore':'city','tn-tiruppur':'city','tn-salem':'city',
  'mh-mumbai':'gateway','mh-mumbaisuburban':'city','mh-thane':'city','mh-pune':'city','mh-nagpur':'city','mh-ratnagiri':'beach','mh-sindhudurg':'beach','mh-raigad':'fort','mh-satara':'hills',
  'mh-gadchiroli':'forest','mh-chandrapur':'forest','mh-kolhapur':'temple','mh-nashik':'temple','mh-sambhajinagar':'fort'});
Object.assign(PLACE_SCENE, {"od-puri": "temple", "od-khordha": "temple", "od-ganjam": "beach", "od-cuttack": "river", "od-koraput": "hills", "od-malkangiri": "forest", "od-mayurbhanj": "forest", "od-sundargarh": "city", "od-jharsuguda": "mine", "od-angul": "mine", "od-sambalpur": "dam", "dl-newdelhi": "redfort", "dl-central": "redfort", "kl-idukki": "hills", "kl-wayanad": "hills", "kl-ernakulam": "boat", "kl-alappuzha": "boat", "kl-kottayam": "boat", "kl-thiruvananthapuram": "beach", "kl-kozhikode": "beach", "kl-kannur": "beach", "kl-kasaragod": "beach", "kl-kollam": "boat", "kl-pathanamthitta": "temple", "kl-thrissur": "temple", "cg-bastar": "forest", "cg-dantewada": "forest", "cg-sukma": "forest", "cg-bijapur": "forest", "cg-narayanpur": "forest", "cg-raipur": "city", "cg-durg": "city", "cg-korba": "mine", "cg-bilaspur": "city", "gj-ahmedabad": "city", "gj-surat": "city", "gj-vadodara": "city", "gj-rajkot": "city", "gj-gandhinagar": "city", "gj-girsomnath": "temple", "gj-devbhumidwarka": "temple", "gj-porbandar": "beach", "gj-kutch": "village", "gj-narmada": "dam", "gj-jamnagar": "beach", "up-agra": "taj", "up-varanasi": "temple", "up-ayodhya": "temple", "up-mathura": "temple", "up-prayagraj": "river", "up-lucknow": "city", "up-gautambuddhanagar": "city", "up-ghaziabad": "city", "up-kanpur": "city", "up-meerut": "city", "up-gorakhpur": "temple", "up-chitrakoot": "temple"});
function stateOf(s){ if(s.st && s.st!=='IN' && s.st!=='WORLD') return s.st; const p=s.place||''; if(p.startsWith('ap-')||p==='AP') return 'AP'; const m=/^([a-z]{2})-/.exec(p); if(m && STATE_DISTRICTS[m[1].toUpperCase()]) return m[1].toUpperCase(); if(s.st) return ''; if(p&&p!=='TS'&&p!=='IN') return 'TG'; return ''; }
function sceneFor(s){
  if(s.kind==='job') return 'city';
  if(s.art==='diya'||(Array.isArray(s.sec)&&s.sec.includes('wishes'))) return 'diya';
  const pk=normPlace(s.place||''); if(pk && PLACE_SCENE[pk]) return PLACE_SCENE[pk];
  const sec = Array.isArray(s.sec)?s.sec:(s.sec?[s.sec]:[]);
  const cat = s.cat||'';
  const st = stateOf(s);
  if(st && st!=='TG' && STATE_SCENE[st]) return STATE_SCENE[st];
  if(sec.includes('world')||/ప్రపంచం/.test(cat)) return 'world';
  if(sec.includes('ai')||sec.includes('innovation')||/టెక్|AI/.test(cat)) return 'tech';
  if(sec.includes('sports')||/క్రీడ|క్రికెట్/.test(cat)) return 'sports';
  if(sec.includes('agri')||s.art==='farm') return 'village';
  if(/హైదరాబాద్/.test(cat)) return 'hyderabad';
  if(/ఏపీ|ఆంధ్ర/.test(cat)) return 'river';
  if(sec.includes('india')||/భారత్|దేశ/.test(cat)) return 'india';
  if(sec.includes('telangana')) return 'village';
  return 'city';
}
/* name of a place key for chips: Telangana/AP district or "st-XX" state */
function placeLabel(key){
  if(!key) return '';
  if(key.startsWith('st-')){ const s=STATES.find(x=>x[0]===key.slice(3)); return s?s[1]:''; }
  key=normPlace(key); const a=AP_DISTRICTS.find(x=>x[0]===key); if(a) return a[1];
  for(const st in STATE_DISTRICTS){ const d=STATE_DISTRICTS[st].find(x=>x[0]===key); if(d) return d[1]; }
  return '';
}
/* stories may carry their own photo (s.img = "photos/…jpg"): shown in the coloured panel instead of the drawing */
try{ if(typeof document!=='undefined' && !document.getElementById('w2sPhCss')) document.head.insertAdjacentHTML('beforeend','<style id="w2sPhCss">img.ph{position:absolute!important;inset:0;width:100%;height:100%;max-width:none;object-fit:cover;opacity:1;pointer-events:none}img.ph.art2,img.ph.adim{object-fit:contain!important;object-position:50% 50%!important;transform:none!important}:has(>img.ph.art2),:has(>img.ph.adim),:has(>i.apl2){background:#4A0E3F!important}img.alogo{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);height:52%;max-width:46%;aspect-ratio:1;object-fit:contain;pointer-events:none}img.ahero{position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);width:82%;max-height:62%;object-fit:contain;pointer-events:none}span.alw{z-index:2;position:absolute!important;inset:0 0 10% 0!important;margin:0!important;padding:0!important;display:flex;align-items:center;justify-content:center;pointer-events:none}span.alr{height:72%;max-width:none;display:flex;align-items:flex-end;padding-left:4%}span.alr img.alogo{position:static!important;transform:none!important;left:auto;top:auto;height:100%!important;max-width:none!important;width:auto;aspect-ratio:1;object-fit:contain;filter:drop-shadow(0 12px 18px rgba(0,0,0,.4))}i.adot{display:block;height:13%;aspect-ratio:1;border-radius:50%;background:#F5A23A;margin:0 0 7% 2%;flex:none;box-shadow:0 6px 12px rgba(0,0,0,.35)}i.apl,i.apl2{position:absolute;inset:0}i.apl{background:repeating-linear-gradient(135deg,#3A0A31 0 14px,#40103A 14px 28px)}i.apl2{background:radial-gradient(120% 90% at 50% 40%,#6B2A5E,#3A0A31 70%)}img.awxs{position:absolute;right:4%;top:12%;width:30%;max-height:26%;object-fit:contain;z-index:1;filter:drop-shadow(0 8px 12px rgba(0,0,0,.4));pointer-events:none}img.aob{position:absolute;right:6px;top:14%;width:34%;max-height:28%;object-fit:contain;pointer-events:none}.ar .pnl:has(img.ph),.lead .pnl:has(img.ph){min-height:440px}.story .panel:has(img.ph){max-height:44%;min-height:clamp(190px,34vh,300px)}.story .panel:has(img.ph) .stat{font-size:30px;letter-spacing:0;line-height:1.15}.story .panel:has(img.ph) .statl{font-size:13px;max-width:30ch;line-height:1.35}.ar .pnl:has(img.ph) .stat,.lead .pnl:has(img.ph) .stat{font-size:36px!important;line-height:1.15!important}.ar .pnl:has(img.ph) .statl,.lead .pnl:has(img.ph) .statl{font-size:15px}i.phs{position:absolute!important;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.42) 0,rgba(0,0,0,0) 28%,rgba(0,0,0,0) 62%,rgba(0,0,0,.6) 100%)}</style>'); }catch(e){}
function photoFocus(s){ const f=parseFloat(s&&s.imgfy); return f>=0&&f<=1?f:0.3; }
function storyPhoto(s){ const p=String((s&&s.img)||''); return /^photos\/[A-Za-z0-9._-]+\.(jpe?g|png|webp)$/.test(p) ? '/'+p : ''; }
/* draws the story photo into a canvas box (cover crop, faces kept in view) with a dark shade for the text; false if none */
async function drawStoryPhoto(ctx,s,x,y,w,h){
  const src=storyPhoto(s); if(!src) return false;
  try{ const im=await new Promise((ok,no)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=no;i.src=src;});
    const sc=Math.max(w/im.width,h/im.height), dw=im.width*sc, dh=im.height*sc;
    ctx.save(); ctx.beginPath(); ctx.rect(x,y,w,h); ctx.clip();
    const fy=photoFocus(s), top=Math.min(0,Math.max(h-dh,h*0.4-fy*dh)); const fx=(parseFloat(s&&s.imgfx)>=0&&parseFloat(s.imgfx)<=1)?parseFloat(s.imgfx):0.5, left=Math.min(0,Math.max(w-dw,w*0.5-fx*dw)); ctx.drawImage(im,x+left,y+top,dw,dh);
    if(dh>h*1.35){ /* tall photo in a wide box: faded copy behind, whole photo in the middle so the face fits */
      ctx.fillStyle='rgba(12,14,22,.62)'; ctx.fillRect(x,y,w,h);
      const sc2=h/im.height, w2=im.width*sc2; ctx.drawImage(im,x+(w-w2)/2,y,w2,h); }
    const g=ctx.createLinearGradient(0,y,0,y+h); g.addColorStop(0,'rgba(0,0,0,.42)'); g.addColorStop(.28,'rgba(0,0,0,0)'); g.addColorStop(.62,'rgba(0,0,0,0)'); g.addColorStop(1,'rgba(0,0,0,.6)');
    ctx.fillStyle=g; ctx.fillRect(x,y,w,h); ctx.restore(); return true; }catch(e){ return false; }
}

/* 14 Nov 2026: picture boards from the owner's Location Identity + 36-category visual system.
   District story → that district's landmark; otherwise the story type's picture; otherwise the state emblem. */
const ART_D=new Set(["adilabad", "ap", "ap-anakapalli", "ap-anantapur", "ap-annamayya", "ap-asr", "ap-bapatla", "ap-chittoor", "ap-eastgodavari", "ap-eluru", "ap-guntur", "ap-kadapa", "ap-kakinada", "ap-konaseema", "ap-krishna", "ap-kurnool", "ap-manyam", "ap-markapuram", "ap-nandyal", "ap-nellore", "ap-ntr", "ap-palnadu", "ap-polavaram", "ap-prakasam", "ap-sathyasai", "ap-srikakulam", "ap-tirupati", "ap-visakhapatnam", "ap-vizianagaram", "ap-westgodavari", "asifabad", "bhadradri", "bhupalpally", "gadwal", "hanumakonda", "hyderabad", "hyderabad-wide", "jagtial", "jangaon", "kamareddy", "karimnagar", "khammam", "mahabubabad", "mahabubnagar", "mancherial", "medak", "medchal", "mulugu", "nagarkurnool", "nalgonda", "narayanpet", "nirmal", "nizamabad", "peddapalli", "rangareddy", "sangareddy", "siddipet", "sircilla", "suryapet", "tg", "vikarabad", "wanaparthy", "warangal", "yadadri"]);
const ART_SEC={sports:'sports',ai:'technology',innovation:'technology',tech:'technology',world:'world',agri:'agriculture',jobs:'jobs',health:'health',entertainment:'entertainment',cinema:'entertainment',crime:'crime',devotional:'devotional',business:'business',economy:'business',education:'education',weather:'weather',courts:'courts',schemes:'schemes',transport:'transport',environment:'environment',science:'science',auto:'auto',realestate:'realestate',finance:'finance',food:'food',travel:'travel',culture:'culture',women:'women',startups:'startups',cyber:'cyber',factcheck:'factcheck',explainer:'explainers',community:'community',politics:'politics',india:'india',lifestyle:'lifestyle'};
const ART_KEY={economy:'business',campus:'education',school:'education',voters:'politics',unity:'politics',rain:'weather',farm:'agriculture',court:'courts',land:'realestate',diya:'devotional',deadline:'schemes',water:'infrastructure',power:'infrastructure'};
const ART_CAT=[[/రాజకీయ|ఎన్నిక|పోలింగ్|Politic|Election|Polling/i,'politics'],[/వాతావరణ|Weather/i,'weather'],[/క్రైమ్|నేర|Crime/i,'crime'],[/విద్య|Education/i,'education'],[/ఆరోగ్య|Health/i,'health'],[/క్రీడ|\bSports?\b/i,'sports'],[/వ్యాపార|ఆర్థిక|Business|Econom/i,'business'],[/సినిమా|వినోద|Cinema|Entertain/i,'entertainment'],[/వ్యవసాయ|రైతు|Agri|Farm/i,'agriculture'],[/ఉద్యోగ|Jobs?\b/i,'jobs'],[/టెక్|\bTech/i,'technology'],[/భక్తి|ఆధ్యాత్మిక|Devotion/i,'devotional'],[/న్యాయ|కోర్టు|\bCourts?\b|\bLaw\b/i,'courts'],[/రవాణా|Transport/i,'transport'],[/పర్యావరణ|Environment/i,'environment'],[/సంక్షేమ|పథక|Scheme|Welfare/i,'schemes'],[/మౌలిక|Infrastructure/i,'infrastructure'],[/నీటి|Water/i,'infrastructure'],[/సైబర్|Cyber/i,'cyber'],[/ఆహార|\bFood/i,'food'],[/పర్యాటక|Travel|Tourism/i,'travel'],[/పండుగ|సంస్కృతి|Festival|Culture/i,'culture'],[/మహిళ|\bWomen/i,'women'],[/సైన్స్|అంతరిక్ష|\bScience|\bSpace\b/i,'science'],[/ఫ్యాక్ట్|\bFact[- ]?check|\bFacts?\b/i,'factcheck']];
const ART_RX=[[/సైబర్(?!\u200c?ఆబాద్|\s?ఆబాద్)(?:\s?(?:నేర|మోస|క్రైమ్|దాడి|ముఠా|పోలీస)|)|ఆన్‌లైన్ మోసం|cyber(?!abad)|online fraud|phishing/i,'cyber'],[/హత్య|అరెస్ట్|దొంగ|పోలీసు|నిందితు|అత్యాచార|murder|arrest|police|robbery|accused/i,'crime'],[/కోర్టు|హైకోర్టు|సుప్రీం|court|bench|judge/i,'courts'],[/వర్ష|తుపాను|అల్పపీడన|చలి|ఎండ|వాతావరణ|rain|cyclone|weather|IMD|fog/i,'weather'],[/ఆలయ|దేవాలయ|తిరుమల|శ్రీవారి|దీపోత్సవ|పూజ|temple|tirumala|festival puja/i,'devotional'],[/క్రికెట్|మ్యాచ్|టోర్నీ|cricket|\bmatch(?:es)?\b|tournament|olympic/i,'sports'],[/ఆసుపత్రి|వైద్య|ఆరోగ్య|వ్యాధి|hospital|health|medical|dengue|fever/i,'health'],[/సినిమా|చిత్రం|హీరో|OTT|movie|film|box office/i,'entertainment'],[/ఆర్టీసీ|RTC|బస్ పాస్|రైలు|మెట్రో|బస్సు|విమాన|ట్రాఫిక్|railway|metro|bus|flight|airport|traffic/i,'transport'],[/పరీక్ష|విద్యార్థ|పాఠశాల|కళాశాల|యూనివర్సిటీ|exam|student|school|college|university/i,'education'],[/ఉద్యోగ|నోటిఫికేషన్|నియామక|recruit|vacanc|jobs?\b/i,'jobs'],[/పులి|అటవీ|వన్యప్రాణ|కాలుష్య|tiger|forest|wildlife|pollution/i,'environment'],[/రైతు|పంట|వరి|పత్తి|మార్కెట్ యార్డ్|farmer|crop|paddy|cotton|mandi/i,'agriculture'],[/బ్రిడ్జి|రోడ్డు|ప్రాజెక్ట్|నిర్మాణ|bridge|road|flyover|project/i,'infrastructure'],[/పథకం|లబ్ధిదారు|scheme|beneficiar|pension/i,'schemes'],[/ఎన్నిక|ఓటు|అసెంబ్లీ|పార్టీ|election|vote|assembly|party/i,'politics'],[/స్టాక్|మార్కెట్|బ్యాంక్|పెట్టుబడ|stock|market|bank|invest|GDP/i,'business'],[/\bAI\b/,'technology'],[/టెక్|ఐటీ|సాఫ్ట్‌వేర్|software|technology|startup|smartphone/i,'technology']];
const ART_W=[[/ఫ్రాన్స్|పారిస్|France|Paris/i,'paris'],[/బ్రిటన్|లండన్|యూకే|Britain|London|\bUK\b/i,'london'],[/అమెరికా|న్యూయార్క్|America|\bUS\b|USA|New York/i,'new-york'],[/ఇటలీ|రోమ్|Italy|Rome/i,'rome'],[/ఈజిప్ట్|కైరో|Egypt|Cairo/i,'cairo'],[/యూఏఈ|దుబాయ్|UAE|Dubai|Fujairah|ఫుజైరా/i,'dubai'],[/ఆస్ట్రేలియా|సిడ్నీ|Australia|Sydney/i,'sydney'],[/జపాన్|టోక్యో|Japan|Tokyo/i,'tokyo'],[/బ్రెజిల్|Brazil|Rio/i,'rio-de-janeiro'],[/చైనా|బీజింగ్|China|Beijing/i,'beijing'],[/సింగపూర్|Singapore/i,'singapore'],[/టర్కీ|తుర్కియే|ఇస్తాంబుల్|Turkey|T[uü]rkiye|Istanbul/i,'istanbul'],[/దక్షిణాఫ్రికా|South Africa|Cape Town/i,'cape-town'],[/నైజీరియా|Nigeria|Lagos/i,'lagos'],[/స్పెయిన్|Spain|Barcelona/i,'barcelona'],[/రష్యా|మాస్కో|Russia|Moscow/i,'moscow'],[/జోర్డాన్|Jordan|Petra/i,'petra'],[/వెనిస్|Venice/i,'venice']];
/* which news type a story is (one of the 36 boards), '' if unknown */
function artType(s){
  const t=(s.h||'')+' '+((s.en&&s.en.h)||'')+' '+(s.cat||'');
  const cw=String(s.cat||'').split('·').slice(1).join(' ')+' '+String((s.en&&s.en.cat)||'').split('·').slice(1).join(' '); if(cw.trim()) for(const [rx,k] of ART_CAT) if(rx.test(cw)) return k;
  const sec=Array.isArray(s.sec)?s.sec:(s.sec?[s.sec]:[]); for(const x of sec) if(ART_SEC[x]) return ART_SEC[x];
  if(s.art&&ART_KEY[s.art]) return ART_KEY[s.art];
  for(const [rx,k] of ART_RX) if(rx.test(t)) return k;
  return '';
}
/* card picture plan (owner-approved 14 Nov 2026):
   sensitive news → plain background + its type picture, never a landmark;
   weather → the condition is the hero (rain cloud only when it rains; cool / warm tone for cold / heat), the place dimmed behind;
   place = subject (temple, travel, festival) → the landmark alone; place + type → landmark + small type picture;
   type only → its picture; else the state emblem. */
const ART_SENS=/కిడ్నాప్|అదృశ్య|అపహరణ|kidnap|missing girl|missing boy|హత్య|అరెస్ట్|దొంగ|పోలీసు|నిందితు|అత్యాచార|ప్రమాద|మృతి|మరణ|ఆత్మహత్య|చనిపో|కోర్టు|సైబర్ (?:నేర|మోస|క్రైమ్)|మోసం|\bmurder|\barrest|\bpolice\b|\baccident|\bkilled\b|\bdeaths?\b|\bdies\b|\bdied\b|\bsuicide|\bcourts?\b|\bcyber(?!abad)|\bfraud|\bscams?\b|\brape\b/i; // word boundaries: 'bodies' is not 'dies', 'scamper' is not 'scam'

/* owner's 18 topic pictures (14 Nov 2026, art/n/): used when the story is about one of these topics and no district landmark applies */
const ART_N=[[/విద్యుత్ సరఫరా|కరెంట్ కోత|కరెంటు|విద్యుత్ కోత|పవర్ కట్|ట్రాన్స్‌ఫార్మర్|సబ్‌స్టేషన్|విద్యుత్ బిల్లు|power cut|power supply|electricity|transformer|substation|discom/i,'power'],
 [/నీటి సరఫరా|తాగునీ|జలమండలి|నీటి కోత|నీటి కొరత|మంచినీ|water supply|drinking water|HMWSSB|water cut|water shortage/i,'water'],
 [/ట్రాఫిక్|రోడ్డు మూసివే|దారి మళ్లింపు|ట్రాఫిక్ ఆంక్షలు|traffic|road closure|diversion/i,'traffic'],
 [/నిత్యావసర|కూరగాయల ధర|ఉల్లి ధర|టమాటా ధర|బియ్యం ధర|ధరలు పెరిగ|ధరలు తగ్గ|వంట నూనె|essential prices|vegetable prices|onion price|tomato price|price rise/i,'prices'],
 [/టెలికాం|మొబైల్ నెట్‌వర్క్|సిమ్ కార్డ్|5జీ|జియో|ఎయిర్‌టెల్|బీఎస్ఎన్ఎల్|రీచార్జ్|telecom|\b5G\b|Jio|Airtel|BSNL|TRAI|recharge plan/i,'telecom'],
 [/ఎన్ఆర్ఐ|ప్రవాస భారతీయ|వీసా|హెచ్-1బీ|గల్ఫ్ కార్మిక|\bNRI\b|\bvisas?\b|H-1B|diaspora|Gulf workers/i,'nri'],
 [/పరీక్ష ఫలితాలు|ఫలితాలు విడుదల|హాల్ టికెట్|పరీక్ష షెడ్యూల్|పరీక్షలు|ఎంసెట్|ఈఏపీసెట్|నీట్|జేఈఈ|exam|results declared|hall ticket|EAPCET|NEET|JEE/i,'exams'],
 [/విద్యార్థుల|విద్యార్థులకు|హాస్టల్|స్కాలర్‌షిప్|ఫీజు రీయింబర్స్|student|scholarship|hostel/i,'students'],
 [/సెన్సెక్స్|నిఫ్టీ|స్టాక్ మార్కెట్|షేర్ మార్కెట్|ఐపీఓ|Sensex|Nifty|stock market|share market|\bIPO\b/i,'trading'],
 [/కృత్రిమ మేధ|(?:^|[\s(‘'"])ఏఐ(?=[\s,.)’'"]|$)|\bAI\b|artificial intelligence|ChatGPT|Gemini AI|machine learning/i,'ai'], // ఏఐ alone, not the end of ఎఫ్‌ఎస్‌ఎస్‌ఏఐ (FSSAI) – owner 18 Nov
 [/ఆరోగ్య చిట్కా|వ్యాయామం|ఆహార నియమ|health tips|fitness|diet|wellness/i,'healthtips'],
 [/కుటుంబ|family/i,'family'],
 [/స్నేహ|friendship|friends day/i,'friendship']];
const ART_REG=[[/ఆఫ్రికా|ఈజిప్ట్|నైజీరియా|కెన్యా|దక్షిణాఫ్రికా|ఇథియోపియా|Africa|Egypt|Nigeria|Kenya|Ethiopia|Sudan|Ghana/i,'africa'],
 [/ఇరాన్|ఇజ్రాయెల్|గాజా|సౌదీ|యూఏఈ|దుబాయ్|యెమెన్|హార్మూజ్|ఖతార్|కువైట్|ఒమన్|ఇరాక్|సిరియా|లెబనాన్|ఫుజైరా|Iran|Israel|Gaza|Saudi|UAE|Dubai|Yemen|Hormuz|Qatar|Kuwait|Oman|Iraq|Syria|Lebanon|Middle East|Gulf/i,'mideast'],
 [/అమెరికా|యూఎస్|కెనడా|మెక్సికో|ట్రంప్|వాషింగ్టన్|న్యూయార్క్|America|\bUS\b|USA|Canada|Mexico|Washington|New York/i,'namerica'],
 [/యూరప్|బ్రిటన్|యూకే|లండన్|ఫ్రాన్స్|జర్మనీ|ఇటలీ|రష్యా|ఉక్రెయిన్|Europe|Britain|\bUK\b|London|France|Germany|Italy|Russia|Ukraine|Spain/i,'europe'],
 [/చైనా|జపాన్|సింగపూర్|బంగ్లాదేశ్|పాకిస్తాన్|శ్రీలంక|నేపాల్|కొరియా|ఆసియా|China|Japan|Singapore|Bangladesh|Pakistan|Sri Lanka|Nepal|Korea|Asia|Malaysia|Thailand/i,'asia']];
const ART_HAVE=new Set(['pod','condolence','coal','mineworkers','power','water','traffic','prices','telecom','nri','students','friendship','family','healthtips','trading','exams','ai','africa','asia','europe','namerica','mideast','industry','strike']); // art/n pictures we have

/* owner's industries & workers library (14 Nov 2026, art/i/): 56 pictures. Workers first (when the story is about the people),
   then the industry, then the 18 general topics. Company names point to their industry. */
const WORKER_RX=/కార్మిక|కూలీ|ఉద్యోగుల|ఉద్యోగులు|సిబ్బంది|లైన్‌మెన్|నర్సు|వైద్య సిబ్బంది|ఆశా వర్కర్|డెలివరీ బాయ్|workers?\b|employees|staff|labou?r|linemen|nurses|delivery (?:boys|partners)/i;
const ART_IW=[[/ఆసుపత్రి సిబ్బంది|ఆసుపత్రుల్లోని|వైద్య|నర్సు|ఆశా|హెల్త్ వర్కర్|hospital|nurses|doctors|ASHA|health workers/i,'healthcare-workers'],[/పారిశుద్ధ్య|చెత్త|sanitation|garbage/i,'sanitation-workers'],[/భూగర్భ గని|అండర్‌గ్రౌండ్|underground mine/i,'underground-miners'],[/గని|బొగ్గు|సింగరేణి|coal|\bmines?\b/i,'coal-mine-workers'],
 [/భవన నిర్మాణ|నిర్మాణ రంగ|construction/i,'construction-workers'],[/ఉక్కు|స్టీల్|steel/i,'steel-plant-workers'],[/చమురు|గ్యాస్|ఓఎన్జీసీ|oil|gas|ONGC/i,'oil-and-gas-workers'],
 [/విద్యుత్|లైన్‌మెన్|ట్రాన్స్‌కో|డిస్కం|electricity|power|linemen|discom/i,'electricity-line-workers'],[/పాల ఉత్పత్తి|పాల కేంద్ర|పాల సేకరణ|డెయిరీ|dairy|milk plant/i,'dairy-plant-workers'],[/ఆహార శుద్ధి|ఫుడ్ ఫ్యాక్టరీ|ఫుడ్ ప్రాసెసింగ్|food processing|food factory/i,'food-factory-workers'],
 [/వ్యవసాయ కూలీ|రైతు కూలీ|వ్యవసాయ కార్మిక|ఉపాధి హామీ|farm workers|agricultural workers|MGNREGA/i,'agricultural-workers'],[/గోదాం|వేర్‌హౌస్|డెలివరీ|గిగ్|warehouse|delivery|gig workers/i,'logistics-and-warehouse-workers']];
const ART_I=[[/సింగరేణి|కోల్ ఇండియా|బొగ్గు ఉత్పత్తి|coal india|SCCL/i,'n/coal'],[/విశాఖ ఉక్కు|వైజాగ్ స్టీల్|ఆర్ఐఎన్ఎల్|ఉక్కు కర్మాగార|స్టీల్ ప్లాంట్|టాటా స్టీల్|జేఎస్‌డబ్ల్యూ|సెయిల్|\bRINL\b|Vizag Steel|steel plant|Tata Steel|JSW Steel|\bSAIL\b|\bsteel\b/i,'iron-and-steel'],
 [/రిఫైనరీ|ముడి చమురు|పెట్రోలియం|ఐఓసీ|బీపీసీఎల్|హెచ్‌పీసీఎల్|refinery|crude oil|petroleum|\bIOCL?\b|BPCL|HPCL/i,'crude-oil-and-refining'],[/సహజ వాయువు|గ్యాస్ పైప్‌లైన్|ఎల్‌పీజీ|గెయిల్|natural gas|gas pipeline|\bLPG\b|\bGAIL\b|\bCNG\b/i,'natural-gas'],
 [/థర్మల్ విద్యుత్|విద్యుత్ కేంద్ర|విద్యుత్ ఉత్పత్తి|ఎన్టీపీసీ|జెన్‌కో|power plant|thermal power|power generation|\bNTPC\b|genco/i,'electric-power'],[/సౌర|సోలార్|పవన విద్యుత్|గ్రీన్ ఎనర్జీ|పునరుత్పాదక|solar|wind power|wind energy|renewable|green energy/i,'solar-and-wind'],
 [/అల్యూమినియం|హిండాల్కో|నాల్కో|aluminium|aluminum|Hindalco|NALCO/i,'aluminium'],[/రాగి|copper/i,'copper'],[/సిమెంట్|అల్ట్రాటెక్|cement|UltraTech/i,'cement'],[/గాజు|సిరామిక్|glass|ceramic/i,'glass-and-ceramics'],
 [/రసాయన|కెమికల్|chemical/i,'chemicals'],[/ఎరువు|యూరియా|డీఏపీ|fertili[sz]er|urea|\bDAP\b/i,'fertilizers'],[/పాల ఉత్పత్తి|పాల ధర|డెయిరీ|విజయ డెయిరీ|అమూల్|కరీంనగర్ డెయిరీ|\bdairy\b|milk price|Amul/i,'milk-and-dairy'],
 [/(?<!ప్రా)ధాన్యం|వరి కొనుగోలు|రైస్ మిల్లు|బియ్యం మిల్లు|పిండి మిల్లు|paddy|rice mill|flour mill|grain/i,'grain-and-flour-milling'],[/చక్కెర|చెరకు|షుగర్ ఫ్యాక్టరీ|sugar|sugarcane/i,'sugar'],[/వంట నూనె ఉత్పత్తి|పామాయిల్|ఆయిల్ పామ్|edible oil|palm oil|oil palm/i,'edible-oils'],
 [/బేకరీ|బిస్కెట్|bakery|biscuit/i,'bakery-and-biscuits'],[/చాక్లెట్|కోకో|cocoa|chocolate|confectionery/i,'cocoa-and-confectionery'],[/శీతల పానీయ|బేవరేజ్|soft drink|beverage/i,'beverages'],
 [/చికెన్|కోడి|పౌల్ట్రీ|మాంసం|గుడ్ల|poultry|chicken|\bmeat\b|eggs?\b/i,'meat-and-poultry'],[/మత్స్య|చేపల|రొయ్య|ఆక్వా|fisheries|aquaculture|shrimp|prawn|fish farm/i,'fisheries-and-aquaculture'],
 [/చేనేత|వస్త్ర|టెక్స్‌టైల్|మగ్గం|పత్తి మిల్లు|నేత కార్మిక|handloom|textile|apparel|garment|weaver/i,'textiles-and-apparel'],[/కాగితం|ప్యాకేజింగ్|paper mill|packaging/i,'paper-and-packaging'],[/ఎఫ్ఎంసీజీ|సబ్బు|FMCG|personal care|household goods/i,'household-and-personal-care'],
 [/ఎలక్ట్రిక్ వాహన|ఈవీ|కార్ల తయారీ|ఆటోమొబైల్|మారుతి|హ్యుందాయ్|టాటా మోటార్స్|మహీంద్రా|electric vehicle|\bEVs?\b|automobile|car maker|Maruti|Hyundai|Tata Motors|Mahindra|Ola Electric/i,'automobiles-and-evs'],
 [/యంత్రాల తయారీ|యంత్ర పరికరాల|ఇంజనీరింగ్ పరిశ్రమ|మెషినరీ|machinery|engineering firm|L&T|Larsen/i,'machinery-and-engineering'],[/సెమీకండక్టర్|చిప్ తయారీ|semiconductor|chip (?:plant|making|maker)/i,'semiconductors'],[/ఎలక్ట్రానిక్స్|మొబైల్ తయారీ|electronics|phone manufactur/i,'electronics'],
 [/ఐటీ కంపెనీ|ఐటీ ఉద్యోగ|సాఫ్ట్‌వేర్ (?:కంపెనీ|సంస్థ|ఉద్యోగ|నిపుణ)|ఇన్ఫోసిస్|టీసీఎస్|విప్రో|కాగ్నిజెంట్|\bIT (?:company|firm|jobs|sector|employees)|software (?:company|firm|jobs)|Infosys|\bTCS\b|Wipro|Cognizant|HCLTech|Tech Mahindra|Microsoft|Google|Amazon Web/i,'it-and-ai'],
 [/ఫార్మా|బల్క్ డ్రగ్|ఔషధ|మందుల కంపెనీ|డాక్టర్ రెడ్డీస్|అరబిందో|హెటిరో|భారత్ బయోటెక్|pharma|bulk drug|drug maker|Dr Reddy|Aurobindo|Hetero|Bharat Biotech|Divi/i,'pharmaceuticals'],
 [/ఆసుపత్రి నిర్మాణ|కొత్త ఆసుపత్రి|మెడికల్ కాలేజీ|ఆరోగ్యశ్రీ|hospital (?:opened|building|beds)|medical college|Aarogyasri/i,'healthcare-services'],
 [/రియల్ ఎస్టేట్|అపార్ట్‌మెంట్|ఇందిరమ్మ ఇళ్ల|ఇళ్ల నిర్మాణ|గృహ నిర్మాణ|టవర్ ఇళ్లు|real estate|apartment|housing project|construction project/i,'construction-and-real-estate'],
 [/ఓడరేవు|పోర్టు|షిప్పింగ్|లాజిస్టిక్స్|కంటైనర్|డ్రై పోర్టు|\bport\b|shipping|logistics|container/i,'logistics-and-shipping'],[/బ్యాంకు|బ్యాంక్|బీమా|ఎల్ఐసీ|రుణాల|\bbank|insurance|\bLIC\b|loan/i,'banking-and-insurance'],
 [/పర్యాటక శాఖ|హోటల్|హోటళ్ల|హోటళ్లు|హాస్పిటాలిటీ|రిసార్ట్|tourism|hotel|hospitality|resort/i,'tourism-and-hospitality'],
 [/ఈ-కామర్స్|అమెజాన్|ఫ్లిప్‌కార్ట్|ఆన్‌లైన్ షాపింగ్|e-commerce|Flipkart|Amazon|Meesho|online shopping/i,'e-commerce'],[/క్విక్ కామర్స్|జెప్టో|బ్లింకిట్|స్విగ్గీ|జొమాటో|quick commerce|Zepto|Blinkit|Swiggy|Zomato|food delivery/i,'quick-commerce-and-delivery'],
 [/ఆన్‌లైన్ గేమ్|గేమింగ్|online gam|gaming/i,'online-gaming'],[/బెట్టింగ్|betting/i,'online-betting'],[/క్రిప్టో|బిట్‌కాయిన్|crypto|bitcoin/i,'crypto-and-digital-assets'],
 [/యూపీఐ|ఫోన్‌పే|పేటీఎం|డిజిటల్ చెల్లింపు|ఫిన్‌టెక్|\bUPI\b|PhonePe|Paytm|fintech|digital payment/i,'fintech-and-payments'],[/సోషల్ మీడియా|యూట్యూబర్|ఇన్‌ఫ్లుయెన్సర్|ఇన్‌స్టాగ్రామ్|social media|YouTuber|influencer|Instagram|creator/i,'social-media-and-creators']];
/* owner's civic-news (art/cv) and welfare-scheme (art/s) pictures, 14 Nov 2026. Category pictures, not official logos. */
const ART_S=[[/కళ్యాణ\s?లక్ష్మి|కల్యాణ\s?లక్ష్మి|Kalyana\s?Lakshmi/i,'kalyana-lakshmi'],[/షాదీ ముబారక్|Shaadi Mubarak/i,'shaadi-mubarak'],
 [/ఆత్మీయ భరోసా|Atmeeya Bharosa/i,'atmeeya-bharosa'],[/రైతు\s?భరోసా|రైతు\s?బంధు|పీఎం[ -]?కిసాన్|Rythu\s?Bharosa|Rythu\s?Bandhu|PM[ -]KISAN/i,'rythu-bharosa'],[/రైతు\s?బీమా|పంటల? బీమా|Rythu\s?Bima|crop insurance|Fasal Bima/i,'rythu-bima'],
 [/రుణ\s?మాఫీ|loan waiver/i,'crop-loan-waiver'],[/ఇందిరమ్మ ఇళ్ల|ఇందిరమ్మ ఇల్లు|ఇందిరమ్మ ఇండ్ల|డబుల్ బెడ్‌?రూం|గృహ నిర్మాణ పథక|Indiramma (?:house|housing|homes)|housing scheme|2BHK|PMAY/i,'indiramma-housing'],
 [/గృహ\s?జ్యోతి|ఉచిత విద్యుత్|Gruha\s?Jyothi|free electricity|free power/i,'gruha-jyothi'],[/(?:మహాలక్ష్మి|ఉచిత).{0,25}(?:బస్|ప్రయాణ)|ఉచిత బస్|free bus|Mahalakshmi.{0,25}bus|women.{0,15}free (?:bus|travel)/i,'mahalakshmi-bus'],
 [/(?:మహాలక్ష్మి|రూ\.?\s?500).{0,25}(?:గ్యాస్|సిలిండర్)|వంట గ్యాస్|గ్యాస్ సిలిండర్|ఎల్పీజీ|\bLPG\b|cooking gas|gas cylinder/i,'mahalakshmi-lpg'],
 [/ఆరోగ్య\s?శ్రీ|ఆయుష్మాన్|Aarogyasri|Arogyasri|Ayushman/i,'aarogyasri'],[/ఆరోగ్య లక్ష్మి|అంగన్‌?వాడీ|పౌష్టికాహార|Aarogya Lakshmi|anganwadi|nutrition/i,'aarogya-lakshmi'],
 [/విదేశీ విద్య|ఓవర్సీస్ స్కాలర్|overseas scholarship|Videshi Vidya|study abroad scholarship/i,'overseas-scholarships'],[/ఫీజు రీయింబర్స్|ఈ-?పాస్|fee reimbursement|\bePASS\b/i,'fee-reimbursement'],[/స్కాలర్‌?షిప్|ఉపకార వేతన|scholarship/i,'scholarships'],
 [/రాజీవ్ యువ వికాస|స్వయం ఉపాధి రుణ|Rajiv Yuva Vikasam|self-employment loan/i,'rajiv-yuva-vikasam'],
[/పింఛన్|(?<![\u0C00-\u0C7F])పెన్షన్|ఆసరా పింఛ|చేయూత|\bpensions?\b|Aasara|Cheyutha/i,'pensions'],
 [/సన్న\s?బియ్య|(?<![\u0C00-\u0C7F])రేషన్ బియ్య|(?<![\u0C00-\u0C7F])రేషన్ (?:కార్డ|షాప|దుకాణ|సరుకు)|పౌరసరఫరా(?!ల(?: శాఖ)? మంత్రి)|fine rice|ration rice|ration card|civil supplies(?! minister)|\bration\b/i,'fine-rice']];
const ART_CV=[[/డంపింగ్ యార్డ్|డంప్ ?యార్డ్|dumping yard|dump ?yard|landfill/i,'dumping-yards'],[/చెత్త (?:పేరుకు|కుప్ప|సేకరణ|తొలగించ)|చెత్త సమస్య|garbage (?:pile|heap|not collected|collection)|uncollected garbage/i,'uncollected-garbage'],
 [/(?<!ఇంకుడు )గుంతల|పాట్‌?హోల్|pothole|damaged road|road damage|దెబ్బతిన్న రోడ్/i,'potholes'],[/మ్యాన్‌?హోల్|manhole/i,'open-manholes'],
 [/వీధి కుక్క|కుక్కల బెడద|కుక్క కాటు|stray (?:dog|cattle|animal)|dog bite/i,'stray-animals'],[/దోమల|ఫాగింగ్|mosquito|fogging/i,'mosquito-breeding'],
 [/విద్యుత్ కోత|కరెంట్ కోత|కరెంటు కోత|పవర్ కట్|power cut|power outage|outage/i,'power-cuts'],[/వీధి దీపా|స్ట్రీట్ ?లైట్|streetlight|street light/i,'streetlights'],
 [/పైప్‌?లైన్ (?:లీక్|పగిలి)|నీరు వృథా|pipeline (?:leak|burst)|water leak/i,'water-leaks'],[/తాగునీటి (?:కొరత|సమస్య|ఇబ్బంద)|నీటి కొరత|ట్యాంకర్|water shortage|water crisis|tanker/i,'water-shortage'],
 [/మురుగు నీరు|సీవరేజ్|sewage/i,'sewage-on-roads'],[/నాలా|డ్రైనేజీ|కాలువ పొంగి|\bdrains?\b|drainage|\bnalas?\b/i,'overflowing-drains'],
 [/పబ్లిక్ టాయిలెట్|ప్రజా మరుగుదొడ్|public toilet/i,'public-toilets'],[/ఫుట్‌?పాత్ ఆక్రమణ|footpath encroach|blocked footpath|walkway/i,'blocked-walkways'],[/ఫుట్‌?పాత్|footpath|pavement/i,'damaged-footpaths'],
 [/బస్ షెల్టర్|బస్ స్టాప్|bus shelter|bus stop/i,'bus-stops'],[/చెట్లు కూలి|కూలిన చెట్ల|నేలకొరిగిన|fallen trees?|uprooted/i,'fallen-trees'],[/విద్యుత్ తీగల|వేలాడుతున్న వైర్|live wires?|exposed wires?|hanging wires?/i,'exposed-wires'],
 [/శబ్ద కాలుష్య|గాలి నాణ్యత|వాయు కాలుష్య|\bAQI\b|air quality|air pollution|noise pollution/i,'air-noise-pollution'],[/(?:పార్కు|park).{0,30}(?:నిర్వహణ|అధ్వాన|దుస్థితి|పిచ్చి మొక్క|పట్టించుకో|maintenance|neglect|renovat|overgrown)|playground/i,'park-maintenance'],
 [/రోడ్డు పనుల|తవ్వకాల|దుమ్ము|road ?work|dug[- ]up|\bdust\b/i,'roadwork-dust'],[/జలమయ|నీట మునిగిన (?:కాలనీ|రోడ్|వీధు)|వరద నీరు|waterlogg|inundat|flooded (?:roads|streets|colonies)/i,'flooded-streets'],[/రోడ్లపై (?:వర్షపు )?నీరు|rainwater on roads/i,'rainwater-on-roads']];
function artScheme(tt){ for(const [rx,k] of ART_S) if(rx.test(tt)) return 's/'+k; return ''; }
function artCivic(tt){ for(const [rx,k] of ART_CV) if(rx.test(tt)) return 'cv/'+k; return ''; }
function artIndustry(tt){
  if(WORKER_RX.test(tt)) for(const [rx,k] of ART_IW) if(rx.test(tt)) return 'i/'+k;
  for(const [rx,k] of ART_I) if(rx.test(tt)) return k.startsWith('n/')?k:'i/'+k;
  return ''; }
function artNews(t){ for(const [rx,k] of ART_N) if(rx.test(t)) return k; return ''; }
function artRegion(t){ for(const [rx,k] of ART_REG) if(rx.test(t)) return k; return ''; }
function artPlan0(s){
  if(s&&s._orig) s=s._orig; // Tenglish: choose the picture from the Telugu original
  if(!s||s.kind) return null;
  // owner 18 Nov 2026 ("no mistakes, we are on the Play Store"): the newsroom now picks the picture for every story
  // by reading it (field "pic", from tools/pictures.md). Keyword guessing below is only the fallback for old stories.
  if(String(s.pic||'')==='logo') return {m:'logo'}; // owner 24 Nov 2026: "if you do not have any image, don't use anyone – just our logo"
  { const pc=String(s.pic||''), m=pc.match(/^(c|o|i|n|s|cv|w|d|e)\/([a-z0-9-]+)$/);
    if(m){ if(m[1]==='c') return {m:'cat',cat:m[2]}; if(m[1]==='o') return {m:'plain',obj:m[2]}; return {m:'land',bg:m[1]==='d'?m[2]:pc}; } }
  const pk=normPlace(String(s.place||'').toLowerCase()), land=ART_D.has(pk)&&!['tg','ap'].includes(pk)?pk:'';
  const st=stateOf(s), sland=st==='AP'?'ap':(st==='TG'||st==='TS')?'tg':'';
  const t=(s.h||'')+' '+((s.en&&s.en.h)||'')+' '+(s.p||'').slice(0,160);
  let type=artType(s);
  if(type==='transport'&&/ఆర్టీసీ|RTC|బస్|\bbus/i.test(t)&&!/రైలు|రైల్వే|ట్రైన్|\btrain|\brail|మెట్రో|metro/i.test(t)) type='bus'; // bus-and-pass story: bus picture, no train
  if(['crime','courts','cyber','factcheck'].includes(type)||ART_SENS.test(t)){
    const o=['crime','courts','cyber','factcheck'].includes(type)?type:/సైబర్ (?:నేర|మోస|క్రైమ్)|సైబర్ నేరగాళ్ల|cyber(?!abad)|మోసం|fraud|scam/i.test(t)?'cyber':/కోర్టు|court/i.test(t)?'courts':/హత్య|అరెస్ట్|దొంగ|పోలీసు|నిందితు|murder|arrest|police|robbery/i.test(t)?'crime':'';
    // owner 14 Nov 2026: death news gets the respectful candle-and-lilies picture (not for court verdicts or fact-checks)
    if(!['courts','factcheck'].includes(type)&&/మృతి|మృతుల|మృతుడు|మృతురాలు|మృతదేహ|అంత్యక్రియ|మరణించ|మరణం|మరణాలు|మృత్యువాత|ప్రాణాలు కోల్పో|ప్రాణం కోల్పో|కన్నుమూ|చనిపో|దుర్మరణ|నివాళ|సంతాప|\bdead\b|\bdied\b|\bdies\b|\bdeaths?\b|killed|passes away|passed away|condolence|tribute|obituary|funeral|bodies found/i.test([s.h,s.statl,s.stat,(s.en&&s.en.h)||''].join(' '))&&!/మరణ\s?శిక్ష|death sentence|death penalty/i.test(s.h||'')) return {m:'land',bg:'n/condolence'};
    return {m:'plain',obj:o};
  }
  { const tq=[s.h,s.statl,String(s.p||'').split(/[.!?।]/)[0]].join(' ');
    if(!/ప్రపంచం|World/.test(String(s.cat||''))){ const ck=artCivic([s.h,s.statl,(s.en&&s.en.h)||''].join(' ')); if(ck) return {m:'land',bg:ck}; } // civic problems: the problem picture (owner, 14 Nov)
    if(/చెరువు|ఆక్రమణ|lake encroach/i.test(tq)) return {m:'cat',cat:'environment'}; // lakes, air quality: environment, not a weather cloud
    if(type!=='weather'&&/రైళ్లు|రైలు|ట్రైన్|\btrains?\b|railway/i.test(tq)&&!/ప్రపంచం|World/.test(String(s.cat||''))) return {m:'cat',cat:'transport'}; }
  if(type==='weather'){
    const bg=land||sland, rain=/వర్ష|వాన|తుపాను|అల్పపీడన|వరద|జల్లు|rain|cyclone|flood|shower|depression/i.test(t), heat=/ఎండ|వడగాల్పు|ఉక్కపోత|heat|hot\b|scorch/i.test(t), cold=/చలి|పొగమంచు|మంచు|cold|chill|fog|mist|winter/i.test(t);
    const wo=rain?'weather':(heat||cold)?'':'cloud';
    let wbg=bg; if((bg==='ap'||!bg)&&st!=='TG'&&/తుపాను|కోస్తా|తీర|సముద్ర|cyclone|coast/i.test(t)) wbg='ap-visakhapatnam'; // cyclone/coast with no district: a coastal picture, not an inland temple
    if(wbg) return {m:'land',bg:wbg,wx:rain?'weather':(heat||cold)?'':'cloud'}; // reviewer 14 Nov: place picture clear; one small weather sign in the sky corner
    return {m:'wx',bg,obj:wo,tone:rain?'':heat?'warm':cold?'cool':''};
  }
  // industry, mines, factories, strikes: an industry picture, never a temple or district landmark (owner, 14 Nov 2026).
  // New owner pictures go in art/n/ and their key in ART_HAVE; until then the closest existing picture is used.
  { const has=k=>ART_HAVE.has(k);
    if(/సింగరేణి|బొగ్గు|ఓపెన్ కాస్ట్|coal|Singareni|colliery|SCCL/i.test(t)){ if(/గని కార్మిక|కాంట్రాక్టు కార్మిక|కార్మికుల|మైనర్లు|బోనస్|వేతన|భద్రత|సమ్మె|mine workers|miners|workers|bonus|wage|safety|strike/i.test(t)) return {m:'land',bg:'n/'+(has('mineworkers')?'mineworkers':has('strike')?'strike':'coal')}; return {m:'land',bg:'n/'+(has('coal')?'coal':'power')}; }
    const tt0=[s.h,s.statl,String(s.p||'').split(/[.!?।]/)[0]].join(' ');
    if(/సమ్మె|సమ్మెకు|కార్మికుల ఆందోళన|కార్మిక సంఘ|యూనియన్|లాకౌట్|\bstrike\b|\bunion\b|lockout/i.test(tt0)) return has('strike')?{m:'land',bg:'n/strike'}:{m:'cat',cat:'infrastructure'};
    // owner 16 Nov 2026: pod-car / PRT news shows a POD, not a car, bus or train
    if(/పాడ్\s?కార్|పాడ్‌కార్|పాడ్ ట్యాక్సీ|పీఆర్‌టీ|పీఆర్టీ|పర్సనల్ ర్యాపిడ్|\bpod[- ]?(?:cars?|taxis?)\b|\bPRT\b|personal rapid transit/i.test(tt0+' '+((s.en&&s.en.h)||''))) return has('pod')?{m:'land',bg:'n/pod'}:{m:'logo'};  // until the owner's pod picture arrives: the neutral logo card, never a wrong vehicle
    if(/పరిశ్రమ|ఫ్యాక్టరీ|కర్మాగార|పారిశ్రామిక|ఫార్మా కంపెనీ|industry|industrial|factory|manufacturing/i.test(tt0)) return has('industry')?{m:'land',bg:'n/industry'}:{m:'cat',cat:'infrastructure'}; }
  // owner 14 Nov 2026: the TOPIC picture comes before the district landmark (a health story shows health, not the town's temple).
  // Landmarks stay for temple, travel, culture and general local / political news.
  // owner 16 Nov 2026 (OU hostels story showed a power tower because the summary said 'restore water and power'):
  // topic pictures follow the MAIN EVENT – headline + picture line. The first summary sentence is used only when the
  // newsroom gave no picture key of its own (s.art).
  const tt=[s.h,s.stat,s.statl].concat(s.art?[]:[String(s.p||'').split(/[.!?।]/)[0]]).join(' ');
  const isWorld=!land&&(/ప్రపంచం|World/.test(t+(s.cat||''))||(Array.isArray(s.sec)&&s.sec.includes('world')));
  if(!isWorld){ const sk=artScheme(tt); if(sk) return {m:'land',bg:sk}; if(/చెత్త|పారిశుద్ధ్య|garbage|sanitation/i.test(tt)&&/శుభ్ర|తొలగి|తరలి|స్వచ్ఛ|clean|clear|drive/i.test(tt)) return {m:'land',bg:'i/sanitation-workers'}; if(/చెత్త|మురుగు|పారిశుద్ధ్య|డ్రైనేజీ|garbage|sewage|sanitation/i.test(tt)) return {m:'cat',cat:'environment'}; if(/పౌరసరఫరా|(?<!కార్పొ)రేషన్ (?:కార్డ|బియ్య|షాప|దుకాణ|సరుకు)|civil supplies|\bration\b/i.test(tt)) return {m:'land',bg:'n/prices'};
    if(/(?:^|[\s(‘'"])ఏఐ(?=[\s,.)’'"]|$)|\bAI\b|కృత్రిమ మేధ|సెన్సెక్స్|నిఫ్టీ|స్టాక్ మార్కెట్|Sensex|Nifty/i.test(String(s.h||''))){ const nk0=artNews(tt); if(nk0) return {m:'land',bg:'n/'+nk0}; }
    const ik=artIndustry(tt); if(ik) return {m:'land',bg:ik};
    const nk=artNews(tt); if(nk) return {m:'land',bg:'n/'+nk}; }
  if(!isWorld&&/చెత్త|మురుగు|కాలుష్య|పారిశుద్ధ్య|డ్రైనేజీ|దోమల|garbage|sewage|pollution|sanitation|drainage/i.test(tt)) return {m:'cat',cat:'environment'};
  if(!isWorld&&['politics','infrastructure','community','lifestyle','explainers','health','education','agriculture','sports','entertainment','business','finance','technology','science','jobs','schemes','environment','food','auto','realestate','startups','women','transport','bus','courts','cyber','crime'].includes(type)) return {m:'cat',cat:type};
  if(land&&['devotional','travel','culture'].includes(type)) return {m:'land',bg:land};
  // owner 14 Nov: place known → the place picture alone, nothing pasted on top
  if(land) return {m:'land',bg:land};
  if(!land&&(/ప్రపంచం|World/.test(t+(s.cat||''))||(Array.isArray(s.sec)&&s.sec.includes('world')))&&!['weather'].includes(type)){ for(const [rx,k] of ART_W) if(rx.test(t+' '+(s.cat||''))) return {m:'land',bg:'w/'+k}; const rg=artRegion(t+' '+(s.cat||'')); if(rg) return {m:'land',bg:'n/'+rg}; }
  { const nk=artNews(t); if(nk) return {m:'land',bg:'n/'+nk}; }
  if(type) return {m:'cat',cat:type};
  if(sland) return {m:'land',bg:sland};
  const world=/ప్రపంచం|World/.test(t+(s.cat||''))||s.st==='WORLD'||(Array.isArray(s.sec)&&s.sec.includes('world'));
  if(world){ for(const [rx,k] of ART_W) if(rx.test(t+' '+(s.cat||''))) return {m:'land',bg:'w/'+k}; const rg=artRegion(t+' '+(s.cat||'')); if(rg) return {m:'land',bg:'n/'+rg}; return {m:'cat',cat:'world'}; }
  if(s.st==='IN'||/భారత్|India/.test(s.cat||'')) return {m:'cat',cat:'india'};
  return {m:'logo'};   // nothing to show: our own logo (vector, sharp at any size)
}
// owner 21 Nov 2026: the new illustrated library (art/e/, 240 pictures) replaces the old topic, civic, scheme, industry and news pictures.
// Old keys keep working and now point to the new picture. Keys with no new picture keep the old one.
// Temples and district landmarks (d/), devotional, world cities (w/) and metals (m/) are not changed.
const ART_NEW={"c/agriculture":"e/paddy-transplanting","c/andhra":"e/vijayawada-river-barrage","c/auto":"e/electric-vehicle-charging","c/bus":"e/bus-stand-rush","c/business":"e/industrial-production","c/community":"e/neighbourhood-volunteers","c/courts":"e/court-hearing","c/crime":"e/police-investigation","c/culture":"e/classical-dance-performance","c/cyber":"e/cyber-fraud-complaint","c/education":"e/government-school-classroom","c/entertainment":"e/telugu-cinema-screening","c/environment":"e/tree-plantation","c/explainers":"e/public-library-reading","c/factcheck":"e/misinformation-verification","c/finance":"e/banking-services","c/food":"e/street-food-vendor","c/health":"e/primary-health-centre","c/india":"e/parliamentary-debate","c/infrastructure":"e/flyover-construction","c/jobs":"e/recruitment-notification","c/lifestyle":"e/morning-tea-stall","c/local":"e/weekly-village-bazaar","c/politics":"e/voting-day","c/realestate":"e/housing-and-real-estate","c/schemes":"e/ration-shop-distribution","c/science":"e/scientific-research","c/sports":"e/cricket-match","c/startups":"e/women-entrepreneurs","c/technology":"e/robotics-training","c/telangana":"e/hyderabad-old-city-market","c/transport":"e/railway-station-departures","c/travel":"e/airport-travel","c/weather":"e/heavy-monsoon-rain","c/women":"e/self-help-group-meeting","c/world":"e/international-diplomacy","n/ai":"e/artificial-intelligence","n/coal":"e/singareni-coal-workers","n/condolence":"e/remembrance-and-condolence","n/exams":"e/board-examination-hall","n/family":"e/family-household-budget","n/healthtips":"e/community-yoga","n/mineworkers":"e/singareni-coal-workers","n/nri":"e/overseas-worker-remittances","n/power":"e/transformer-repair","n/prices":"e/inflation-and-groceries","n/students":"e/teacher-vacancy-protest","n/telecom":"e/mobile-network-coverage","n/trading":"e/stock-market-movement","n/traffic":"e/traffic-congestion","n/water":"e/drinking-water-queue","n/industry":"e/industrial-production","n/strike":"e/teacher-vacancy-protest","cv/air-noise-pollution":"e/air-pollution","cv/blocked-walkways":"e/footpath-encroachment","cv/bus-stops":"e/bus-stand-rush","cv/damaged-footpaths":"e/footpath-encroachment","cv/dumping-yards":"e/neighbourhood-garbage-dump","cv/exposed-wires":"e/transformer-repair","cv/fallen-trees":"e/fallen-tree-after-storm","cv/flooded-streets":"e/waterlogged-street","cv/mosquito-breeding":"e/dengue-prevention-drive","cv/open-manholes":"e/sewer-maintenance","cv/overflowing-drains":"e/overflowing-open-drain","cv/park-maintenance":"e/neglected-public-park","cv/potholes":"e/potholes-and-broken-roads","cv/power-cuts":"e/power-cut-at-home","cv/public-toilets":"e/public-toilet-maintenance","cv/rainwater-on-roads":"e/waterlogged-street","cv/roadwork-dust":"e/road-widening","cv/sewage-on-roads":"e/overflowing-open-drain","cv/stray-animals":"e/stray-dog-management","cv/streetlights":"e/broken-streetlights","cv/traffic-congestion":"e/traffic-congestion","cv/uncollected-garbage":"e/neighbourhood-garbage-dump","cv/water-leaks":"e/burst-water-pipeline","cv/water-shortage":"e/water-tanker-supply","s/aarogya-lakshmi":"e/anganwadi-nutrition","s/aarogyasri":"e/public-health-coverage-desk","s/atmeeya-bharosa":"e/employment-guarantee-work","s/crop-loan-waiver":"e/tenant-farmer-loan-assistance","s/fee-reimbursement":"e/student-scholarship-desk","s/fine-rice":"e/ration-shop-distribution","s/gruha-jyothi":"e/electricity-meter-reading","s/indiramma-housing":"e/affordable-housing-support","s/kalyana-lakshmi":"e/wedding-community-meal","s/mahalakshmi-bus":"e/women-bus-travel-support","s/mahalakshmi-lpg":"e/lpg-cylinder-delivery","s/overseas-scholarships":"e/international-student-journey","s/pensions":"e/pension-distribution","s/rajiv-yuva-vikasam":"e/skill-training-workshop","s/rythu-bharosa":"e/farmer-assistance-counter","s/rythu-bima":"e/farmer-assistance-counter","s/scholarships":"e/student-scholarship-desk","s/shaadi-mubarak":"e/wedding-community-meal","i/agricultural-workers":"e/paddy-transplanting","i/automobiles-and-evs":"e/electric-vehicle-charging","i/banking-and-insurance":"e/banking-services","i/coal":"e/singareni-coal-workers","i/coal-mine-workers":"e/singareni-coal-workers","i/construction-and-real-estate":"e/housing-and-real-estate","i/construction-workers":"e/construction-workers","i/dairy-plant-workers":"e/dairy-milk-collection","i/e-commerce":"e/gig-delivery-work","i/electric-power":"e/transformer-repair","i/electricity-line-workers":"e/transformer-repair","i/fertilizers":"e/fertilizer-and-seed-supply","i/fintech-and-payments":"e/digital-payments","i/fisheries-and-aquaculture":"e/nellore-aquaculture","i/food-factory-workers":"e/factory-employment","i/healthcare-services":"e/primary-health-centre","i/healthcare-workers":"e/hospital-outpatient-queue","i/it-and-ai":"e/artificial-intelligence","i/logistics-and-shipping":"e/visakhapatnam-port-operations","i/logistics-and-warehouse-workers":"e/freight-truck-movement","i/milk-and-dairy":"e/dairy-milk-collection","i/quick-commerce-and-delivery":"e/gig-delivery-work","i/sanitation-workers":"e/sewer-maintenance","i/stock-trading":"e/stock-market-movement","i/telecommunications":"e/mobile-network-coverage","i/textiles-and-apparel":"e/handloom-weaving","i/tourism-and-hospitality":"e/tourism-and-travel","i/social-media-and-creators":"e/digital-newsroom","i/solar-and-wind":"e/rooftop-solar-installation","i/underground-miners":"e/singareni-coal-workers","i/meat-and-poultry":"e/poultry-farm-care","i/machinery-and-engineering":"e/industrial-production"};
// owner 21 Nov 2026: party news shows that party's picture (art/e/party-*). Only when ONE party is named in the
// headline/picture line; two or more parties, or a party whose picture is not ready (AAP, ABVP, AIMIM, DYFI, NSUI),
// keep the neutral voting picture. Never on crime, court, death or world stories (those keep their own picture).
const ART_PARTY=[ // order matters: longer names first (YSR Congress before Congress, BJYM before BJP, CPI(M) before CPI)
  ['ysrcp',/వైఎస్సార్\s?కాంగ్రెస్|వైఎస్ఆర్\s?కాంగ్రెస్|వైఎస్సార్సీపీ|వైఎస్సార్‌సీపీ|వైఎస్ఆర్సీపీ|వైసీపీ|వైకాపా|\bYSRCP\b|\bYSR\s?Congress|\bYCP\b/i],
  ['bjym',/బీజేవైఎం|భాజయుమో|\bBJYM\b/i],
  ['bjp',/బీజేపీ|భాజపా|బిజెపి|\bBJP\b|Bharatiya Janata/i],
  ['brs',/బీఆర్ఎస్|బీఆర్‌ఎస్|భారత రాష్ట్ర సమితి|టీఆర్ఎస్|\bBRS\b|\bTRS\b|Bharat Rashtra Samithi/i],
  ['tdp',/టీడీపీ|తెలుగుదేశం|తెదేపా|\bTDP\b|Telugu Desam/i],
  ['janasena',/జనసేన|\bJana\s?Sena\b/i],
  ['bsp',/బీఎస్పీ|బహుజన్ సమాజ్|\bBSP\b|Bahujan Samaj/i],
  ['cpim',/సీపీఐ\s?\(?ఎం\)?|సీపీఎం|\bCPI\s?\(M\)|\bCPI-M\b|\bCPM\b|Marxist/i],
  ['cpi',/సీపీఐ|\bCPI\b|Communist Party of India/i],
  ['sfi',/ఎస్ఎఫ్ఐ|ఎస్‌ఎఫ్‌ఐ|\bSFI\b|Students'? Federation of India/i],
  ['congress',/కాంగ్రెస్|హస్తం పార్టీ|\bCongress\b|\bINC\b/i],
  ['aap',/ఆమ్ ఆద్మీ|\bAAP\b|Aam Aadmi/i],['abvp',/ఏబీవీపీ|\bABVP\b/i],['aimim',/ఎంఐఎం|మజ్లిస్|\bA?IMIM\b|\bMIM\b|Owaisi|ఒవైసీ/i],
  ['dyfi',/డీవైఎఫ్ఐ|\bDYFI\b/i],['nsui',/ఎన్ఎస్‌యూఐ|ఎన్ఎస్యూఐ|\bNSUI\b/i]];
const ART_PARTY_HAVE=new Set(['ysrcp','bjym','bjp','brs','tdp','janasena','bsp','cpim','cpi','sfi','congress']); // cpim added 22 Nov 2026 (official logo picture)
function artParty(s,a){
  const o=(s&&s._orig)||s; if(!o||!a||a.m!=='land') return '';
  const pol=/రాజకీయ|Politic/i.test(String(o.cat||'')+' '+String(((o.en||{}).cat)||'')) || String(o.pic||'')==='c/politics';
  if(!(/^e\/(voting-day|election-office)$/.test(a.bg)||(pol&&(!/\//.test(a.bg)||/^e\/(government-press-briefing|peaceful-public-protest|public-policy-announcement)$/.test(a.bg))))) return ''; // politics picture, or a district / press-meet / protest picture on a politics story
  let t=[o.h,o.statl,(o.en&&o.en.h)||'',(o.en&&o.en.statl)||''].join(' ').replace(/‌|‍/g,'');
  const hit=[]; for(const [k,rx] of ART_PARTY){ if(rx.test(t)){ hit.push(k); t=t.replace(new RegExp(rx.source,'gi'),' '); } }
  if(hit.length!==1||!ART_PARTY_HAVE.has(hit[0])) return '';
  // owner 22 Nov 2026: when ONE party speaks, condemns or protests, show that party's picture ("…ఖండించిన బీఆర్‌ఎస్" → BRS).
  // Stay neutral only when that party is the TARGET (బీఆర్‌ఎస్‌పై / బీఆర్‌ఎస్‌ను …, "against BRS"), or for alliances and killings.
  const tt=[o.h,o.statl,(o.en&&o.en.h)||''].join(' ').replace(/‌|‍/g,''); const rx=(ART_PARTY.find(x=>x[0]===hit[0])||[])[1];
  if(rx){ const g=new RegExp('(?:'+rx.source+')\\s?(?:పై|ను|ని|కు|కి|మీద|పట్ల)','i'); if(g.test(tt)) return '';
    if(new RegExp('(?:against|slams?|targets?|hits out at|attacks?|on)\\s+(?:the\\s+)?(?:'+rx.source+')','i').test(tt)) return ''; }
  if(/కూటమి|alliance|NDA\b|హత్య|murder|kill/i.test(tt)) return '';
  return 'e/party-'+hit[0];
}
/* owner 23 Nov 2026: HYDRAA stories show HYDRAA's own logo (sent by the owner); no "AI picture" label on logos */
const ART_ORG=[['hydraa',/హైడ్రా(?!లిక్|క్సి|జన్|కార్బన్|ఫోన్)|\bHYDRAA?\b|Hydraa/i]];
function artOrg(s){ const o=(s&&s._orig)||s; if(!o||o.kind) return ''; const t=[o.h,o.statl,(o.en&&o.en.h)||''].join(' ');
  for(const [k,rx] of ART_ORG) if(rx.test(t)) return 'e/logo-'+k; return ''; }
function artPlan(s){ const ok=artOrg(s); if(ok) return {m:'land',bg:ok}; const a=artPlan1(s); const pk=artParty(s,a); return pk?{m:'land',bg:pk}:a; }
function artPlan1(s){ const a=artPlan0(s); if(!a) return a;
  if(a.m==='cat'){ const k=ART_NEW['c/'+a.cat]; if(k) return {m:'land',bg:k}; }
  else if(a.m==='plain'&&a.obj){ const k=ART_NEW['c/'+a.obj]; if(k) return {m:'land',bg:k}; }
  else if(a.m==='land'&&ART_NEW[a.bg]) return Object.assign({},a,{bg:ART_NEW[a.bg]});
  return a; }
function artImg(s){ const a=artPlan(s); if(!a) return ''; return a.m==='logo'?'/art/logo.svg':a.m==='cat'?'/art/c/'+a.cat+'.jpg':a.bg?artBg(a.bg):'/art/o/'+(a.obj||'local')+'.webp'; }
const ART_DISC={te:'AI రూపొందించిన చిత్రం',en:'AI-generated illustration',hi:'AI से बना चित्र'};
function artBg(k,big){ const e=big?'.jpg':'.webp'; return /^(?:w|n|i|cv|s|e)\//.test(k)?'/art/'+k+e:'/art/d/'+k+e; } // cards: light 960px WebP; shared 4K photo: full-size original
function artHTML(a){
  const im=(src,cls)=>`<img class="${cls}" src="${src}" alt="" decoding="async">`;
  if(a.m==='logo') return `<i class="apl2"></i><span class="alw"><span class="alr"><img class="alogo" src="/art/logo.svg" alt=""><i class="adot"></i></span></span>`;
  if(a.m==='cat') return `<i class="apl2"></i>${im('/art/o/'+a.cat+'.webp','ahero acat')}`; // illustration-led: one large object
  if(a.m==='plain') return `<i class="apl"></i>${a.obj?im('/art/o/'+a.obj+'.webp','ahero'):''}`; // no object = number-led (shorter header)
  if(a.m==='wx') return `${a.bg?im(artBg(a.bg),'ph art2 adim'):'<i class="apl"></i>'}${a.tone?`<i class="atone ${a.tone}"></i>`:''}${a.obj?im('/art/o/'+a.obj+'.webp','ahero awx'):''}`;
  return im(artBg(a.bg),'ph art2 aland')+(a.m==='landobj'?im('/art/o/'+a.obj+'.webp','aob'):'')+(a.wx?im('/art/o/'+a.wx+'.webp','awxs'):''); // location-led: landmark dominant, map badge quietened
}
/* same picture on the shared / downloaded photo */
async function drawArtPlan(ctx,s,x,y,w,h,fill){
  const a=artPlan(s); if(!a) return false;
  const L=src=>new Promise((ok,no)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=no;i.src=src;});
  // share photos: 2560px HD pictures (sharp when zoomed); fall back to the normal picture if the HD one is missing
  const LB=k=>/^e\//.test(k)?L(artBg(k,1)):L('/art/hd/'+(/^(?:w|n|i|cv|s)\//.test(k)?k:'d/'+k)+'.webp').catch(()=>L(artBg(k,1))); // e/ library has no HD copies: go straight to the original
  const cover=(im)=>{ ctx.fillStyle='#4A0E3F'; ctx.fillRect(x,y,w,h); if(fill){ const sc=Math.max(w/im.width,h/im.height),dw=im.width*sc,dh=im.height*sc; ctx.drawImage(im,x+(w-dw)/2,y+h-dh,dw,dh); return; } const sc=Math.min(w/im.width,h/im.height),dw=im.width*sc,dh=im.height*sc; ctx.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,dw,dh); }; // fit the whole picture, plum around it
  const contain=(im,cx,cy,mw,mh)=>{ const sc=Math.min(mw/im.width,mh/im.height),dw=im.width*sc,dh=im.height*sc; ctx.drawImage(im,cx-dw/2,cy-dh/2,dw,dh); };
  const stripes=()=>{ ctx.fillStyle='#3A0A31'; ctx.fillRect(x,y,w,h); ctx.strokeStyle='#40103A'; ctx.lineWidth=28; for(let k=-h;k<w+h;k+=56){ ctx.beginPath(); ctx.moveTo(x+k,y); ctx.lineTo(x+k+h,y+h); ctx.stroke(); } };
  try{ ctx.save(); ctx.beginPath(); ctx.rect(x,y,w,h); ctx.clip();
    if(a.m==='cat'){ const rg=ctx.createRadialGradient(x+w/2,y+h*.42,10,x+w/2,y+h*.42,w*.7); rg.addColorStop(0,'#6B2A5E'); rg.addColorStop(1,'#3A0A31'); ctx.fillStyle=rg; ctx.fillRect(x,y,w,h); ctx.shadowColor='rgba(0,0,0,.45)'; ctx.shadowBlur=30; ctx.shadowOffsetY=18; contain(await L('/art/o/full/'+a.cat+'.webp'),x+w/2,y+h*.42,w*.84,h*.62); ctx.shadowColor='transparent'; }
    else if(a.m==='plain'){ stripes(); if(a.obj){ ctx.shadowColor='rgba(0,0,0,.45)'; ctx.shadowBlur=30; ctx.shadowOffsetY=18; contain(await L('/art/o/full/'+a.obj+'.webp'),x+w/2,y+h*.42,w*.82,h*.62); ctx.shadowColor='transparent'; } }
    else if(a.m==='wx'){ if(a.bg){ cover(await LB(a.bg)); ctx.fillStyle='rgba(20,4,17,.25)'; ctx.fillRect(x,y,w,h); } else stripes();
      if(a.tone){ ctx.fillStyle=a.tone==='cool'?'rgba(120,160,210,.30)':'rgba(245,130,40,.30)'; ctx.fillRect(x,y,w,h); if(a.tone==='cool'){ const g=ctx.createLinearGradient(0,y+h*.45,0,y+h); g.addColorStop(0,'rgba(235,240,250,0)'); g.addColorStop(1,'rgba(235,240,250,.35)'); ctx.fillStyle=g; ctx.fillRect(x,y,w,h); } }
      if(a.obj){ ctx.shadowColor='rgba(0,0,0,.45)'; ctx.shadowBlur=30; ctx.shadowOffsetY=18; contain(await L('/art/o/full/'+a.obj+'.webp'),x+w/2,y+h*.40,w*.7,h*.5); ctx.shadowColor='transparent'; } }
    else if(a.m==='logo'){ const rg=ctx.createRadialGradient(x+w/2,y+h*.42,10,x+w/2,y+h*.42,w*.7); rg.addColorStop(0,'#6B2A5E'); rg.addColorStop(1,'#3A0A31'); ctx.fillStyle=rg; ctx.fillRect(x,y,w,h); const lg=await L('/art/logo.svg'); const sz=Math.min(h*.66,w*.52), ds=sz*.13, gap=sz*.02, tw=sz+gap+ds, lx=x+(w-tw)/2, ly=y+h*.45-sz/2; ctx.shadowColor='rgba(0,0,0,.4)'; ctx.shadowBlur=30; ctx.shadowOffsetY=14; ctx.drawImage(lg,lx,ly,sz,sz); ctx.fillStyle='#F5A23A'; ctx.beginPath(); ctx.arc(lx+sz+gap+ds/2,ly+sz-sz*.07-ds/2,ds/2,0,Math.PI*2); ctx.fill(); ctx.shadowColor='transparent'; }
    else { cover(await LB(a.bg),.5); if(a.wx){ ctx.shadowColor='rgba(20,4,17,.5)'; ctx.shadowBlur=20; ctx.shadowOffsetY=10; contain(await L('/art/o/full/'+a.wx+'.webp'),x+w*.8,y+h*.2,w*.3,h*.22); ctx.shadowColor='transparent'; } if(a.m==='landobj'){ ctx.shadowColor='rgba(20,4,17,.55)'; ctx.shadowBlur=24; ctx.shadowOffsetY=14; contain(await L('/art/o/full/'+a.obj+'.webp'),x+w*.8,y+h*.3,w*.32,h*.26); ctx.shadowColor='transparent'; } }
    if(a.m!=='logo'){ const g=ctx.createLinearGradient(0,y,0,y+h); g.addColorStop(0,'rgba(46,8,39,.5)'); g.addColorStop(.22,'rgba(46,8,39,0)'); g.addColorStop(.5,'rgba(46,8,39,0)'); g.addColorStop(.72,'rgba(46,8,39,.85)'); g.addColorStop(1,'rgba(46,8,39,.97)'); ctx.fillStyle=g; ctx.fillRect(x,y,w,h); }
    ctx.restore(); return true; }catch(e){ ctx.restore(); return false; }
}
function sceneSVG(s, cls){
  const ph=storyPhoto(s);
  const ap=(!ph&&cls!=='cv'&&cls!=='og')?artPlan(s):null;
  if(ap) return artHTML(ap)+'<i class="phs"></i>';
  if(ph && cls!=='cv' && cls!=='og') return `<img class="ph" style="object-position:50% ${Math.round(photoFocus(s)*100)}%" src="${ph}" alt="" loading="lazy" decoding="async"><i class="phs"></i>`;
  const k=sceneFor(s); const body=SCENES[k]||SCENES.city;
  const hole = k==='hyderabad' ? `<mask id="m${cls}"><rect width="400" height="200" fill="#fff"/><g fill="#000">${SCENES.hyderabadHole}</g></mask>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" class="${cls||'scene'}" viewBox="0 0 400 200" preserveAspectRatio="xMidYMax meet" fill="#fff" aria-hidden="true">${hole?`<defs>${hole}</defs><g mask="url(#m${cls})">${body}</g>`:body}</svg>`;
}

/* ---------- reader's language (Telugu / English / Hindi) shared by app, website and article pages ---------- */
function w2sLang(){ try{ const q=new URLSearchParams(location.search).get('l'); if(/^(te|en|hi)$/.test(q||'')) return q;
  const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); return /^(te|en|hi)$/.test(p.lang||'')?p.lang:'te'; }catch(e){ return 'te'; } }
/* a story in the reader's language (missing translations stay Telugu); sidFn keeps the story's link the same */
function w2sTr(s,sidFn,l){ l=l||w2sLang(); if(!s||l==='te'||!s[l]||typeof s[l]!=='object') return s;
  const o=Object.assign({},s,s[l]); if(sidFn) o._sid=sidFn(s); o._lang=l; return o; }
const W2S_UI={te:{posts:'పోస్టులు',lastd:'చివరి తేదీ',today:'ఈరోజే చివరి రోజు',left:n=>n+' రోజులు మిగిలాయి',few:n=>n+' రోజులే',off:'అధికారిక వెబ్‌సైట్‌లో దరఖాస్తు →',warn:'⚠️ ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి. అధికారిక వెబ్‌సైట్‌లోనే దరఖాస్తు చేయండి.',rows:{posts:'పోస్టులు',qual:'అర్హత',exp:'అనుభవం',loc:'ఎక్కడ',age:'వయసు',pay:'జీతం',last:'చివరి తేదీ',walk:'వాక్-ఇన్',how:'ఎలా దరఖాస్తు'},why:'ఇది ఎందుకు ముఖ్యం?',read:'పూర్తి వార్త చదవండి →',src:'మూలం',listen:'🔊 తెలుగులో వినండి',wa:'WhatsAppలో షేర్ చేయండి',speech:'te-IN'},
  en:{posts:'Posts',lastd:'Last date',today:'Last day today',left:n=>n+' days left',few:n=>'only '+n+' days',off:'Apply on the official website →',warn:'⚠️ Never pay anyone for a job. Apply only on the official website.',rows:{posts:'Posts',qual:'Eligibility',exp:'Experience',loc:'Where',age:'Age',pay:'Pay',last:'Last date',walk:'Walk-in',how:'How to apply'},why:'Why it matters',read:'Read full story →',src:'Source',listen:'🔊 Listen',wa:'Share on WhatsApp',speech:'en-IN'},
  hi:{posts:'पद',lastd:'अंतिम तिथि',today:'आज आख़िरी दिन',left:n=>n+' दिन बाकी',few:n=>'सिर्फ़ '+n+' दिन',off:'आधिकारिक वेबसाइट पर आवेदन करें →',warn:'⚠️ नौकरी के लिए किसी को पैसे न दें। सिर्फ़ आधिकारिक वेबसाइट पर आवेदन करें।',rows:{posts:'पद',qual:'योग्यता',exp:'अनुभव',loc:'कहाँ',age:'आयु',pay:'वेतन',last:'अंतिम तिथि',walk:'वॉक-इन',how:'कैसे आवेदन करें'},why:'यह क्यों ज़रूरी है?',read:'पूरी खबर पढ़ें →',src:'स्रोत',listen:'🔊 सुनें',wa:'WhatsApp पर शेयर करें',speech:'hi-IN'}};
/* the తె / EN / हि switch in the website header */
function w2sLangSwitch(){ const w=document.getElementById('lsw'); if(!w) return; const cur=w2sLang();
  w.querySelectorAll('button').forEach(b=>{ b.setAttribute('aria-pressed',String(b.dataset.l===cur));
    b.onclick=()=>{ try{ const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); p.lang=b.dataset.l; localStorage.setItem('w2s.prefs',JSON.stringify(p)); }catch(e){}
      const u=new URL(location.href); u.searchParams.delete('l'); location.href=u.pathname+u.search; }; }); }

/* a job in the reader's language; _h0 keeps the original Telugu headline for the link */
function w2sJob(j,l){ l=l||w2sLang(); const o=(l!=='te'&&j&&j[l]&&typeof j[l]==='object'&&j[l].h)?Object.assign({},j,j[l]):Object.assign({},j); o._h0=j.h; return o; }

/* website menu: show the sections that fit in one row, the rest go under "మరిన్ని ▾" (nothing hides off the edge) */
function w2sNavFit(nav){
  if(!nav) return; nav.classList.add('fit');
  if(nav.querySelector('.s2more')) return; // Swipe2News menu: scrolls sideways, extra items live in its own More menu
  let more=nav.querySelector('.nmore'); if(more){ more.querySelectorAll('.nmenu a').forEach(a=>nav.insertBefore(a,more)); more.remove(); }
  if(nav.scrollWidth<=nav.clientWidth+1) return;
  more=document.createElement('div'); more.className='nmore';
  more.innerHTML='<button type="button" aria-expanded="false" aria-haspopup="true">మరిన్ని ▾</button><div class="nmenu" hidden></div>';
  nav.appendChild(more); const menu=more.querySelector('.nmenu'), btn=more.querySelector('button');
  const links=[...nav.querySelectorAll(':scope > a')];
  for(let i=links.length-1;i>0 && nav.scrollWidth>nav.clientWidth+1;i--){ menu.insertBefore(links[i],menu.firstChild); }
  if(menu.querySelector('a[aria-current="true"]')) btn.classList.add('cur');
  btn.onclick=e=>{ e.stopPropagation(); const o=menu.hidden; menu.hidden=!o; btn.setAttribute('aria-expanded',String(o)); };
  const close=()=>{ menu.hidden=true; btn.setAttribute('aria-expanded','false'); };
  menu.addEventListener('click',close);
  // on a computer: opens when the mouse comes over "మరిన్ని", closes by itself when the mouse leaves
  let lt; more.addEventListener('mouseenter',e=>{ if(matchMedia('(hover: hover)').matches){ clearTimeout(lt); menu.hidden=false; btn.setAttribute('aria-expanded','true'); } });
  more.addEventListener('mouseleave',()=>{ clearTimeout(lt); lt=setTimeout(close,250); });
  if(!w2sNavFit.doc){ w2sNavFit.doc=1; const shut=()=>document.querySelectorAll('.nmore .nmenu').forEach(m=>{ m.hidden=true; const b=m.parentNode.querySelector('button'); if(b) b.setAttribute('aria-expanded','false'); });
    document.addEventListener('click',shut); addEventListener('scroll',shut,{passive:true}); document.addEventListener('keydown',e=>{ if(e.key==='Escape') shut(); });
    let t; addEventListener('resize',()=>{ clearTimeout(t); t=setTimeout(()=>document.querySelectorAll('nav.secs').forEach(w2sNavFit),150); }); }
}

/* First visit through a shared story link: ask the reader's language once (తెలుగు / English / हिन्दी), then show the story in it */
function w2sAskLang(){
  return; // replaced by the Swipe2News language screen (web/s2n.js)
  try{
    if(!document.querySelector('article.ar') || document.getElementById('sheet') || document.getElementById('pick')) return;
    if(/[?&]l=(te|en|hi)\b/.test(location.search)) return;
    const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); if(p.lang) return;
  }catch(e){ return; }
  const o=document.createElement('div'); o.id='w2sAsk';
  o.style.cssText='position:fixed;inset:0;z-index:9999;background:rgba(8,12,24,.72);display:flex;align-items:center;justify-content:center;padding:18px';
  o.innerHTML='<div style="background:#fff;color:#202124;border-radius:20px;padding:22px 20px;width:min(380px,100%);box-shadow:0 20px 60px rgba(0,0,0,.4);text-align:center;font-family:\'Noto Sans Telugu\',\'Noto Sans Devanagari\',system-ui,sans-serif">'
   +'<img src="/logo.png" alt="Swipe2News" style="height:34px;margin-bottom:10px">'
   +'<div style="font:800 19px/1.4 inherit">భాష ఎంచుకోండి</div><div style="font:600 14px/1.5 inherit;color:#555">Choose your language · अपनी भाषा चुनें</div>'
   +'<div style="display:grid;gap:10px;margin-top:16px">'
   +'<button type="button" data-l="te" style="min-height:52px;border:0;border-radius:12px;background:#4A0E3F;color:#fff;font:800 19px inherit;cursor:pointer">తెలుగు</button>'
   +'<button type="button" data-l="en" style="min-height:52px;border:0;border-radius:12px;background:#2E0827;color:#fff;font:800 19px inherit;cursor:pointer">English</button>'
   +'<button type="button" data-l="hi" style="min-height:52px;border:0;border-radius:12px;background:#c47a00;color:#fff;font:800 19px inherit;cursor:pointer">हिन्दी</button>'
   +'</div></div>';
  document.body.appendChild(o);
  o.querySelectorAll('button[data-l]').forEach(b=>b.onclick=()=>{
    const l=b.dataset.l;
    try{ const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); p.lang=l; localStorage.setItem('w2s.prefs',JSON.stringify(p)); }catch(e){}
    try{ if(window.gtag) gtag('event','pick_language',{lang:l,from:'story_link'}); }catch(e){}
    if(l==='te'){ o.remove(); return; }
    const u=new URL(location.href); u.searchParams.set('l',l); location.replace(u.toString());
  });
}
if(typeof document!=='undefined'){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',w2sAskLang); else w2sAskLang(); }

/* Story pages: always-visible language row at the top of the story (తెలుగు / English / हिन्दी) */
function w2sLangStrip(){
  try{
    const ar=document.querySelector('article.ar .in'); if(!ar || document.getElementById('w2sLs')) return;
    const cur=w2sLang();
    const L=[['te','తెలుగు'],['en','English'],['hi','हिन्दी']];
    const d=document.createElement('div'); d.id='w2sLs';
    d.style.cssText='display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 14px';
    d.innerHTML='<span style="font:700 13px/1 inherit;color:#6b6f80">🌐</span>'+L.map(([k,t])=>'<button type="button" data-l="'+k+'" aria-pressed="'+(k===cur)+'" style="min-height:36px;padding:0 16px;border-radius:999px;cursor:pointer;font:800 15px/1 inherit;border:2px solid '+(k===cur?'#4A0E3F;background:#4A0E3F;color:#fff':'#d8d2c6;background:#fff;color:#202124')+'">'+t+'</button>').join('');
    ar.insertBefore(d, ar.firstChild);
    d.querySelectorAll('button[data-l]').forEach(b=>b.onclick=()=>{
      const l=b.dataset.l;
      try{ const p=JSON.parse(localStorage.getItem('w2s.prefs')||'{}'); p.lang=l; localStorage.setItem('w2s.prefs',JSON.stringify(p)); }catch(e){}
      try{ if(window.gtag) gtag('event','pick_language',{lang:l,from:'story_strip'}); }catch(e){}
      const u=new URL(location.href); u.searchParams.set('l',l); location.replace(u.toString());
    });
  }catch(e){}
}
if(typeof document!=='undefined'){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',w2sLangStrip); else w2sLangStrip(); }

/* Website + story pages: tagline in the reader's language (user, 9 Nov 2026) —
   "Know More. Scroll Less." / "Know More. Scroll Less." / "कम स्क्रॉल, ज़्यादा जानकारी" */
const W2S_TAG={te:{tag:'Know More. Scroll Less.',l1:'ఒక్క స్వైప్‌లో వార్తలు!',sub:'తక్కువ స్క్రోల్, ఎక్కువ సమాచారం'},
  en:{tag:'Know More. Scroll Less.',l1:'News in one swipe!',sub:'Short news you can check'},
  hi:{tag:'कम स्क्रॉल, ज़्यादा जानकारी',l1:'एक स्वाइप में खबरें!',sub:'तेज़ और छोटी खबरें, आपकी भाषा में'}};
function w2sTagline(){
  try{ const l=w2sLang(); if(l==='te'||!W2S_TAG[l]) return; const T=W2S_TAG[l], te=W2S_TAG.te;
    document.querySelectorAll('.tagl').forEach(el=>{ const sm=el.querySelectorAll('small');
      if(el.firstChild&&el.firstChild.nodeType===3) el.firstChild.nodeValue=T.l1;
      if(sm[0]) sm[0].textContent=T.tag; if(sm[1]) sm[1].textContent=T.sub; });
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n;
    while((n=w.nextNode())){ if(n.nodeValue.includes(te.tag)) n.nodeValue=n.nodeValue.split(te.tag).join(T.tag); }
    if(document.title.includes(te.tag)) document.title=document.title.split(te.tag).join(T.tag).split(te.l1).join(T.l1);
  }catch(e){}
}
if(typeof document!=='undefined'){ if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',w2sTagline); else w2sTagline(); }
