#!/usr/bin/env python3
"""Swipe2News e-paper: turns one day's stories (archive/YYYY-MM-DD.json) and open jobs into a newspaper PDF.

usage:  python3 tools/epaper.py [NEWS-DATE] [ISSUE-DATE]
        NEWS-DATE  = the day whose stories go in (default: yesterday in India)
        ISSUE-DATE = the date printed on the paper and used for the files (default: today in India)
        The morning edition (5:30 am IST) carries the full previous day's news.
output: epaper/YYYY-MM-DD.pdf  (+ epaper/index.json listing all issues)

The PDF is locked against copying text and editing (it can be read and printed),
and every page carries the Swipe2News name, date and a faint watermark."""
import json, os, re, sys, html, datetime, secrets, threading, http.server, functools, socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
LAUNCH = datetime.date(2026, 10, 31)  # first Swipe2News issue
WEEK = ['సోమవారం', 'మంగళవారం', 'బుధవారం', 'గురువారం', 'శుక్రవారం', 'శనివారం', 'ఆదివారం']
MON = ['జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్', 'జులై', 'ఆగస్టు', 'సెప్టెంబర్', 'అక్టోబర్', 'నవంబర్', 'డిసెంబర్']
COLS = {'--c-election': '#B3400F', '--c-gov': '#1F6B3A', '--c-money': '#16406E', '--c-water': '#0B5CAD',
        '--c-power': '#5B3A8C', '--c-city': '#7A4A12', '--c-job': '#0F6E5C'}
import re as _re
def tidy(s):
    """clean Telugu text: single spaces, no space before punctuation, curly quotes"""
    s = str(s or '').replace('\u00a0', ' ')
    s = _re.sub(r'\s+', ' ', s).strip()
    s = _re.sub(r'\s+([,.;:!?)%])', r'\1', s)
    s = _re.sub(r'([(])\s+', r'\1', s)
    s = _re.sub(r"(^|[\s(])'", r'\1‘', s); s = s.replace("'", '’')
    s = _re.sub(r'(^|[\s(])"', r'\1“', s); s = s.replace('"', '”')
    return s
e = lambda s: html.escape(tidy(s), quote=False)


def secs(s):
    v = s.get('sec')
    return v if isinstance(v, list) else ([v] if v else ['telangana'])


def group(stories):
    """front page + section pages, each story used once"""
    order = sorted(stories, key=lambda s: (not s.get('brk'), s.get('t') or ''), reverse=False)
    order = sorted(stories, key=lambda s: (0 if s.get('brk') else 1, -(int((s.get('t') or '0:0').replace(':', '')))))
    used = set()
    take = lambda l, n: [x for x in l if id(x) not in used][:n]
    def mark(l):
        for x in l: used.add(id(x))
        return l
    front = mark(take(order, 4))
    stp = [s for s in order if (s.get('st') in (None, 'TG', 'AP') and 'telangana' in secs(s))]
    tg = take([s for s in stp if s.get('st') != 'AP'], 8); ap = take([s for s in stp if s.get('st') == 'AP'], 4)
    state = mark([x for pair in zip(tg, ap) for x in pair] + tg[len(ap):] + ap[len(tg):])  # Telangana and Andhra Pradesh, side by side (review 25 Nov 2026)
    india = mark(take([s for s in order if 'india' in secs(s)], 10))
    world = mark(take([s for s in order if 'world' in secs(s)], 10))
    def mix(l):  # round-robin by source: no page full of one paper's stories (review 25 Nov 2026)
        by = {}
        for x in l: by.setdefault(x.get('src') or '', []).append(x)
        out = []
        while any(by.values()):
            for k in list(by):
                if by[k]: out.append(by[k].pop(0))
        return out
    sport = mark(take([s for s in order if 'sports' in secs(s)], 8))
    hyd = lambda s: s.get('place') in ('hyderabad', 'rangareddy', 'medchal') or 'హైదరాబాద్' in (s.get('cat') or '')
    city = mark(mix(take([s for s in order if hyd(s)], 8)))
    local = lambda s: str(s.get('place') or '') not in ('', 'TS', 'AP', 'IN', 'hyderabad') and 'telangana' in secs(s)
    rest = mark(mix(take([s for s in order if local(s)], 14)))  # districts page: district news first
    rest += mark(mix(take([s for s in order if 'telangana' in secs(s)], 14 - len(rest))))
    return front, state, india, world, city, sport, rest


def ptime(s):
    m = re.search(r'T(\d\d:\d\d)', str(s.get('pub') or ''))
    return m.group(1) if m else (s.get('t') or '')


def own(s):
    return 'swipe2news' in str(s.get('src') or '').lower()


import difflib
_WHY = []
def stems(t):
    return {w[:4] for w in _re.findall(r'[\u0C00-\u0C7FA-Za-z0-9₹]+', str(t or '')) if len(w) >= 4}


def fit_pts(s):
    """drop bullet points that share no word with the story (review 25 Nov 2026: Bagel Fest carried liquor-shop bullets)"""
    pts = s.get('pts') or []
    base = stems(str(s.get('h')) + ' ' + str(s.get('p')) + ' ' + str(s.get('stat')) + ' ' + str(s.get('statl')))
    return pts if any(stems(p) & base for p in pts) else []


def fit_why(s):
    """one 'why it matters' line is not repeated for another story in the same paper"""
    w = str(s.get('why') or '').strip()
    if not w: return ''
    if any(difflib.SequenceMatcher(None, w, x).ratio() > 0.6 for x in _WHY): return ''
    _WHY.append(w); return w


def story(s, size='', lead=False):
    col = COLS.get(s.get('col'), '#2E0827')
    pts = ''.join(f'<li>{e(p)}</li>' for p in fit_pts(s))
    why = fit_why(s) if size not in ('small', 'mid') else ''
    art = f'<div class="scene" data-sid="{e(s["_k"])}" style="background:{col}"><span class="kick">{e(s.get("cat"))}</span><b class="big{' te' if any('ఀ' <= ch <= '౿' for ch in str(s.get('stat') or '')) else ''}">{e(s.get("stat"))}</b><i>{e(s.get("statl"))}</i></div>' if lead or size == 'mid' else ''
    brk = '<span class="brk">BREAKING</span>' if s.get('brk') else ''
    return f'''<article class="st {size}{' own' if own(s) else ''}" style="--c:{col}" data-sid="{e(s['_k'])}">{art}
  <div class="hd">{'' if (lead or size == 'mid') else f'<div class="kick2">{"📝 మా రిపోర్టర్ · " if own(s) else ""}{e(s.get("cat"))}</div>'}
  {f'<div class="fact"><b class="{"te" if any("ఀ" <= ch <= "౿" for ch in str(s.get("stat") or "")) else ""}">{e(s.get("stat"))}</b><i>{e(s.get("statl"))}</i></div>' if size == '' and s.get('stat') else ''}
  <h2>{brk}{e(s.get('h'))}</h2>
  <p class="p">{e(s.get('p'))}</p></div>
  {f'<ul class="pts">{pts}</ul>' if pts and size not in ('small', 'mid') else ''}
  {f'<p class="why"><b>ఎందుకు ముఖ్యం?</b> {e(why)}</p>' if why else ''}
  <p class="src">మూలం: {e(s.get('src'))}{(' · ' + e(ptime(s)) + ' గం.') if ptime(s) else ''}</p>
</article>'''


