#!/usr/bin/env python3
""""Why this matters · ఇది ఎందుకు ముఖ్యం?" – editor approval of a story's why lines (owner 27 Nov 2026).

The explanation text stays where it always was: story["why"], story["en"]["why"], story["hi"]["why"].
An editor's approval is the optional field story["whyr"]:
  {"ok": true, "at": "2026-11-27T10:05+05:30", "src": ["https://…"], "hash": "<why_hash>", "by": "ED1"}
The app shows the "ఇది ఎందుకు ముఖ్యం?" button only when this approval is valid and "hash" still matches
the current text, so any later edit (correction, proofreading) hides it until an editor approves it again.
Scheduled tasks never write "whyr"; they must keep it unchanged when they re-save a story.

Usage:
  python3 tools/why_check.py approve news.json <story id> --src URL [--src URL] [--by ED1]
  python3 tools/why_check.py check news.json            # list approvals and problems
check_news.py calls problems() for every story; with --fix an invalid approval is removed (never blocks publishing).
"""
import datetime as dt, ipaddress, json, re, sys
from urllib.parse import urlsplit

MAX_LEN = {'te': 180, 'en': 220, 'hi': 220}
MAX_SENT = 2
OFFICIAL = ('gov.in', 'nic.in', 'gov', 'rbi.org.in', 'indianrailways.gov.in', 'irctc.co.in', 'eci.gov.in',
            'tspsc.gov.in', 'tgpsc.gov.in', 'psc.ap.gov.in', 'upsc.gov.in', 'imd.gov.in', 'pib.gov.in', 'who.int', 'un.org')
