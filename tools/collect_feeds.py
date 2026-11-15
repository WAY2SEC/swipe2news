#!/usr/bin/env python3
"""Swipe2News feed collector.

Runs on GitHub Actions every 15 minutes. Reads headline feeds from Telugu and
English papers, TV sites, agencies, government press pages and Google News
(one search per outlet and per district), then:

  * keeps only items from the last 36 hours,
  * groups the same event reported by several papers into ONE "event"
    (the newsroom writes one story from one source, the others are listed),
  * marks events already published on Swipe2News as covered,
  * writes feeds/latest.json (events) and feeds/status.json (which feeds worked).

Only headline, link, outlet and time are stored — never article text.
"""
import json, re, sys, time, html, hashlib, unicodedata, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'feeds'
IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime.now(timezone.utc)
KEEP_H = 36
UA = 'Mozilla/5.0 (compatible; Swipe2NewsBot/1.0; +https://swipe2news.com)'

cfg = json.load(open(f'{ROOT}/tools/feeds.json', encoding='utf-8'))

def gnews(q, lang='te'):
    hl, ceid = ('te', 'IN:te') if lang == 'te' else ('en-IN', 'IN:en')
    return 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q, 'hl': hl, 'gl': 'IN', 'ceid': ceid})

# ---- which feeds to read this run ----------------------------------------
feeds = []
for f in cfg['direct']:
    feeds.append({'name': f['name'], 'url': f['url'], 'kind': 'direct', 'region': f.get('region', '')})
for o in cfg['outlets']:
    feeds.append({'name': o['name'], 'url': gnews(f"site:{o['site']} when:1d", o.get('lang', 'te')), 'kind': 'gnews-outlet', 'region': o.get('region', '')})