def page_head(title, color, date_te, pno):
    return f'<header class="ph" style="--c:{color}"><span class="pt">{title}</span><span class="pm"><b>జనధ్వని</b> · {date_te} · పేజీ {pno}</span></header>'


def quote_box(d, extra):
    """Daily good word in the masthead's free corner: extra.json "quote" {t, a} wins, else tools/quotes.json by date."""
    q = extra.get('quote')
    if not q:
        try: qs = json.load(open(os.path.join(ROOT, 'tools', 'quotes.json'), encoding='utf-8'))
        except Exception: qs = []
        q = qs[d.toordinal() % len(qs)] if qs else None
    if not q: return '<span class="sp"></span>'
    au = f'<i>– {e(q.get("a"))}</i>' if q.get('a') else ''
    return f'<div class="qbox"><b>✨ నేటి మంచి మాట</b><p>“{e(q.get("t"))}”</p>{au}</div>'


def build_html(iso, day, jobs, extra=None):
    extra = extra or {}
    _WHY.clear()
    d = datetime.date.fromisoformat(iso)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fillers; fill = fillers.build(iso)
    except Exception as ex:
        print('fillers skipped:', ex); fill = {'list': []}
    date_te = f'{d.day} {MON[d.month - 1]} {d.year}'
    wk = WEEK[d.weekday()]
    issue = (d - LAUNCH).days + 1
    stories = [dict(s, _k=str(i)) for i, s in enumerate(day.get('stories') or [])]
    front, state, india, world, city, sport, rest = group(stories)
    nums = [s for s in stories if s.get('stat')][:3]
    lead, sub = (front[0] if front else None), front[1:4]
    today = f'{d.day:02d}.{d.month:02d}.{d.year}'
    def jobrow(j):
        return f'<tr{" class=jt" if j.get("last") == today else ""}><td>{"<span class=jtb>ఈరోజే చివరి తేదీ</span>" if j.get("last") == today else ""}<b>{e(j.get("h"))}</b><small>{e(j.get("org"))}{(" · " + e(j.get("qual"))) if j.get("qual") else ""}</small></td><td class="n">{e(j.get("posts"))}</td><td class="n">{e(j.get("last") or j.get("loc") or "")}</td></tr>'
    jobs = sorted(jobs, key=lambda j: (j.get('last') or '99.99.9999')[6:] + (j.get('last') or '99.99')[3:5] + (j.get('last') or '99')[:2])
    pages = []
    # ---------- front page ----------
    pages.append(f'''<section class="page front">
 <div class="mast">
   <div class="mtop"><span>{wk}, {date_te}</span><span>సంపుటి 1 · సంచిక {issue}</span><span>హైదరాబాద్ · AI ఈ-పేపర్ · ఉచితం</span></div>
   <div class="mname"><img class="mk" src="/epaper/mark.png" alt=""><img class="nm" src="/epaper/janadhwani-name.png" alt="జనధ్వని – ప్రజల గొంతుక… ప్రతి ఊరి పలుకు · A SWIPE2NEWS Publication">{quote_box(d, extra)}</div>
   <div class="mbar"><span>📍 తెలంగాణ</span><span>ఆంధ్రప్రదేశ్</span><span>దేశం</span><span>ప్రపంచం</span><span>ఉద్యోగాలు</span><span class="r"></span></div>
 </div>
 <div class="fgrid">
   <div class="flead">{story(lead, 'lead', True) if lead else ''}</div>
   <aside class="fside">
     <div class="box nums"><h3>ఈరోజు సంఖ్యల్లో</h3>{''.join(f'<div class="num"><b class="{'te' if any('ఀ' <= ch <= '౿' for ch in str(s.get('stat') or '')) else ''}" style="color:{COLS.get(s.get("col"), "#2E0827")}">{e(s.get("stat"))}</b><span>{e(s.get("statl"))}</span></div>' for s in nums)}</div>
     <div class="box idx"><h3>ఈ సంచికలో</h3>
       <div><span>ముఖ్యాంశాలు & రాబోయే ఘట్టాలు</span><b data-p="high">2</b></div><div><span>రాష్ట్రం – తెలంగాణ, ఏపీ</span><b data-p="state">3</b></div><div><span>దేశం</span><b data-p="india">3</b></div><div><span>ప్రపంచం</span><b data-p="world">4</b></div><div><span>ఉద్యోగాలు</span><b data-p="jobs">5</b></div><div><span>హైదరాబాద్ నగరం</span><b data-p="city">6</b></div><div><span>క్రీడలు</span><b data-p="sport">7</b></div><div><span>జిల్లాలు · మరిన్ని వార్తలు</span><b data-p="rest">8</b></div>
       <p>ఈ సంచికలో <b class="nst">{len(stories)}</b> వార్తలు · {len(jobs)} ఉద్యోగ ప్రకటనలు</p></div>
   </aside>
 </div>
 <div class="fsub">{''.join(story(s, 'mid') for s in sub)}</div>
</section>''')
    # ---------- highlights of the day + what is coming up ----------
    def pick_high():
        want = extra.get('highlights') or []
        out = []
        for h in want:
            s = next((x for x in stories if x.get('h') == h or (isinstance(h, int) and x['_k'] == str(h))), None)
            if s and s not in out: out.append(s)
        if len(out) < 6:
            for s in sorted(stories, key=lambda s: (0 if s.get('brk') else 1, -(int((s.get('t') or '0:0').replace(':', ''))))):
                if s not in out: out.append(s)
                if len(out) >= 8: break
        return out[:8]
    high = pick_high()
    up = list(extra.get('upcoming') or [])
    def dd(j):
        try: return datetime.date(int(j['last'][6:]), int(j['last'][3:5]), int(j['last'][:2]))
        except Exception: return None
    soon = sorted([j for j in jobs if dd(j) and 0 <= (dd(j) - d).days <= 7], key=dd)[:6]
    def chip(when):
        m = re.match(r'(\d{1,2})\s+(\S+)', str(when or ''))
        return (m.group(1), m.group(2)) if m else ('', str(when or ''))
    hl = ''.join(f'''<li style="--c:{COLS.get(s.get('col'), '#2E0827')}"><b class="hn">{i + 1}</b><div><span class="hk">{e(s.get('cat'))}</span><h3>{e(s.get('h'))}</h3>{f'<p>{e(s.get("why"))}</p>' if s.get('why') else ''}</div></li>''' for i, s in enumerate(high))
    ul = ''.join(f'''<li><div class="dc"><b>{e(chip(u.get('when'))[0])}</b><small>{e(chip(u.get('when'))[1])}</small></div><div><h3>{e(u.get('what'))}</h3><p>{e(' · '.join(x for x in [u.get('when'), u.get('where')] if x))}</p>{f'<small class="us">మూలం: {e(u.get("src"))}</small>' if u.get('src') else ''}</div></li>''' for u in up[:8])
    jl = ''.join(f'''<li><b>{e(j.get('last'))}</b><span>{e(j.get('h'))}</span></li>''' for j in soon)
    pages.append(f'''<section class="page" data-p="high">{page_head('ముఖ్యాంశాలు · రాబోయే ఘట్టాలు', '#4A0E3F', date_te, 2)}
  <div class="hgrid">
    <div class="hbox"><h2 class="hh">⚡ ఈరోజు ముఖ్యాంశాలు</h2><ol class="hl">{hl}</ol></div>
    <div class="ubox"><h2 class="hh">📅 రాబోయే ముఖ్య ఘట్టాలు</h2>{f'<ol class="ul">{ul}</ol>' if ul else '<p class="none">రేపటి ముఖ్య ఘట్టాలు త్వరలో.</p>'}
      {f'<div class="jbox"><h3>⏰ చివరి తేదీ దగ్గర పడుతున్న ఉద్యోగాలు</h3><ul>{jl}</ul></div>' if jl else ''}</div>
  </div></section>''')
    # ---------- section pages ----------
    def sec_page(title, color, items, pno, key):
        if not items: return ''
        first, more = items[0], items[1:]
        return f'''<section class="page" data-p="{key}" style="--pc:{color}">{page_head(title, color, date_te, pno)}
  <div class="secopen">{story(first, 'lead', True)}</div>
  <div class="cols">{''.join(story(s) for s in more)}</div></section>'''
    pno = 3
    for title, color, items, key in [('రాష్ట్రం · తెలంగాణ & ఆంధ్రప్రదేశ్', '#1F6B3A', state, 'state'), ('దేశం', '#B3400F', india, 'india'), ('ప్రపంచం', '#5B3A8C', world, 'world')]:
        h = sec_page(title, color, items, pno, key)
        if h: pages.append(h); pno += 1
    # ---------- jobs ----------
    pages.append(f'''<section class="page" data-p="jobs">{page_head('ఉద్యోగాలు · Jobs', '#0F6E5C', date_te, pno)}
  <p class="jintro">ఈరోజు దరఖాస్తు చేయగలిగే ప్రభుత్వ, ప్రైవేట్ ఉద్యోగాలు. పూర్తి వివరాలు, అధికారిక లింకులు: <b>swipe2news.com/?jobs=1</b></p>
  <table class="jobs"><thead><tr><th>ఉద్యోగం</th><th class="n">పోస్టులు</th><th class="n">చివరి తేదీ</th></tr></thead><tbody>{''.join(jobrow(j) for j in jobs[:22])}{''.join(jobrow(j).replace('<tr>', '<tr class="jx">', 1) for j in jobs[22:45])}</tbody></table>
  <p class="warn">⚠️ ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి. అధికారిక వెబ్‌సైట్‌లోనే దరఖాస్తు చేయండి.</p></section>''')
    pno += 1
    # ---------- Hyderabad city, sports (review 25 Nov 2026: named pages, not four "more news" pages) ----------
    for title, color, items, key in [('హైదరాబాద్ నగరం', '#7A4A12', city, 'city'), ('క్రీడలు', '#0B5CAD', sport, 'sport')]:
        if items:
            pages.append(f'''<section class="page" data-p="{key}" style="--pc:{color}">{page_head(title, color, date_te, pno)}
  <div class="cols">{''.join(story(x) for x in items)}</div></section>''')
            pno += 1
    # ---------- districts + more news + back cover ----------
    pages.append(f'''<section class="page" data-p="rest" style="--pc:#2E0827">{page_head('జిల్లాలు · మరిన్ని వార్తలు', '#2E0827', date_te, pno)}
  <div class="cols" data-rest="1">{''.join(story(s, 'small') for s in rest)}</div>
  <div class="back">
    <img src="/qr.png" alt="">
    <div><h3>ప్రతి 30 నిమిషాలకు తాజా వార్తలు – మీ ఫోన్‌లోనే</h3>
      <p>మా WhatsApp ఛానెల్‌లో చేరండి · యాప్: <b>swipe2news.com</b></p>
      <p>📝 మీ ఊరి వార్త పంపండి – పరిశీలించి ప్రపంచానికి చేరుస్తాం.</p>
      <p class="fine">ఈ ఈ-పేపర్‌లోని వార్తలు AI సహాయంతో మా మాటల్లో రాసినవి; ప్రతి వార్తకు మూలం పేర్కొన్నాం. © {d.year} జనధ్వని. అనుమతి లేకుండా పునఃప్రచురణ, కాపీ నిషిద్ధం.</p></div>
  </div></section>''')
    return f'''<!doctype html><html lang="te"><head><meta charset="utf-8"><title>జనధ్వని ఈ-పేపర్ – {date_te}</title>
<style>
@font-face{{font-family:W2Rama;src:url(/tools/fonts/Ramabhadra-Regular.ttf)}}
@font-face{{font-family:W2Serif;src:url(/tools/fonts/NotoSerifTelugu.ttf);font-weight:100 900}}
@font-face{{font-family:W2Sans;src:url(/tools/fonts/NotoSansTelugu.ttf);font-weight:100 900}}
@font-face{{font-family:W2Disp;src:url(/tools/fonts/Outfit-ExtraBold.ttf)}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#fff;color:#1A1410;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:210mm;height:297mm;padding:11mm 11mm 14mm;position:relative;overflow:hidden;break-after:page;background:#FFFFFF}}
.page::after{{content:"జనధ్వని · {date_te} · A SWIPE2NEWS Publication";position:absolute;left:11mm;right:11mm;bottom:0;font:600 7pt/1 W2Sans;color:#8A7E70;z-index:5;background:#fff;
  border-top:.6pt solid #CFC4B2;padding:2.2mm 0 6mm;letter-spacing:.3pt}}
.page::before{{content:"జనధ్వని";position:absolute;left:50%;top:52%;transform:translate(-50%,-50%) rotate(-30deg);font:400 120pt/1 W2Rama;color:rgba(200,16,46,.018);pointer-events:none;white-space:nowrap}}
/* masthead */
.mast{{border-bottom:2.4pt solid #2E0827;margin-bottom:4mm}}
.mtop{{display:flex;justify-content:space-between;font:700 7.6pt/1.4 W2Sans;color:#fff;background:#4A0E3F;padding:1.6mm 4mm;border-radius:1.2mm 1.2mm 0 0}}
.mname{{display:grid;grid-template-columns:auto 1fr 42mm;gap:3mm;align-items:center;padding:3mm 0 2.5mm}}
.qbox{{justify-self:end;width:42mm;background:#FFF8E6;border:.6pt solid #E8C77A;border-top:2pt solid #4A0E3F;border-radius:1.5mm;padding:2mm 2.6mm}}
.qbox b{{display:block;font:800 7.4pt/1.3 W2Sans;color:#4A0E3F;margin-bottom:.8mm}} .qbox p{{margin:0;font:600 8.2pt/1.55 W2Sans;color:#14100C}} .qbox i{{display:block;font:700 6.8pt/1.3 W2Sans;font-style:normal;color:#7A6E60;margin-top:.8mm;text-align:right}}
.mname .mk{{height:33mm;justify-self:start}} .mname .nm{{height:33mm;max-width:100%;object-fit:contain;justify-self:center}}
.mbar{{display:flex;gap:0;background:#2E0827;color:#fff;font:700 8pt/1.3 W2Sans;padding:0;margin-bottom:.8mm;overflow:hidden;border-radius:0 0 1.2mm 1.2mm}} .mbar span{{padding:2.2mm 3.6mm}}
.mbar span:nth-child(1){{background:#1F6B3A}} .mbar span:nth-child(2){{background:#0B5CAD}} .mbar span:nth-child(3){{background:#B3400F}} .mbar span:nth-child(4){{background:#5B3A8C}} .mbar span:nth-child(5){{background:#0F6E5C}} .mbar .r{{margin-left:auto;color:#F5A23A}}
/* stories */
.st{{break-inside:avoid;margin:0 0 4mm}}
.st h2{{font:400 13pt/1.45 W2Rama;margin:1mm 0 1.5mm;color:#14100C;text-wrap:balance}}
.st .p{{font:400 8.8pt/1.8 W2Serif;margin:0 0 1.6mm;text-align:left;word-spacing:normal;hyphens:none}}
.kick2{{font:800 6.8pt/1.4 W2Sans;color:#fff;background:var(--pc,var(--c));border-radius:.8mm;padding:.6mm 2.2mm;display:inline-block}}
.fact{{display:flex;align-items:baseline;gap:2.5mm;background:color-mix(in srgb,var(--c) 10%,#fff);border-left:2.4pt solid var(--c);border-radius:0 1.5mm 1.5mm 0;padding:1.6mm 2.5mm;margin:1.4mm 0 1.6mm}}
.fact b{{font:400 15pt/1.1 W2Disp;color:var(--c);white-space:nowrap}} .fact b.te{{font:400 13pt/1.3 W2Rama}} .fact i{{font:700 7.2pt/1.4 W2Sans;font-style:normal;color:#3B332B}}
.pts{{margin:0 0 1.6mm;padding-left:4mm;font:600 8pt/1.65 W2Sans}} .pts li::marker{{color:var(--c)}}
.why{{font:500 7.8pt/1.65 W2Sans;margin:0 0 1.5mm;background:#F2F4F7;border-left:2pt solid var(--c);padding:1.5mm 2.5mm}} .why b{{color:var(--c)}}
.src{{font:600 6.8pt/1.4 W2Sans;color:#7A6E60;margin:0}} .st.own .kick2{{background:#1F6B3A}}
.pic{{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;border-radius:1.5mm;margin:0 0 2mm}} .pcap{{display:block;font:600 5.8pt/1.2 W2Sans;color:#9A8E80;margin:-1.4mm 0 1.6mm}}
.brk{{display:inline-block;background:#4A0E3F;color:#fff;font:800 7pt/1 W2Sans;padding:1mm 2mm;border-radius:1mm;margin-right:2mm;vertical-align:middle}}
.scene{{position:relative;height:46mm;border-radius:2mm;overflow:hidden;color:#fff;padding:4mm 5mm;display:flex;flex-direction:column;justify-content:flex-end;margin-bottom:2.5mm}}
.scene svg{{position:absolute;inset:0;width:100%;height:100%;opacity:.3}}
.scene>*{{position:relative}}
.scene .scimg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}} .scene .scsh{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05) 30%,rgba(0,0,0,.72))}} .scene .scai{{position:absolute;right:3mm;bottom:2mm;font:600 5.6pt/1 W2Sans;color:rgba(255,255,255,.8)}}
.scene .kick{{position:absolute;top:3.5mm;left:5mm;border:.8pt solid rgba(255,255,255,.85);border-radius:10mm;padding:.8mm 3mm;font:800 7pt/1.4 W2Sans}}
.scene .big{{font:400 30pt/1 W2Disp}} .scene .big.te{{font:400 26pt/1.15 W2Rama}} .scene i{{font:700 9pt/1.3 W2Sans;font-style:normal;opacity:.95;margin-top:1mm}}
.st.lead h2{{font-size:21pt;line-height:1.4}} .st.lead .p{{font-size:9.8pt;line-height:1.85}}
.st.mid .scene{{height:30mm}} .st.mid .scene .big{{font-size:20pt}} .st.mid h2{{font-size:12pt}}
.st.small h2{{font-size:11pt}} .st.small .p{{font-size:8.2pt}} .st.small .pts,.st.small .why{{display:none}}
/* front grid */
.fgrid{{display:grid;grid-template-columns:1fr 52mm;gap:5mm;border-bottom:.8pt solid #CFC4B2;margin-bottom:4mm}}
.fside{{display:grid;gap:4mm;align-content:start}}
.box{{border:0;border-radius:2mm;padding:3mm;background:#F1F5FB;border-top:2.4pt solid #0B5CAD}} .box.idx{{background:#FFF6E0;border-top-color:#4A0E3F}}
.box h3{{margin:0 0 2.5mm;font:400 11pt/1 W2Rama;color:#2E0827}}
.num{{display:grid;border-top:.6pt dashed #DDD3C4;padding:1.8mm 0}} .num b{{font:400 15pt/1.1 W2Disp}} .num b.te{{font:400 14pt/1.2 W2Rama}} .num span{{font:600 7.2pt/1.35 W2Sans;color:#3B332B}}
.idx div{{display:flex;justify-content:space-between;font:700 7.8pt/1.35 W2Sans;border-top:.6pt dashed #DDD3C4;padding:1.2mm 0}} .idx b{{color:#4A0E3F}} .idx p{{font:600 7pt/1.4 W2Sans;color:#7A6E60;margin:2mm 0 0}}
.fsub{{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}}
/* inner pages */
.ph{{display:flex;justify-content:space-between;align-items:center;background:var(--c);border-radius:1.5mm;padding:2.2mm 4mm;margin-bottom:4mm;box-shadow:inset 0 -1.2mm 0 rgba(0,0,0,.18)}}
.pt{{font:400 18pt/1.3 W2Rama;color:#fff}} .pm{{font:600 7.4pt/1.3 W2Sans;color:rgba(255,255,255,.9)}} .pm b{{font:400 11pt/1 W2Rama;color:#F5A23A}}
.secopen .scene{{height:52mm}} .secopen .scene:not(.photo){{height:30mm}} .fsub .scene:not(.photo){{height:24mm}} .scene.sm .kick{{display:none}}
.secopen{{border-bottom:.8pt solid #CFC4B2;margin-bottom:4mm}}
.cols{{column-count:3;column-gap:5mm;column-rule:.6pt solid #E0D6C6;column-fill:auto}}
.cols .st{{break-inside:auto}} .cols .st .hd{{break-inside:avoid}} .cols.bal .st{{break-inside:avoid}} .cols .st .src{{break-before:avoid}} .cols .st .why{{break-before:avoid}} .cols .st:nth-child(3n+2){{background:color-mix(in srgb,var(--c) 6%,#fff);border-top:2pt solid var(--c);padding:2mm 2.5mm;border-radius:1.5mm}} .cols .st h2{{color:#2E0827}} .cols .st:nth-child(3n+2) h2{{color:color-mix(in srgb,var(--c) 75%,#000)}} .st h2,.kick2{{break-after:avoid}} .why,.pts li,.src{{break-inside:avoid}} .cols .st .p{{orphans:3;widows:3}}
.jintro{{font:600 9pt/1.5 W2Sans;margin:0 0 3mm}}
.hgrid{{display:grid;grid-template-columns:1.15fr 1fr;gap:6mm;height:calc(100% - 22mm)}}
.hh{{font:400 15pt/1.35 W2Rama;margin:0 0 3mm;color:#2E0827;border-bottom:1.6pt solid #2E0827;padding-bottom:1.5mm}}
.hl{{list-style:none;margin:0;padding:0;display:grid;gap:3.2mm}}
.hl li{{display:grid;grid-template-columns:11mm 1fr;gap:3mm;align-items:start;border-bottom:.6pt dashed #DDD3C4;padding-bottom:3mm}}
.hn{{font:400 15pt/1 W2Disp;color:#fff;background:var(--c);border-radius:50%;width:10mm;height:10mm;display:flex;align-items:center;justify-content:center}}
.hk{{font:800 6.8pt/1.4 W2Sans;color:var(--c)}}
.hl h3{{font:400 11.6pt/1.45 W2Rama;margin:.6mm 0 1mm;color:#14100C}}
.hl p{{font:500 7.8pt/1.6 W2Sans;margin:0;color:#4A4036}}
.ubox{{background:#F3F5F8;border-radius:3mm;padding:4mm;border-top:2.4pt solid #4A0E3F}}
.ul{{list-style:none;margin:0;padding:0;display:grid;gap:3mm}}
.ul li{{display:grid;grid-template-columns:15mm 1fr;gap:3mm;align-items:start;background:#fff;border-radius:2mm;padding:2.5mm;box-shadow:0 .6mm 2mm rgba(18,40,74,.08)}}
.dc{{background:#2E0827;color:#fff;border-radius:2mm;text-align:center;padding:1.8mm 1mm;display:grid}}
.dc b{{font:400 15pt/1 W2Disp;color:#F5A23A}} .dc small{{font:700 6.6pt/1.4 W2Sans}}
.ul h3{{font:400 10.4pt/1.45 W2Rama;margin:0 0 1mm;color:#14100C}} .ul p{{font:600 7.4pt/1.5 W2Sans;margin:0;color:#4A4036}} .us{{font:600 6.4pt/1.4 W2Sans;color:#7A6E60}}
.none{{font:600 9pt/1.6 W2Sans;color:#6B5F52}}
.jbox{{margin-top:4mm;border-top:1.2pt solid #0F6E5C;padding-top:2.5mm}} .jbox h3{{font:400 11pt/1.4 W2Rama;color:#0F6E5C;margin:0 0 2mm}}
.jbox ul{{list-style:none;margin:0;padding:0;display:grid;gap:1.6mm}} .jbox li{{display:grid;grid-template-columns:19mm 1fr;gap:2mm;font:600 7.6pt/1.5 W2Sans}} .jbox li b{{color:#B3400F}}
table.jobs{{width:100%;border-collapse:collapse;font:600 8pt/1.4 W2Sans}}
table.jobs th{{background:#0F6E5C;color:#fff;text-align:left;padding:2mm 2.5mm;font-weight:800}}
table.jobs td{{border-bottom:.6pt solid #DDD3C4;padding:1.8mm 2.5mm;vertical-align:top}}
table.jobs tr:nth-child(even) td{{background:#F3F5F8}} table.jobs tr.jx{{display:none}} table.jobs tr.jt td{{background:#FFF1E6!important}} .jtb{{display:inline-block;background:#B3400F;color:#fff;font:800 6.4pt/1.3 W2Sans;border-radius:.8mm;padding:.3mm 1.6mm;margin:0 1.6mm .6mm 0}}
table.jobs td small{{display:block;color:#6B5F52;font-weight:600;font-size:7pt}}
table.jobs .n{{text-align:right;white-space:nowrap;width:24mm}}
.warn{{font:800 8.6pt/1.5 W2Sans;color:#B3400F;margin:3mm 0 0}}
.frow{{position:absolute;left:11mm;right:11mm;display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;align-items:start}} .frow.fewer{{justify-content:center;grid-template-columns:repeat(auto-fit,minmax(0,calc((100% - 10mm)/3)))}}
.fcell{{min-width:0}}
.fm{{break-inside:avoid;margin:3mm 0 0;padding:2.6mm 0 0;border-top:1.6pt solid #4A0E3F;font:500 8pt/1.6 W2Sans;color:#1A1410}}
.fcell .fm{{margin-top:0}}
.fmh{{display:flex;align-items:center;gap:1.6mm;margin:0 0 1.8mm}} .fmh i{{width:2.2mm;height:2.2mm;background:#F5A23A;border-radius:.4mm}} .fmh span{{font:400 11pt/1.3 W2Rama;color:#4A0E3F}}
.fmf{{font:600 6.4pt/1.4 W2Sans;color:#7A6E60;margin-top:1.4mm}}
.fm h4{{font:400 10.5pt/1.4 W2Rama;margin:0 0 .8mm;color:#14100C}} .fm p{{margin:0 0 1.2mm}}
.fq{{font:400 10.5pt/1.6 W2Serif;color:#2E0827}} .fqa{{text-align:right;font:700 7.4pt/1.4 W2Sans;color:#7A6E60}}
.fpv{{margin:0 0 1.6mm}} .fpv b{{display:block;font:400 10pt/1.45 W2Rama;color:#4A0E3F}} .fpv span{{font:500 7.8pt/1.55 W2Sans;color:#3B332B}}
.fdate{{font:400 12pt/1.3 W2Rama;color:#B3400F;margin:0 0 1mm!important}} .fev{{font:500 8pt/1.6 W2Sans;border-bottom:.5pt dotted #D9CDBE;padding-bottom:1mm}}
.fht b{{display:block;font:800 8pt/1.4 W2Sans;color:#4A0E3F}}
.fhl{{display:grid;grid-template-columns:1fr 1fr;gap:.8mm 2mm;margin-top:1mm;border-top:.5pt solid #E4D9CB;padding-top:1.2mm}} .fhl span{{display:flex;justify-content:space-between;font:600 6.8pt/1.4 W2Sans;color:#3B332B}} .fhl b{{color:#B3400F}}
.fgk{{margin:0;padding-left:4mm;font:500 8pt/1.55 W2Sans}} .fgk li{{margin-bottom:1mm}} .fgk li::marker{{color:#F5A23A;font-weight:800}}
.fans{{transform:rotate(180deg);font:600 6.4pt/1.4 W2Sans;color:#8A7E70;margin-top:1.4mm!important;border-top:.5pt solid #E4D9CB;padding-top:1mm}}
.ffc{{font:400 8.4pt/1.65 W2Serif;padding-left:2.4mm;border-left:1.6pt solid #F5A23A}}
.fhr{{margin-bottom:1.6mm}} .fhr small{{display:block;font:700 6.8pt/1.3 W2Sans;color:#7A6E60;margin-bottom:.6mm}} .fhr p{{font:400 8pt/1.6 W2Serif}}
.fsd{{font:500 7pt/1.45 W2Sans;color:#4A4036}}
table.sdk{{border-collapse:collapse;margin:1.4mm auto 0;border:1.2pt solid #2E0827}} table.sdk td{{width:5.6mm;height:5.6mm;border:.4pt solid #B9AE9F;text-align:center;font:400 9pt/1 W2Disp;color:#2E0827;padding:0}}
table.sdk.n6 td{{width:7mm;height:7mm}} table.sdk td.bR{{border-right:1.2pt solid #2E0827}} table.sdk td.bB{{border-bottom:1.2pt solid #2E0827}}
table.fmt{{width:100%;border-collapse:collapse;font:600 7.6pt/1.35 W2Sans}} table.fmt th{{text-align:left;font:800 6.6pt/1.3 W2Sans;color:#7A6E60;border-bottom:.8pt solid #4A0E3F;padding:.6mm 0}}
table.fmt td{{border-bottom:.5pt solid #E4D9CB;padding:1mm 0;vertical-align:top}} table.fmt td small{{display:block;font-weight:500;font-size:6.4pt;color:#7A6E60}} table.fmt .n{{text-align:right;white-space:nowrap}} table.fmt td.n{{font:400 9pt/1.2 W2Disp;color:#2E0827}}
.fm.pr{{background:#FBF6EE;border-top-color:#F5A23A;padding:2.6mm 2.6mm 2mm}} .fm .fct{{font:700 7.4pt/1.4 W2Sans;color:#4A0E3F}}
.fqr{{display:flex;gap:2.4mm;align-items:center}} .fqr img{{width:17mm;height:17mm;background:#fff;padding:.6mm;flex:none}}
.fch{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.6mm}} .fch figure{{margin:0;text-align:center}} .fch svg{{width:100%;height:auto}} .fch figcaption{{font:700 6.4pt/1.3 W2Sans}}
.fm.paid{{border:.8pt solid #4A0E3F;border-top-width:1.6pt;padding:2.4mm}} .fadimg{{width:100%;height:auto;margin-bottom:1.4mm}} .fadv{{display:block;font:600 6pt/1.3 W2Sans;color:#8A7E70}}
.hab{{position:absolute;left:11mm;right:11mm;display:flex;gap:5mm;align-items:center;justify-content:center;border:1.2pt dashed #C9A9BE;border-radius:3mm;background:#FBF4F8;padding:4mm 6mm;overflow:hidden}}
.hab.col{{position:static;flex-direction:column;text-align:center;margin-top:3mm;break-inside:avoid;padding:3mm}} .hab.col .hx{{max-width:none}}
.hab img{{width:24mm;height:24mm;background:#fff;padding:1mm;border-radius:1.5mm;flex:none}} .hab .hx{{max-width:120mm}}
.hab h3{{margin:0 0 1.5mm;font:400 15pt/1.35 W2Rama;color:#2E0827}} .hab p{{margin:0 0 1mm;font:600 8.6pt/1.55 W2Sans;color:#3B2A35}} .hab b{{color:#B3400F}}
.hab .em{{font-size:26pt;line-height:1}} .hab.sm h3{{font-size:12pt}} .hab.sm img{{width:16mm;height:16mm}} .hab.sm .em{{font-size:18pt}}
.back{{position:absolute;left:11mm;right:11mm;bottom:16mm;display:flex;gap:6mm;align-items:center;background:#2E0827;color:#fff;border-radius:3mm;padding:5mm}}
.back.slim{{padding:2mm 4mm;gap:3mm;bottom:15mm}} .back.slim img{{width:11mm;height:11mm;padding:.6mm}} .back.slim h3{{font-size:10pt;margin:0}} .back.slim p{{display:none}}
.back img{{width:30mm;height:30mm;background:#fff;padding:1.5mm;border-radius:1.5mm}}
.back h3{{margin:0 0 2mm;font:400 14pt/1.3 W2Rama;color:#F5A23A}} .back p{{margin:0 0 1.5mm;font:600 8.4pt/1.5 W2Sans}} .back .fine{{font-size:6.8pt;color:#B9C4D6;margin:2mm 0 0}}
</style></head><body>{''.join(pages)}
<script src="/scenes.js"></script>
<script>window.FILL={json.dumps(fill, ensure_ascii=False)};const S={json.dumps(stories, ensure_ascii=False)};
document.querySelectorAll('.page:not(:has(.secopen)) .cols').forEach(c=>{{ for(const st of c.querySelectorAll('.st')){{ const s=S.find(x=>x._k===st.dataset.sid); let a=null; try{{ a=s&&artPlan(s); }}catch(e){{}}
  if(a&&a.bg){{ const h=st.querySelector('h2'); if(h) h.insertAdjacentHTML('beforebegin','<img class="pic" src="'+artBg(a.bg)+'" alt=""><small class="pcap">AI రూపొందించిన చిత్రం</small>'); break; }} }} }});
document.querySelectorAll('.scene[data-sid]').forEach(el=>{{ const s=S.find(x=>x._k===el.dataset.sid); if(!s) return; let a=null; try{{ a=artPlan(s); }}catch(e){{}}
  if(a&&a.bg){{ el.classList.add('photo'); el.insertAdjacentHTML('afterbegin','<img class="scimg" src="'+artBg(a.bg)+'" alt=""><i class="scsh"></i><small class="scai">AI రూపొందించిన చిత్రం</small>'); }}
  else if(!a||a.m!=='logo') el.insertAdjacentHTML('afterbegin', sceneSVG(s,'ep')); }});
{FIT_JS}</script></body></html>'''


