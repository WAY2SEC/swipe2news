#!/usr/bin/env python3
"""Nigeria edition – Jobs list (no AI): newest vacancies from Nigerian job sites + government recruitment news.
Writes editions/ng/jobs.json {updated, jobs:[{t, co, src, url, time, gov}]} – titles and links only (readers apply on the site).
Run by .github/workflows/jobs-ng.yml three times a day.   Usage: python3 tools/ng/jobs_ng.py [OUT]
"""
import datetime as dt, email.utils, html, json, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'editions', 'ng', 'jobs.json')
WAT = dt.timezone(dt.timedelta(hours=1)); NOW = dt.datetime.now(dt.timezone.utc)
FEEDS = [('MyJobMag', 'https://www.myjobmag.com/jobsxml.xml', False), ('Hot Nigerian Jobs', 'https://www.hotnigerianjobs.com/feed/', False),
         ('Jobzilla', 'https://www.jobzilla.ng/feed/', False), ('Jobs in Nigeria', 'https://www.jobsinnigeria.careers/feed/', False),
         ('Google News', 'https://news.google.com/rss/search?q=%22recruitment+portal%22+OR+%22recruitment+exercise%22+Nigeria+when:7d&hl=en-NG&gl=NG&ceid=NG:en', True)]
GOV = re.compile(r'\b(nigerian army|army|navy|air force|police|nscdc|immigration|customs service|civil defence|federal fire service|correctional service|inec|nnpc|central bank of nigeria|cbn|nysc|n-power|npower|federal government|state government|ministry of|civil service commission|recruitment portal|shortlist)\b', re.I)   # public-sector only
JUNK = re.compile(r'\b(scam|fake|beware|lure|trafficking|cyberfraud|war)\b', re.I)

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (compatible; Swipe2NewsBot/1.0; +https://swipe2news.com)'}), timeout=30).read()

def when(s):
    try:
        d = email.utils.parsedate_to_datetime(s); return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None

jobs, seen, status = [], set(), []
for name, url, news in FEEDS:
    try:
        root = ET.fromstring(get(url).lstrip()); n = 0
        for it in root.iter('item'):
            t = re.sub(r'\s+', ' ', html.unescape(it.findtext('title') or '')).strip()
            link = (it.findtext('link') or '').strip(); d = when(it.findtext('pubDate'))
            src = name
            if news:
                s = it.find('source'); src = (s.text or 'News').strip() if s is not None else 'News'
                t = re.sub(r'\s+-\s+[^-]{2,60}$', '', t)
                if JUNK.search(t): continue
            if not t or not link or (d and NOW - d > dt.timedelta(days=7 if news else 4)): continue
            key = re.sub(r'[^a-z0-9]', '', t.lower())[:70]
            if key in seen: continue
            seen.add(key); n += 1
            m = re.search(r'\bat\s+(.+)$', t)
            jobs.append({'t': t[:140], 'co': (m.group(1)[:70] if m and not news else ''), 'src': src, 'url': link,
                         'time': (d or NOW).astimezone(WAT).isoformat(timespec='minutes'), 'gov': bool(news or GOV.search(t))})
        status.append(f'{name}: {n}')
    except Exception as e:
        status.append(f'{name}: FAILED {str(e)[:60]}')
jobs.sort(key=lambda j: j['time'], reverse=True)
gov = [j for j in jobs if j['gov']][:30]; rest = [j for j in jobs if not j['gov']][:120]
out = {'updated': NOW.astimezone(WAT).isoformat(timespec='minutes'), 'jobs': gov + rest, 'sources': status}
if len(out['jobs']) < 10 and os.path.exists(OUT):
    sys.exit('too few jobs this time – keeping the old list: ' + '; '.join(status))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f"{len(out['jobs'])} jobs ({len(gov)} government) · " + ' · '.join(status))
