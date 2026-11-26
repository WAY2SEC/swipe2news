#!/usr/bin/env python3
"""Swipe2News phone alerts (OneSignal) – runs after every news update (GitHub Action push-news.yml).

Who gets what (owner 19 Nov 2026 – alerts must reach people who installed the app):
  * BREAKING ("brk": true)       -> everyone, at once
  * Top story of the moment       -> everyone, 6 times a day: 7 AM "Good morning", 11 AM, 1 PM "Had your lunch?", 4 PM, 6 PM "Good evening", 9 PM "Good night" (IST); skipped right after a breaking alert
  * New jobs                      -> everyone, once a day at about 9 AM IST, when new job notices came in
  * District news ("place")       -> only readers who chose that district (Andhra: readers who chose AP), at most 1 per district every 2 h and 5 a day
Every alert is sent in the reader's own language (tag "lang": te / en / hi; readers without a tag get Telugu).
No alerts between 10 PM and 6 AM IST except breaking news.

Needs the GitHub secret ONESIGNAL_REST_KEY (OneSignal -> Settings -> Keys & IDs -> REST API key).
Without it the script only prints what it would send.   Usage: python3 tools/push_news.py [--dry]
"""
import json, os, re, sys, datetime, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ID = '4f354e28-c33a-4836-8a3a-f25d58b2ba49'
STATE = os.path.join(ROOT, 'push', 'state.json')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SITE = 'https://swipe2news.com/'
DIGEST_HOURS = (7, 11, 13, 16, 20)  # owner 24 Nov 2026: 7 AM and 8 PM use the owner's 30-day greeting calendar (tools/greetings.json); 1 PM lunch greeting
GREET = {7: 'morning', 13: 'lunch', 20: 'evening'}
CAL = {7: 'm', 20: 'e'}

def sid(s):  # same id as the app (index.html sid()), so the alert opens that exact card
    h = 5381
    for ch in (s.get('url') or '') + '|' + (s.get('h') or ''):
        c = ord(ch)
        units = [c] if c < 0x10000 else [0xD800 + ((c - 0x10000) >> 10), 0xDC00 + ((c - 0x10000) & 0x3FF)]
        for u in units:
            h = ((h << 5) + h + u) & 0xFFFFFFFF
    n, out = h, ''
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    while True:
        out = digits[n % 36] + out; n //= 36
        if not n: break
    return out

def when(s):
    try: return datetime.datetime.fromisoformat(str(s.get('pub') or ''))
    except Exception: return None

def text(s, lang):
    if lang in ('en', 'hi') and isinstance(s.get(lang), dict) and s[lang].get('h'):
        o = s[lang]; return o.get('h'), (o.get('p') or '')
    return s.get('h') or '', s.get('p') or ''

def short(p, n=110):
    p = ' '.join(str(p).split())
    if len(p) <= n: return p
    cut = p[:n].rsplit(' ', 1)[0]
    return cut + '…'

LANG_FILTERS = {
    'te': [{'field': 'tag', 'key': 'lang', 'relation': '!=', 'value': 'en'}, {'field': 'tag', 'key': 'lang', 'relation': '!=', 'value': 'hi'}],
    'en': [{'field': 'tag', 'key': 'lang', 'relation': '=', 'value': 'en'}],
    'hi': [{'field': 'tag', 'key': 'lang', 'relation': '=', 'value': 'hi'}],
}
# Nigeria edition (25 Nov 2026): readers of /ng/ are tagged edition=ng and get only Nigeria alerts (tools/ng/push_ng.py).
# Every India alert goes to readers with NO edition tag OR edition=in – written with not_exists / "=" (clear meaning in
# OneSignal) instead of "!=". India readers get edition=in when they open the app (index.html tagUser).
def india_only(filters):
    f = [x for x in filters if x.get('operator') is None]
    return f + [{'field': 'tag', 'key': 'edition', 'relation': 'not_exists'}, {'operator': 'OR'}] + f + [{'field': 'tag', 'key': 'edition', 'relation': '=', 'value': 'in'}]