FIT_JS = r'''/* fit every page: stories that do not fit move to a continuation page, nothing is cut */
const MM=96/25.4;
async function fit(){ await document.fonts.ready; let changed=true, guard=0;
  // the QR back box goes on the last page at the end, so no page keeps a hole where it used to be (review 25 Nov 2026)
  const BACK=document.querySelector('.back'), BH=BACK?BACK.offsetHeight:0; if(BACK) BACK.remove();
  while(changed && guard++<30){ changed=false;
    for(const pg of [...document.querySelectorAll('.page')]){ const c=pg.querySelector('.cols'); if(!c||c.dataset.fit) continue;
      const back=pg.querySelector('.back'); const pr=pg.getBoundingClientRect();
      const limit=(back?back.getBoundingClientRect().top-4*MM:pr.bottom-16*MM);
      c.style.height=Math.max(40,limit-c.getBoundingClientRect().top)+'px'; c.dataset.fit=1;
      const moved=[]; while(c.scrollWidth>c.clientWidth+2 && c.children.length>1){ moved.unshift(c.lastElementChild); c.lastElementChild.remove(); }
      const rest=document.querySelector('.cols[data-rest]');
      if(moved.length && ['india','world'].includes(pg.dataset.p)){ changed=true; break; }
      if(moved.length && rest && c!==rest && !c.closest('.page.cont')){ moved.reverse().forEach(m=>{ m.classList.add('small'); rest.insertBefore(m,rest.firstChild); });
        delete rest.dataset.fit; rest.style.height=''; changed=true; break; }
      if(moved.length){ const np=document.createElement('section'); np.className='page cont'; const ph=pg.querySelector('.ph');
        np.innerHTML=(ph?ph.outerHTML:'')+'<div class="cols"></div>'; const t=np.querySelector('.pt'); if(t&&!/కొనసాగింపు/.test(t.textContent)) t.textContent+=' (కొనసాగింపు)';
        moved.forEach(m=>np.querySelector('.cols').appendChild(m)); (back?pg:pg).after(np); changed=true; break; } } }
  // last page of each section: spread the stories evenly over the 3 columns (no half-empty last column)
  document.querySelectorAll('.page .cols').forEach(c=>{ const pg=c.closest('.page'), nx=pg.nextElementSibling;
    if(nx && nx.classList.contains('cont')) return; const h=c.style.height; c.style.height=''; c.style.columnFill='balance'; c.classList.add('bal');
    const pr=pg.getBoundingClientRect(), lim=pr.bottom-16*MM;
    if(c.scrollWidth>c.clientWidth+2 || c.getBoundingClientRect().bottom>lim){ c.style.height=h; c.style.columnFill=''; c.classList.remove('bal'); } });
  // nothing may run under the footer line (review 25 Nov 2026: front teasers, jobs-closing list, last jobs row)
  const over=(pg)=>{ const lim=pg.getBoundingClientRect().bottom-13*MM; return [...pg.querySelectorAll('.fsub .st, .jbox li, .hl li, .ul li, table.jobs tr, .warn')].some(x=>x.offsetParent&&x.getBoundingClientRect().bottom>lim); };
  document.querySelectorAll('.page').forEach(pg=>{
    for(const n of ['L58mm','L48mm','24mm',3,'L40mm',2,0]){ if(!over(pg)) break; if(typeof n==='string'){ if(n[0]==='L') pg.querySelectorAll('.flead .scene').forEach(x=>x.style.height=n.slice(1)); else pg.querySelectorAll('.fsub .scene').forEach(x=>{ x.style.height=n; x.classList.add('sm'); }); continue; }
      pg.querySelectorAll('.fsub .p').forEach(p=>{ if(n){ p.style.cssText='display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;-webkit-line-clamp:'+n; } else p.style.display='none'; }); }
    let g=0; while(over(pg) && g++<60){ const x=[...pg.querySelectorAll('.jbox li, .ul li, table.jobs tbody tr:not(.jx)')].pop(); if(!x) break; if(x.tagName==='TR') x.classList.add('jx'); else x.remove(); } });
  let pgs=[...document.querySelectorAll('.page')], last=pgs[pgs.length-1]; const back=BACK;
  // jobs page: show more jobs until the page is full
  document.querySelectorAll('table.jobs').forEach(t=>{ const pg=t.closest('.page'), lim=pg.getBoundingClientRect().bottom-34*MM;
    for(const r of t.querySelectorAll('tr.jx')){ r.classList.remove('jx'); if(t.getBoundingClientRect().bottom>lim){ r.classList.add('jx'); break; } } });
  if(back && last){ const cs=[...last.querySelectorAll('.cols > *')], bot=cs.length?Math.max(...cs.map(x=>x.getBoundingClientRect().bottom)):last.getBoundingClientRect().top+40*MM;
    const room=last.getBoundingClientRect().bottom-16*MM-bot; if(room>BH+8*MM){ last.appendChild(back); }
    else if(room>17*MM){ back.classList.add('slim'); last.appendChild(back); } // little room: one slim line, never an extra page for the box alone
    pgs=[...document.querySelectorAll('.page')]; }
  // white space (user, 25 Nov 2026): measured on every page after the news is placed, then filled from the
  // day's module library (tools/fillers.json via tools/fillers.py). Paid ads first, no module twice, few promos, small gaps left alone.
  const F=window.FILL||{list:[]}, used=new Set(); let promos=0;
  const take=(hmax, tryIn)=>{ for(const m of F.list){ if(used.has(m.k)) continue; if(m.promo&&promos>=F.max_promos) continue;
      for(const v of m.v){ const el=tryIn(v); if(el){ used.add(m.k); if(m.promo) promos++; return el; } } } return null; };
  document.querySelectorAll('.page').forEach(pg=>{ const c=pg.querySelector('.cols'); if(!c||!c.children.length) return;
    const pr=pg.getBoundingClientRect(), bk=pg.querySelector('.back');
    const lim=bk?bk.getBoundingClientRect().top-4*MM:pr.bottom-16*MM;
    // a) columns filled one after another: space at the foot of the last column
    const lastEl=c.lastElementChild, lr=[...lastEl.getClientRects()].pop(), cb=c.getBoundingClientRect().bottom;
    if(!c.classList.contains('bal') && lr && cb-lr.bottom>F.min_col_mm*MM){
      take(0, v=>{ const w=document.createElement('div'); w.className='fslot'; w.innerHTML=v; const el=w.firstElementChild; c.appendChild(el);
        if(c.scrollWidth>c.clientWidth+2 || el.getBoundingClientRect().bottom>cb+1){ el.remove(); return null; } return el; });
      return; }
    // b) balanced columns: a row of up to three column-wide modules in the space under them
    const bot=Math.max(...[...c.querySelectorAll(':scope > *')].map(x=>{ const rs=[...x.getClientRects()]; return rs.length?Math.max(...rs.map(q=>q.bottom)):0; }));
    const room=lim-bot-5*MM; if(room<F.min_row_mm*MM) return;
    const row=document.createElement('div'); row.className='frow'; row.style.top=(bot-pr.top+5*MM)+'px'; row.style.height=room+'px'; pg.appendChild(row);
    for(let k=0;k<3;k++){ const slot=document.createElement('div'); slot.className='fcell'; row.appendChild(slot);
      const el=take(0, v=>{ slot.innerHTML=v; const e=slot.firstElementChild; if(e.getBoundingClientRect().bottom>row.getBoundingClientRect().bottom+1){ slot.innerHTML=''; return null; } return e; });
      if(!el){ slot.remove(); break; } }
    if(!row.children.length) row.remove(); else if(row.children.length<3) row.classList.add('fewer'); });
  document.querySelectorAll('.nst').forEach(b=>b.textContent=new Set([...document.querySelectorAll('.st h2')].map(h=>h.textContent.trim())).size);
  document.querySelectorAll('.idx b[data-p]').forEach(b=>{ const i=pgs.findIndex(p=>p.dataset.p===b.dataset.p); if(i>=0) b.textContent=i+1; else b.parentNode.remove(); });
  document.querySelectorAll('.page').forEach((pg,i)=>{ const pm=pg.querySelector('.pm'); if(pm) pm.innerHTML=pm.innerHTML.replace(/పేజీ \d+/,'పేజీ '+(i+1)); });
  document.body.dataset.ready='1'; }
fit();'''


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


