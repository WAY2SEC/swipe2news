#!/usr/bin/env python3
"""Swipe2News Nigeria – phone alerts (OneSignal), like the India greetings. Runs after each Nigeria news update
(.github/workflows/push-ng.yml). Only readers of /ng/ who turned alerts on get these (tag edition=ng).

One top story per time slot, at most 4 a day (Nigerian time, WAT):
  (Nigerian Pidgin) morning 05–10 "Good morning o, Naija!" · afternoon 11–15 "How your day dey go?" ·
  evening 16–19 "How far, Naija? Evening gist don land" · night 20–21 "Sleep well o, Naija!" – each with the owner's greeting picture
No alerts 22:00–06:00. A story is never alerted twice.   Usage: python3 tools/ng/push_ng.py [--dry]
"""
import datetime, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_ID = '4f354e28-c33a-4836-8a3a-f25d58b2ba49'
FEED = os.path.join(ROOT, 'editions', 'ng', 'news.json')
STATE = os.path.join(ROOT, 'push', 'state-ng.json')
WAT = datetime.timezone(datetime.timedelta(hours=1))
SITE = 'https://swipe2news.com/'
# owner 25 Nov 2026: alert greetings in friendly Nigerian Pidgin, with the owner's greeting pictures (art/ng/greet-*.jpg)
SLOTS = [((5, 6, 7, 8, 9, 10), 'morning', '☀️ Good morning o, Naija!', 'greet-morning'),
         ((11, 12, 13, 14, 15), 'afternoon', '🌤️ How your day dey go?', 'greet-afternoon'),
         ((16, 17, 18, 19), 'evening', '🌆 How far, Naija? Evening gist don land', 'greet-evening'),
         ((20, 21), 'night', '🌙 Sleep well o, Naija!', 'greet-night')]


def sid(s):  # same id as /ng/ (and index.html)
    h = 5381
    for ch in (s.get('url') or '') + '|' + (s.get('h') or ''):
        c = ord(ch)
        for u in ([c] if c < 0x10000 else [0xD800 + ((c - 0x10000) >> 10), 0xDC00 + ((c - 0x10000) & 0x3FF)]):
            h = ((h << 5) + h + u) & 0xFFFFFFFF
    out = ''
    while True:
        h, r = divmod(h, 36); out = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + out
        if not h: return out


def short(p, n=120):
    p = ' '.join(str(p).split())
    return p if len(p) <= n else p[:n].rsplit(' ', 1)[0] + '…'


def main():
    dry = '--dry' in sys.argv
    key = os.environ.get('ONESIGNAL_REST_KEY', '').strip()
    now = datetime.datetime.now(WAT)
    slot = next(((name, greet, pic) for hours, name, greet, pic in SLOTS if now.hour in hours), None)
    if not slot:
        print(f'{now:%H:%M} WAT: no alert slot now (quiet or between slots)'); return
    try: st = json.load(open(STATE, encoding='utf-8'))
    except Exception: st = {'sent': [], 'days': {}}
    today = now.strftime('%Y-%m-%d')
    done = st.setdefault('days', {}).get(today, [])
    if slot[0] in done:
        print(f'{slot[0]} alert already sent today'); return
    stories = json.load(open(FEED, encoding='utf-8')).get('stories', [])
    fresh = []
    for s in stories:
        try: age = now - datetime.datetime.fromisoformat(s.get('pub'))
        except Exception: continue
        if sid(s) not in st['sent'] and age < datetime.timedelta(hours=8):
            fresh.append(s)
    # the first card is the editor's top story; prefer confirmed facts
    top = next((s for s in fresh if s.get('lbl') == 'fact'), fresh[0] if fresh else None)
    if not top:
        print('no new story to alert'); return
    body = {'app_id': APP_ID, 'target_channel': 'push', 'filters': [{'field': 'tag', 'key': 'edition', 'relation': '=', 'value': 'ng'}],
            'headings': {'en': slot[1]}, 'contents': {'en': short(top['h'] + ' – ' + (top.get('p') or ''), 150)},  # Pidgin greeting, then the story
            'url': SITE + 'ng/?s=' + sid(top), 'chrome_web_icon': SITE + 'icon-192.png', 'chrome_web_badge': SITE + 'icon-192.png',
            'chrome_web_image': SITE + 'art/ng/' + slot[2] + '.jpg',
            'web_push_topic': 'ng-top', 'ttl': 6 * 3600}
    if dry or not key:
        print(f'[{"dry" if dry else "no key"}] {slot[0]}: {body["headings"]["en"]} | {body["contents"]["en"][:80]} | {body["url"]}'); return
    req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read().decode() or '{}')
        print(f'sent {slot[0]}: {res.get("id")} {res.get("errors") or ""} – {top["h"]}')
    except Exception as e:
        print(f'FAILED {slot[0]}: {e}'); return
    st['sent'] = (st['sent'] + [sid(top)])[-300:]
    st['days'] = {d: v for d, v in st['days'].items() if d >= (now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')}
    st['days'][today] = done + [slot[0]]
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