HEAD = {'te': {'brk': '🔴 బ్రేకింగ్', 'top': '📰 ముఖ్య వార్త', 'local': '📍 మీ జిల్లా వార్త'},
        'en': {'brk': '🔴 Breaking', 'top': '📰 Top story', 'local': '📍 Your district'},
        'hi': {'brk': '🔴 ब्रेकिंग', 'top': '📰 बड़ी ख़बर', 'local': '📍 आपके ज़िले की ख़बर'}}
HEAD['te'].update(morning='☀️ శుభోదయం! నేటి ముఖ్య వార్త', lunch='🍛 భోజనం చేశారా? ఈ వార్త చూడండి', evening='🌆 శుభ సాయంత్రం! ఇప్పటి ముఖ్య వార్త', night='🌙 శుభరాత్రి! నేటి ముఖ్య వార్త')
HEAD['en'].update(morning='☀️ Good morning! Top story', lunch='🍛 Had your lunch? Catch this', evening='🌆 Good evening! Top story now', night='🌙 Good night! Today\'s top story')
HEAD['hi'].update(morning='☀️ सुप्रभात! आज की बड़ी ख़बर', lunch='🍛 खाना खाया? यह ख़बर देखिए', evening='🌆 शुभ संध्या! अभी की बड़ी ख़बर', night='🌙 शुभ रात्रि! आज की बड़ी ख़बर')

JOBTX = {'te': ('💼 కొత్త ఉద్యోగాలు', '{n} కొత్త ఉద్యోగ ప్రకటనలు · '), 'en': ('💼 New jobs', '{n} new job notices · '), 'hi': ('💼 नई नौकरियाँ', '{n} नई भर्तियाँ · ')}
def send(s, kind, key, dry, place=None):
    sent = 0
    for lang, flt in LANG_FILTERS.items():
        h, p = text(s, lang)
        filters = list(flt)
        if place:
            filters = [{'field': 'tag', 'key': 'place', 'relation': '=', 'value': place}] + filters
        body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': india_only(filters),
                'headings': {'en': f"{HEAD[lang][kind]} · {h}"[:90]}, 'contents': {'en': short(p) or h},
                'url': SITE + '?s=' + sid(s), 'chrome_web_icon': SITE + 'icon-192.png',
                'chrome_web_badge': SITE + 'icon-192.png', 'web_push_topic': ('top' if kind in GREET.values() else kind) + (place or ''), 'ttl': 6 * 3600}
        if dry or not key:
            print(f'  [{"dry" if dry else "no key"}] {kind}/{lang}{"/" + place if place else ""}: {body["headings"]["en"]}')
            continue
        req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read().decode() or '{}')
            print(f'  sent {kind}/{lang}{"/" + place if place else ""}: {res.get("id")} {res.get("errors") or ""}')
            sent += 1
        except Exception as e:
            print(f'  FAILED {kind}/{lang}: {e}')
    return sent


# ---- owner's 30-day greeting calendar (tools/greetings.json) ----
TOPIC = {'weather': r'వాతావరణ|వర్ష|చలి|ఎండ', 'commute': r'ట్రాఫిక్|మెట్రో|రోడ్డు|బస్|ఆర్టీసీ|రైలు', 'money': r'బంగారం|వెండి|ధర|మార్కెట్|వ్యాపార|బ్యాంక',
         'farm': r'వ్యవసాయ|రైతు|పంట|మార్కెట్ యార్డ్|మండీ|పత్తి|వరి|ధాన్యం', 'edu': r'విద్య|పరీక్ష|స్కూల్|పాఠశాల|కాలేజీ|ఫలితాల|విద్యార్థ',
         'jobs': r'ఉద్యోగ|నియామక|పోస్టుల|రిక్రూట్', 'politics': r'రాజకీయ|ఎన్నిక|పార్టీ|అసెంబ్లీ', 'movies': r'సినిమా|వినోద|OTT|ట్రైలర్',
         'health': r'ఆరోగ్య|ఆసుపత్రి|వైద్య|హాస్పిటల్', 'sports': r'క్రీడ|క్రికెట్|మ్యాచ్|టోర్నీ|పోటీలు', 'schemes': r'పథక|పింఛన్|రేషన్|సంక్షేమ',
         'tech': r'టెక్|సైబర్|యాప్|ఏఐ|మొబైల్', 'city': r'నీటి|కరెంట్|విద్యుత్|రోడ్డు|జీహెచ్ఎంసీ|మున్సిప|హైడ్రా|డ్రైనేజీ',
         'devotional': r'ఆలయ|భక్తి|తిరుమల|టీటీడీ|దేవాలయ|దర్శనం', 'world': r'భారత్|దేశం|ప్రపంచ|అంతర్జాతీయ|కేంద్ర'}