def serve():
    h = functools.partial(Quiet, directory=ROOT)
    srv = socketserver.TCPServer(('127.0.0.1', 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    today = datetime.datetime.now(IST).date()
    news_iso = sys.argv[1] if len(sys.argv) > 1 else (today - datetime.timedelta(days=1)).isoformat()
    iso = sys.argv[2] if len(sys.argv) > 2 else (news_iso if len(sys.argv) > 1 else today.isoformat())
    day = json.load(open(os.path.join(ROOT, 'archive', news_iso + '.json'), encoding='utf-8'))
    d0 = datetime.date.fromisoformat(iso); day = dict(day, date=f'{d0.day:02d}.{d0.month:02d}.{d0.year}')
    try: jobs = json.load(open(os.path.join(ROOT, 'jobs.json'), encoding='utf-8')).get('jobs', [])
    except Exception: jobs = []
    out_dir = os.path.join(ROOT, 'epaper'); os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(ROOT, 'epaper', '_build.html')
    try: extra = json.load(open(os.path.join(ROOT, 'epaper', iso + '.extra.json'), encoding='utf-8'))
    except Exception: extra = {}
    open(tmp, 'w', encoding='utf-8').write(build_html(iso, day, jobs, extra))
    srv = serve()
    from playwright.sync_api import sync_playwright
    raw = os.path.join(out_dir, '_raw.pdf')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 820, 'height': 1200}, device_scale_factor=2)
        pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/epaper/_build.html'); pg.wait_for_selector('body[data-ready="1"]')
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        # page pictures + where each story sits on the page (for the web viewer and its ✂️ clip tool)
        day_dir = os.path.join(out_dir, iso); os.makedirs(day_dir, exist_ok=True)
        info = pg.evaluate('''() => [...document.querySelectorAll('.page')].map(pg => { const r = pg.getBoundingClientRect();
          const clips = [...pg.querySelectorAll('.st, table.jobs, .hbox, .ubox')].map(el => { const rs = [...el.getClientRects()].filter(q => q.width > 20 && q.height > 10);
            return rs.map(q => ({x: (q.left - r.left) / r.width, y: (q.top - r.top) / r.height, w: q.width / r.width, h: q.height / r.height,
              t: (el.querySelector('h2') || {}).textContent || 'ఉద్యోగాలు'})); }).flat();
          const ttl = (pg.querySelector('.pt') || {}).textContent || 'మొదటి పేజీ';
          return {title: ttl, clips}; })''')
        pages_meta = []; stamp = datetime.datetime.now(IST).strftime('%H%M%S')
        for i, m in enumerate(info):
            fn = f'p{i + 1}.jpg'
            pg.locator('.page').nth(i).screenshot(path=os.path.join(day_dir, fn), type='jpeg', quality=82)
            pages_meta.append({'img': f'{iso}/{fn}?v={stamp}', 'title': m['title'], 'clips': m['clips']})  # ?v: a rebuilt issue never mixes old and new page pictures
        json.dump({'iso': iso, 'date': day.get('date'), 'pdf': f'{iso}.pdf', 'pages': pages_meta}, open(os.path.join(day_dir, 'pages.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        pg.emulate_media(media='print')
        pg.pdf(path=raw, format='A4', print_background=True, prefer_css_page_size=True)
        b.close()
    srv.shutdown()
    # lock: readers can open and print, but not copy text or edit
    from pypdf import PdfReader, PdfWriter
    from pypdf.constants import UserAccessPermissions as P
    r = PdfReader(raw); w = PdfWriter()
    for pgx in r.pages: w.add_page(pgx)
    w.add_metadata({'/Title': f'జనధ్వని ఈ-పేపర్ {iso}', '/Author': 'జనధ్వని', '/Subject': 'జనధ్వని – ప్రజల గొంతుక… ప్రతి ఊరి పలుకు · A SWIPE2NEWS Publication', '/Creator': 'swipe2news.com'})
    w.encrypt(user_password='', owner_password=secrets.token_hex(16), permissions_flag=P.PRINT | P.PRINT_TO_REPRESENTATION, algorithm='AES-256')
    out = os.path.join(out_dir, iso + '.pdf')
    with open(out, 'wb') as f: w.write(f)
    os.remove(raw); os.remove(tmp)
    idx_p = os.path.join(out_dir, 'index.json')
    try: idx = json.load(open(idx_p, encoding='utf-8'))
    except Exception: idx = {'issues': []}
    idx['issues'] = [x for x in idx['issues'] if x.get('iso') != iso] + [{'iso': iso, 'date': day.get('date'), 'pages': len(r.pages), 'stories': len(day.get('stories') or [])}]
    idx['issues'].sort(key=lambda x: x['iso'], reverse=True)
    json.dump(idx, open(idx_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(open(os.path.join(ROOT, 'tools', 'epaper_viewer.html'), encoding='utf-8').read())
    print(f'epaper: {out} · {len(r.pages)} pages · {os.path.getsize(out)//1024} KB')


if __name__ == '__main__':
    main()