# districts: a quarter of them each run (all 59 every hour), in Telugu and English
slot = (NOW.hour * 4 + NOW.minute // 15) % 4
dists = cfg['districts']
for i, d in enumerate(dists):
    if i % 4 != slot:
        continue
    feeds.append({'name': f"district:{d['en']}", 'url': gnews(f"{d['te']} when:1d", 'te'), 'kind': 'gnews-district', 'region': d['state'], 'district': d['en']})
    feeds.append({'name': f"district:{d['en']}:en", 'url': gnews(f"{d['en']} {d['state_en']} when:1d", 'en'), 'kind': 'gnews-district', 'region': d['state'], 'district': d['en']})
for q in cfg.get('topics', []):
    feeds.append({'name': f"topic:{q['q']}", 'url': gnews(q['q'] + ' when:1d', q.get('lang', 'en')), 'kind': 'gnews-topic', 'region': q.get('region', '')})

# ---- fetch + parse ---------------------------------------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/rss+xml,application/xml,text/xml,*/*'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def ptime(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace('Z', '+00:00'))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=IST)
    return d.astimezone(timezone.utc)

def text(el, *names):
    for n in names:
        x = el.find(n)
        if x is not None and (x.text or x.get('href')):
            return (x.text or x.get('href') or '').strip()
    return ''

ATOM = '{http://www.w3.org/2005/Atom}'
def parse(raw):
    root = ET.fromstring(raw)
    out = []
    for it in root.iter('item'):
        src = it.find('source')
        out.append({'t': html.unescape(text(it, 'title')), 'u': text(it, 'link'), 'p': text(it, 'pubDate', '{http://purl.org/dc/elements/1.1/}date'),
                    'o': (src.text.strip() if src is not None and src.text else '')})
    for it in root.iter(ATOM + 'entry'):
        ln = it.find(ATOM + 'link')
        out.append({'t': html.unescape(text(it, ATOM + 'title')), 'u': ln.get('href') if ln is not None else '', 'p': text(it, ATOM + 'published', ATOM + 'updated'), 'o': ''})
    return out

# not news: tag/search/epaper pages, price tables, horoscopes, galleries, quizzes, ads
JUNK = re.compile(r'Latest News in Telugu|Top Headline|Search Results|e-?paper|epaper|Tab - Latest News|Silver Rate Today|Gold Rate Today|Petrol (?:and|&) Diesel Price|Today.s (?:Gold|Silver)|రాశి ?ఫలాలు|రాశిఫలం|ఈరోజు రాశి|Horoscope|పంచాంగం|Panchangam|Photo ?Gallery|Photos:|Web ?Stories|Quiz|Sponsored|Advertorial|Lottery (?:Result|Sambad)|Box Office Collection|OTT (?:release|this week)', re.I)
JUNK_URL = re.compile(r'/(?:tag|tags|topic|topics|search|epaper|photogallery|photos|web-?stories|videos?)/', re.I)
TGAP = re.compile(r'తెలంగాణ|హైదరాబాద్|ఏపీ|ఆంధ్ర|అమరావతి|విజయవాడ|విశాఖ|తిరుపతి|తిరుమల|రేవంత్|చంద్రబాబు|పవన్|జగన్|కేటీఆర్|కేసీఆర్|Telangana|Hyderabad|Andhra|Amaravati|Vijayawada|Visakhapatnam|Vizag|Tirupati|Tirumala|Revanth|Naidu|Pawan Kalyan|Jagan|KTR|KCR|Secunderabad|Cyberabad|GHMC|TSRTC|TGSRTC|APSRTC|Singareni', re.I)
items, status = [], []
for f in feeds:
    st = {'name': f['name'], 'kind': f['kind'], 'ok': False, 'items': 0, 'fresh': 0}
    try:
        got = parse(fetch(f['url']))
        st['ok'] = True; st['items'] = len(got)
        for g in got:
            d = ptime(g['p'])
            if not d or not g['t'] or NOW - d > timedelta(hours=KEEP_H) or d - NOW > timedelta(hours=2):
                continue
            title, outlet = g['t'], g['o'] or (f['name'] if f['kind'] in ('direct', 'gnews-outlet') else '')
            m = re.match(r'^(.*\S)\s+[-–|]\s+([^-–|]{2,40})$', title)   # Google News: "Headline - Outlet"
            if m and f['kind'].startswith('gnews'):
                title, outlet = m.group(1), outlet or m.group(2)
            if JUNK.search(title) or JUNK_URL.search(g['u'] or ''):
                st['junk'] = st.get('junk', 0) + 1
                continue
            items.append({'title': title.strip(), 'url': g['u'], 'outlet': outlet.strip(), 'time': d.astimezone(IST).isoformat(timespec='minutes'),
                          'via': f['name'], 'region': f.get('region', ''), 'district': f.get('district', '')})
            st['fresh'] += 1
    except Exception as e:
        st['error'] = str(e)[:120]
    status.append(st)
    time.sleep(0.6 if f['kind'].startswith('gnews') else 0.2)

# ---- group the same event across papers -----------------------------------
STOP = set('the a an of in on at to for and or is are was were with by from as after over into new says said will be has have its it this that report news latest live update updates today video photos telangana andhra pradesh hyderabad ap tg india'.split())
TE_STOP = set('లో కు కి ను తో పై మరియు ఈ ఆ వార్తలు తాజా లైవ్ వీడియో ఫోటోలు తెలంగాణ ఏపీ హైదరాబాద్ ఆంధ్రప్రదేశ్'.split())
def norm(t):
    t = unicodedata.normalize('NFC', t.lower())
    t = re.sub(r'[‘’“”"\'`:;,.!?()\[\]{}|/\\#@*+=<>~]', ' ', t)
    return t

def stem(w):
    # Telugu words carry case endings ("కరీంనగర్‌లో", "కరీంనగర్‌కు"): compare the first 4 letters
    return w[:4] if re.search(r'[ఀ-౿]', w) else w[:6]

def tokens(t):
    out = set()
    for w in norm(t).split():
        w = w.strip('-–')
        if len(w) < 2 or w in STOP or w in TE_STOP:
            continue
        out.add(stem(w))
    return out

def nums(t):
    return set(re.findall(r'\d[\d,.]*', t))

items.sort(key=lambda x: x['time'])
seen_url, uniq = set(), []
for it in items:
    k = it['url'] or it['title']
    if k in seen_url:
        continue
    seen_url.add(k); it['_tok'] = tokens(it['title']); it['_num'] = nums(it['title']); uniq.append(it)

events = []
for it in uniq:
    best, score = None, 0.0
    for ev in events:
        a, b = it['_tok'], ev['_tok']
        if not a or not b:
            continue
        inter = len(a & b)
        j = inter / min(len(a), len(b))
        if it['_num'] and ev['_num'] and not (it['_num'] & ev['_num']):
            j -= 0.25      # different figures → probably a different event
        if inter >= 3 and j > score:
            best, score = ev, j
    if best is not None and score >= 0.55:
        best['sources'].append({k: it[k] for k in ('outlet', 'title', 'url', 'time')})
        best['_tok'] |= it['_tok']; best['_num'] |= it['_num']
        if it['district'] and it['district'] not in best['districts']:
            best['districts'].append(it['district'])
    else:
        events.append({'_tok': set(it['_tok']), '_num': set(it['_num']), 'title': it['title'], 'first': it['time'], 'region': it['region'],
                       'districts': [it['district']] if it['district'] else [], 'sources': [{k: it[k] for k in ('outlet', 'title', 'url', 'time')}]})

# ---- best source per event + already covered on Swipe2News -----------------
RANK = {o['name']: o.get('rank', 50) for o in cfg['outlets']}
RANK.update({f['name']: f.get('rank', 40) for f in cfg['direct']})
def rank(s):
    return min([v for k, v in RANK.items() if k.lower() in (s['outlet'] or '').lower()] or [60])

published = []
import glob as _glob
for fp in [f'{ROOT}/news.json'] + sorted(_glob.glob(f'{ROOT}/archive/20*.json'))[-2:]:   # today + yesterday too
    try:
        j = json.load(open(fp, encoding='utf-8'))
        published += [s for s in (j.get('stories') if isinstance(j, dict) else j) if isinstance(s, dict)]
    except Exception:
        pass
pub_urls = {s.get('url', '') for s in published}
pub_tok = [tokens(' '.join([s.get('h', ''), s.get('statl', '') or '', (s.get('en') or {}).get('h', '') if isinstance(s.get('en'), dict) else ''])) for s in published]

out = []
for ev in events:
    ev['sources'].sort(key=lambda s: (rank(s), s['time']))
    covered = any(s['url'] in pub_urls for s in ev['sources']) or any(len(ev['_tok'] & t) >= 3 and len(ev['_tok'] & t) / max(1, min(len(ev['_tok']), len(t))) >= 0.5 for t in pub_tok)
    eid = hashlib.md5((ev['sources'][0]['url'] or ev['title']).encode()).hexdigest()[:10]
    local = bool(ev['districts']) or ev['region'] in ('TG', 'AP') or any(TGAP.search(x['title']) for x in ev['sources'])
    out.append({'id': eid, 'local': local, 'title': ev['title'], 'first_seen': ev['first'], 'region': ev['region'], 'districts': ev['districts'],
                'n_sources': len(ev['sources']), 'best': ev['sources'][0], 'others': ev['sources'][1:6], 'covered': covered})
out.sort(key=lambda e: (e['covered'], not e['local'], -e['n_sources'], e['first_seen']))

import os
os.makedirs(OUT, exist_ok=True)
summary = {'updated': NOW.astimezone(IST).isoformat(timespec='minutes'), 'window_hours': KEEP_H, 'feeds_read': len(feeds),
           'feeds_ok': sum(1 for s in status if s['ok']), 'headlines': len(uniq), 'events': len(out),
           'uncovered': sum(1 for e in out if not e['covered']), 'uncovered_tg_ap': sum(1 for e in out if not e['covered'] and e['local']), 'district_slot': slot}
json.dump({'about': 'Swipe2News feed collector: one entry per EVENT (same news from several papers grouped). Headlines and links only.',
           **summary, 'events': out}, open(f'{OUT}/latest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({**summary, 'feeds': status}, open(f'{OUT}/status.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