LIQ = {'te': {'district': 'మీ ప్రాంతం', 'city': 'మీ నగరం', 'state': 'తెలంగాణ, ఏపీ'},  # used for readers with no district chosen
       'en': {'district': 'your area', 'city': 'your city', 'state': 'Telangana and AP'}}

def post(body, label, key, dry):
    body = dict(body, filters=india_only(body.get('filters') or []))
    if dry or not key:
        print(f'  [{"dry" if dry else "no key"}] {label}: {body["headings"]["en"]} | {body["contents"]["en"][:70]}'); return
    req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read().decode() or '{}')
        print(f'  sent {label}: {res.get("id")} {res.get("errors") or ""}')
    except Exception as e:
        print(f'  FAILED {label}: {e}')

def wx_line(day, lang):
    cond = ('వర్షం అవకాశం' if lang == 'te' else 'rain likely') if (day.get('rain') or 0) >= 2.5 else \
           ('మేఘావృతం' if lang == 'te' else 'cloudy') if (day.get('cloud') or 0) >= 5 else ('పొడి వాతావరణం' if lang == 'te' else 'dry')
    return f"{int(day['tmin'])}–{int(day['tmax'])}°, {cond}"

def calendar(now, which, stories, sadf, done, key, dry):
    """Send the calendar greeting for this morning ('m') or evening ('e'). Returns the story used (or None)."""
    try: G = json.load(open(os.path.join(ROOT, 'tools', 'greetings.json'), encoding='utf-8'))
    except Exception as e: print('  greetings.json missing:', e); return None
    today = now.strftime('%Y-%m-%d'); wd = now.weekday()
    n = (now.date() - datetime.date.fromisoformat(G['start'])).days
    if n < 0: return None
    day = G['days'][n % len(G['days'])]; line = day[which]; topic = day.get('topic', '')
    fest = (G.get('festivals') or {}).get(today, {})
    over = {(0, 'm'): 'mon_m', (4, 'm'): 'fri_m', (5, 'e'): 'sat_e', (6, 'm'): 'sun_m', (6, 'e'): 'sun_e'}.get((wd, which))
    if fest.get(which): line, topic = fest[which], ''
    elif over and not topic and not re.search(r'\{(weather|quote|local_fact)\}', line.get('en', '')):  # weekday lines only replace the general days
        line = G['weekday'][over]; topic = {'fri_m': 'movies'}.get(over, '')
    else: over = None
    ok = lambda x: sid(x) not in done and when(x) and now - when(x) < datetime.timedelta(hours=8) and not sadf(x)
    pool = [x for x in stories if ok(x)]
    rx = re.compile(TOPIC[topic]) if topic in TOPIC else None
    top = next((x for x in pool if rx and rx.search((x.get('cat') or '') + ' ' + (x.get('h') or ''))), None) or (pool[0] if pool else None)
    if not top: return None
    url = SITE + ('?jobs' if topic == 'jobs' else '?s=' + sid(top))
    if day.get('theme') == 'Thank you' and which == 'e' and 'WhatsApp' in line.get('en', ''):
        url = 'https://wa.me/917032656422?text=' + urllib.parse.quote('Swipe2News – నాకు ఈ వార్తలు ఎక్కువ కావాలి: ')
    try: D = json.load(open(os.path.join(ROOT, 'daily.json'), encoding='utf-8')).get('items', [])
    except Exception: D = []
    def item(kind): return next((x for x in D if x.get('kind') == kind), None)
    print(f'CALENDAR day {n % len(G["days"]) + 1} {which} ({day.get("theme")}{" · festival" if fest.get(which) else " · " + over if over else ""}):', top.get('h'))
    for lang, flt in LANG_FILTERS.items():
        h, p = text(top, lang)
        base = {'app_id': APP_ID, 'target_channel': 'push', 'url': url, 'chrome_web_icon': SITE + 'icon-192.png',
                'chrome_web_badge': SITE + 'icon-192.png', 'web_push_topic': 'greet', 'ttl': 6 * 3600}
        if lang == 'hi':  # the calendar is Telugu + English; Hindi readers keep the simple greeting
            post(dict(base, filters=flt, headings={'en': f"{HEAD['hi']['morning' if which == 'm' else 'evening']} · {h}"[:90]}, contents={'en': short(p) or h}), f'greet/{which}/hi', key, dry)
            continue
        tx = line[lang]; body = h  # the alert shows the personal note, then the story headline
        fill = dict(LIQ[lang], headline=h)
        q = item('quote'); r = item('roots')
        qt = ((q or {}).get('text') if lang == 'te' else ((q or {}).get('en') or {}).get('text')) or ''
        rt = ((r or {}).get('text') if lang == 'te' else ((r or {}).get('en') or {}).get('text')) or ''
        rt = re.split(r'(?<=[.!?।])\s', rt.strip())[0] if rt else ''
        fill['quote'] = qt; fill['local_fact'] = rt
        if '{headline}' in tx: body = short(p) or h
        need = re.findall(r'\{(quote|local_fact|weather|headline)\}', tx)
        plain = line.get('p' + lang)
        if any(k in ('quote', 'local_fact') for k in need):
            val = ' '.join(fill.get(k) or '' for k in need if k in ('quote', 'local_fact')).strip()
            if not val: tx = plain or tx
            elif len(tx.format(**{**fill, 'weather': ''})) > 90 and plain: tx, body = plain, short(val, 150)  # long thought: short heading, the thought below
        if re.search(r'\{(weather|district|city|state)\}', tx):  # one alert per district with its own name (and IMD forecast), the plain line for everyone else
            try: W = json.load(open(os.path.join(ROOT, 'weather.json'), encoding='utf-8'))['d']
            except Exception: W = {}
            try:
                NM = {k: (te, en) for k, te, en in re.findall(r"\['([a-zA-Z]+)','([^']+)','([^']+)'\]", open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read().split('const PLACES', 1)[1].split('];', 1)[0])}
            except Exception: NM = {}
            done_keys = []
            for k, (nte, nen) in NM.items():
                f2 = dict(fill, state='తెలంగాణ' if lang == 'te' else 'Telangana')
                if k != 'TS':
                    nm = nte + ('\u200c' if nte.endswith('్') else '') if lang == 'te' else nen
                    f2.update(city=nm, district=nm)
                t2 = tx
                if '{weather}' in tx:
                    dd = next((x for x in (W.get(k) or {}).get('days', []) if x.get('date') == today), None)
                    if not dd: continue
                    f2['weather'] = wx_line(dd, lang)
                done_keys.append(k)
                post(dict(base, filters=[{'field': 'tag', 'key': 'place', 'relation': '=', 'value': k}] + flt,
                          headings={'en': t2.format(**f2)}, contents={'en': body}), f'greet/{which}/{lang}/{k}', key, dry)
            ex = [{'field': 'tag', 'key': 'place', 'relation': '!=', 'value': k} for k in done_keys]
            rest = (plain or tx.replace('{weather}', '')) if '{weather}' in tx else tx
            f3 = dict(fill); f3.setdefault('weather', '')
            post(dict(base, filters=ex + flt, headings={'en': rest.format(**f3)}, contents={'en': body}), f'greet/{which}/{lang}/rest', key, dry)
            continue
        post(dict(base, filters=flt, headings={'en': tx.format(**fill)}, contents={'en': body}), f'greet/{which}/{lang}', key, dry)
    return top