SHORTENERS = ('bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'cutt.ly', 'rb.gy', 'shorturl.at')
# words that turn an explanation into a promise about money, deadlines or who qualifies: allowed only if the story says it too
RISKY = {
    'te': ['అర్హ', 'చివరి తేదీ', 'గడువు', 'దరఖాస్తు', 'ఉచితంగా', 'రాయితీ', 'జరిమానా', 'రుణమాఫీ', 'పెన్షన్', 'జీతం'],
    'en': ['eligib', 'deadline', 'last date', 'apply', 'free of cost', 'subsid', 'fine of', 'penalt', 'loan waiver', 'pension', 'salary', 'refund'],
    'hi': ['पात्र', 'अंतिम तिथि', 'आवेदन', 'मुफ्त', 'सब्सिडी', 'जुर्माना', 'पेंशन', 'वेतन'],
}
SENT_END = re.compile(r'[.!?।]+(?=\s|$)')


def djb2(t):
    """Same as the app's sid(): djb2 over UTF-16 code units, unsigned, base 36."""
    h = 5381
    b = t.encode('utf-16-le')
    for i in range(0, len(b), 2):
        h = ((h << 5) + h + (b[i] | b[i + 1] << 8)) & 0xFFFFFFFF
    n, out = h, ''
    while True:
        n, r = divmod(n, 36)
        out = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + out
        if not n:
            return out


def story_id(s):
    return s.get('_sid') or djb2((s.get('url') or '') + '|' + (s.get('h') or ''))


def texts(s):
    g = lambda L: (s.get(L) or {}).get('why') if isinstance(s.get(L), dict) else ''
    return {'te': (s.get('why') or '').strip(), 'en': (g('en') or '').strip(), 'hi': (g('hi') or '').strip()}


def why_hash(s):
    t = texts(s)
    return djb2(t['te'] + '\n' + t['en'] + '\n' + t['hi'])


def story_text(s, L):
    o = s if L == 'te' else (s.get(L) if isinstance(s.get(L), dict) else {})
    pts = o.get('pts') or []
    return ' '.join([o.get('h') or '', o.get('p') or '', ' '.join(pts if isinstance(pts, list) else []), o.get('next') or '', o.get('stat') or '', o.get('statl') or ''])


def parse_time(v):
    try:
        t = dt.datetime.fromisoformat(str(v).replace('Z', '+00:00'))
        return t if t.tzinfo else None
    except Exception:
        return None


def host_of(u):
    try:
        return (urlsplit(u).hostname or '').lower()
    except Exception:
        return ''


def url_problem(u):
    if not isinstance(u, str) or len(u) > 500 or any(c in u for c in ' <>"\'\\\n\t'):
        return 'not a clean link'
    p = urlsplit(u)
    if p.scheme != 'https':
        return 'must start with https://'
    if p.username or p.password or not p.hostname or '.' not in p.hostname:
        return 'odd address'
    try:
        ipaddress.ip_address(p.hostname); return 'uses an IP address'
    except ValueError:
        pass
    if p.hostname.lower().removeprefix('www.') in SHORTENERS:
        return 'short link – use the real page'
    return ''


def same_site(a, b):
    a, b = a.removeprefix('www.'), b.removeprefix('www.')
    return bool(a and b) and (a == b or a.endswith('.' + b) or b.endswith('.' + a))


def problems(s, now=None):
    """[] when the approval is valid. Stories without "whyr" are not checked (nothing to show)."""
    r = s.get('whyr')
    if r is None:
        return []
    if not isinstance(r, dict):
        return ['"whyr" is not an object']
    out = []
    if r.get('ok') is not True:
        out.append('not approved (ok is not true)')
    at = parse_time(r.get('at'))
    now = now or dt.datetime.now(dt.timezone.utc)
    if not at:
        out.append('"at" is not a date-time with time zone')
    else:
        if at > now + dt.timedelta(minutes=10):
            out.append('"at" is in the future')
        pub = parse_time(s.get('pub'))
        if pub and at < pub - dt.timedelta(minutes=1):
            out.append('"at" is before the story was published')
    if 'by' in r and not re.fullmatch(r'[A-Za-z0-9]{1,8}', str(r.get('by'))):
        out.append('"by" must be a short editor code (no names or phone numbers)')
    t = texts(s)
    for L in ('te', 'en'):
        if not t[L]:
            out.append(f'{L} why line missing')
    for L, x in t.items():
        if not x:
            continue
        if len(x) > MAX_LEN[L]:
            out.append(f'{L} why line is {len(x)} characters (max {MAX_LEN[L]})')
        parts = [p for p in SENT_END.split(x) if p.strip()]
        if len(parts) > MAX_SENT:
            out.append(f'{L} why line has more than {MAX_SENT} sentences')
        if '<' in x or '>' in x or 'http' in x.lower():
            out.append(f'{L} why line contains markup or a link')
        body = story_text(s, L)
        for n in re.findall(r'\d[\d,.]*', x):
            if n.rstrip('.,') not in body:
                out.append(f'{L} why line has "{n}" which the story does not mention')
        for w in RISKY[L]:
            if w.lower() in x.lower() and w.lower() not in body.lower():
                out.append(f'{L} why line talks about "{w}" which the story does not mention')
        if '₹' in x and '₹' not in body:
            out.append(f'{L} why line has a ₹ amount the story does not mention')
    src = r.get('src')
    if not isinstance(src, list) or not 1 <= len(src) <= 3:
        out.append('"src" must list 1–3 links')
    else:
        for u in src:
            e = url_problem(u)
            if e:
                out.append(f'source {str(u)[:60]!r}: {e}')
        hosts = [host_of(u) for u in src if not url_problem(u)]
        story_host = host_of(s.get('url') or '')
        if hosts and not any(same_site(h, story_host) or any(h == o or h.endswith('.' + o) for o in OFFICIAL) for h in hosts):
            out.append("no source is the story's own source or an official site")
    if r.get('hash') != why_hash(s):
        out.append('why text changed after approval – an editor must approve it again')
    return out


def approve(path, sid, srcs, by=None):
    d = json.load(open(path, encoding='utf-8'))
    L = d['stories'] if isinstance(d, dict) else d
    hit = [s for s in L if not s.get('kind') and story_id(s) == sid]
    if not hit:
        sys.exit(f'no story with id {sid} in {path}')
    s = hit[0]
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).replace(second=0, microsecond=0)
    r = {'ok': True, 'at': now.isoformat(timespec='minutes'), 'src': srcs, 'hash': why_hash(s)}
    if by:
        r['by'] = by
    s['whyr'] = r
    bad = problems(s)
    if bad:
        del s['whyr']
        sys.exit('NOT approved: ' + '; '.join(bad))
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'approved {sid}: {texts(s)["te"]}')


def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == 'approve':
        srcs = [a[i + 1] for i, x in enumerate(a) if x == '--src' and i + 1 < len(a)]
        by = a[a.index('--by') + 1] if '--by' in a else None
        return approve(a[1], a[2], srcs, by)
    if len(a) >= 2 and a[0] == 'check':
        d = json.load(open(a[1], encoding='utf-8'))
        for s in (d['stories'] if isinstance(d, dict) else d):
            if 'whyr' in s:
                p = problems(s)
                print(('OK   ' if not p else 'BAD  ') + story_id(s) + '  ' + (s.get('h') or '')[:40] + ('' if not p else '  → ' + '; '.join(p)))
        return
    print(__doc__)


if __name__ == '__main__':
    main()
