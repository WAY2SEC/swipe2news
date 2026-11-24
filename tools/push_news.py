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
import json, os, re, sys, datetime, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_ID = '4f354e28-c33a-4836-8a3a-f25d58b2ba49'
STATE = os.path.join(ROOT, 'push', 'state.json')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SITE = 'https://swipe2news.com/'
DIGEST_HOURS = (7, 11, 13, 16, 18, 21)  # owner 24 Nov 2026: top story with greetings – morning 7, lunch 1 PM, evening 6, night 9 PM
GREET = {7: 'morning', 13: 'lunch', 18: 'evening', 21: 'night'}

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
        body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': filters,
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

def main():
    dry = '--dry' in sys.argv
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

    # 1) breaking news, any time
    for s in [x for x in fresh if x.get('brk')][:2]:
        print('BREAKING:', s.get('h')); send(s, 'brk', key, dry); mark(s, 'brk')
    # 2) top story at 8 AM / 1 PM / 7 PM (first run in that hour), skipped right after a breaking alert
    slot = f'{today}-{now.hour}'
    if now.hour in DIGEST_HOURS and st.get('slot') != slot and not logged('brk', hours=2):
        sad = re.compile(r'మృతి|మరణ|చనిపో|హత్య|ఆత్మహత్య|ప్రమాదం|మునిగి|గల్లంతు|దుర్మరణ|అత్యాచార|died|death|dead|killed|murder|suicide|drown|accident|rape|मौत|मृत|हत्या|हादसा')
        greet = now.hour in GREET  # a "Good night / Good morning" greeting must never sit on a death or accident story
        top = next((x for x in stories if sid(x) not in done and when(x) and now - when(x) < datetime.timedelta(hours=6)
                    and not (greet and sad.search(' '.join([x.get('h') or '', x.get('statl') or '', (x.get('en') or {}).get('h') or ''])))), None)
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
                body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': flt, 'headings': {'en': hd},
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