def wait_live(local_updated, limit=300):
    """Owner, 26 Nov 2026: an alert tap must open the exact story. This job starts the moment the news is pushed,
    but the website (GitHub Pages) needs a minute or two to publish it; an alert sent before that opened another card.
    So wait until swipe2news.com serves this news.json (at most 5 minutes, then send anyway)."""
    import time
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            with urllib.request.urlopen(SITE + 'news.json?t=' + str(int(time.time())), timeout=20) as r:
                if (json.loads(r.read().decode()).get('updated') or '') >= local_updated:
                    print('site is live (%ds)' % (time.time() - t0)); return True
        except Exception as e:
            print('site check:', e)
        time.sleep(20)
    print('site not updated after %ds, sending anyway' % limit); return False

def main():
    dry = '--dry' in sys.argv
    if not dry:
        try: wait_live(json.load(open(os.path.join(ROOT, 'news.json'), encoding='utf-8')).get('updated') or '')
        except Exception as e: print('wait_live skipped:', e)
    key = os.environ.get('ONESIGNAL_REST_KEY', '').strip()
    now = datetime.datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    stories = [s for s in json.load(open(os.path.join(ROOT, 'news.json'), encoding='utf-8'))['stories'] if not s.get('kind')]
    try: st = json.load(open(STATE, encoding='utf-8'))
    except Exception: st = {}
    st.setdefault('sent', []); st.setdefault('log', [])
    st['log'] = [x for x in st['log'] if x.get('t', '') >= (now - datetime.timedelta(days=2)).isoformat()]
    done = set(st['sent'][-600:])
    fresh = [s for s in stories if when(s) and now - when(s) < datetime.timedelta(hours=3) and sid(s) not in done]
    night = now.hour >= 22 or now.hour < 6
    def logged(kind, place=None, hours=24):
        since = (now - datetime.timedelta(hours=hours)).isoformat()
        return [x for x in st['log'] if x['kind'] == kind and x.get('place') == place and x['t'] >= since]
    def mark(s, kind, place=None):
        st['sent'].append(sid(s)); st['log'].append({'t': now.isoformat(), 'kind': kind, 'place': place, 'h': s.get('h')}); done.add(sid(s))

    # 0) owner's one-off announcements to every India reader (tools/announce.json), each sent once
    try: ann = json.load(open(os.path.join(ROOT, 'tools', 'announce.json'), encoding='utf-8')).get('items', [])
    except Exception: ann = []
    for a in ann:
        k = 'ann:' + a['id']
        if k in done or not (a.get('from', '') <= now.strftime('%Y-%m-%dT%H:%M') <= a.get('to', '9999')): continue
        print('ANNOUNCE:', a['id'])
        for lang, flt in LANG_FILTERS.items():
            t = a.get(lang) or a['en']
            body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': list(flt), 'headings': {'en': t['h']}, 'contents': {'en': t['b']},
                    'url': a.get('url') or SITE, 'chrome_web_icon': SITE + 'icon-192.png', 'chrome_web_badge': SITE + 'icon-192.png',
                    'web_push_topic': 'ann', 'ttl': 12 * 3600}
            if a.get('image'): body.update(chrome_web_image=a['image'], big_picture=a['image'], ios_attachments={'id1': a['image']})
            post(body, f'ann/{a["id"]}/{lang}', key, dry)
        st['sent'].append(k); st['log'].append({'t': now.isoformat(), 'kind': 'ann', 'place': None, 'h': a['id']}); done.add(k)
    # 1) breaking news, any time
    for s in [x for x in fresh if x.get('brk')][:2]:
        print('BREAKING:', s.get('h')); send(s, 'brk', key, dry); mark(s, 'brk')
    # 2) top story at 8 AM / 1 PM / 7 PM (first run in that hour), skipped right after a breaking alert
    slot = f'{today}-{now.hour}'
    if now.hour in DIGEST_HOURS and st.get('slot') != slot and not logged('brk', hours=2):
        sad = re.compile(r'మృతి|మరణ|చనిపో|హత్య|ఆత్మహత్య|ప్రమాదం|మునిగి|గల్లంతు|దుర్మరణ|అత్యాచార|died|death|dead|killed|murder|suicide|drown|accident|rape|मौत|मृत|हत्या|हादसा')
        greet = now.hour in GREET  # a "Good night / Good morning" greeting must never sit on a death or accident story
        sadf = lambda x: bool(sad.search(' '.join([x.get('h') or '', x.get('statl') or '', (x.get('en') or {}).get('h') or ''])))
        if now.hour in CAL:
            top = calendar(now, CAL[now.hour], stories, sadf, done, key, dry)
            if top: mark(top, 'top')
            st['slot'] = slot; top = None
        else:
            top = next((x for x in stories if sid(x) not in done and when(x) and now - when(x) < datetime.timedelta(hours=6)
                    and not (greet and sadf(x))), None)
        if top:
            kd = GREET.get(now.hour, 'top'); print('TOP STORY (' + kd + '):', top.get('h')); send(top, kd, key, dry); mark(top, 'top')
        st['slot'] = slot
    # 3) district news to readers of that district
    if not night:
        for s in fresh:
            pl = str(s.get('place') or '').strip()
            # Andhra readers choose "AP" as a whole in the app, so AP district news goes to them as one group
            if pl.lower().startswith('ap-') or (s.get('st') == 'AP' and pl.lower() in ('', 'ap')):
                pl = 'AP'
            if not pl or pl in ('tg', 'ap', 'TS', 'IN') or pl.startswith('st-') or sid(s) in done:  # other states: nobody picks them as home
                continue
            if logged('local', pl, 2) or len(logged('local', pl, 24)) >= 5:  # 1 every 2 h, 5 a day per district
                continue
            print('DISTRICT', pl + ':', s.get('h')); send(s, 'local', key, dry, place=pl); mark(s, 'local', pl)
    # 4) new jobs once a day (~9 AM IST)
    if now.hour == 9 and st.get('jobday') != today:
        try:
            J = json.load(open(os.path.join(ROOT, 'jobs.json'), encoding='utf-8'))['jobs']
        except Exception:
            J = []
        seen = set(st.get('jobs_seen', []))
        new = [j for j in J if j.get('id') and j['id'] not in seen]
        if new and seen:  # the very first run only remembers what is there
            top = new[0]
            for lang, flt in LANG_FILTERS.items():
                hd, pre = JOBTX[lang]; h = (top.get(lang) or {}).get('h') if isinstance(top.get(lang), dict) else None
                body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': india_only(flt), 'headings': {'en': hd},
                        'contents': {'en': (pre.format(n=len(new)) + (h or top.get('h') or ''))[:160]},
                        'url': SITE + '?jobs', 'chrome_web_icon': SITE + 'icon-192.png', 'web_push_topic': 'jobs', 'ttl': 12 * 3600}
                if dry or not key:
                    print('  [dry] jobs/' + lang + ':', body['contents']['en']); continue
                try:
                    req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
                    with urllib.request.urlopen(req, timeout=20) as r: print('  sent jobs/' + lang + ':', json.loads(r.read().decode() or '{}').get('id'))
                except Exception as e:
                    print('  FAILED jobs/' + lang + ':', e)
            st['log'].append({'t': now.isoformat(), 'kind': 'jobs', 'place': None, 'h': f'{len(new)} new jobs'})
        st['jobs_seen'] = [j['id'] for j in J if j.get('id')][-800:]
        st['jobday'] = today
    if not dry and key:  # without the key nothing went out, so nothing is marked as sent
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        st['sent'] = st['sent'][-600:]
        json.dump(st, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not key:
        print('ONESIGNAL_REST_KEY is not set – nothing was sent (add it in GitHub → Settings → Secrets → Actions).')

if __name__ == '__main__':
    main()
