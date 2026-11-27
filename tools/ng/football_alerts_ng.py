#!/usr/bin/env python3
"""Swipe2News Nigeria – football alerts (OneSignal), in friendly Pidgin. Runs after each football update.
Only readers who switched ON "⚽ Football alerts" in the Nigeria app get them (tags edition=ng AND fb=1).

  Super Eagles / Super Falcons (any Nigeria national team):
     kick-off in ~30 min · every goal · full time
  Big games (Champions League, Premier League big clubs, clubs with Super Eagles players, AFCON, NPFL top games):
     full-time result only
  Quiet 23:00–07:00 WAT except Nigeria national-team matches. At most 10 non-Nigeria alerts a day.
  Usage: python3 tools/ng/football_alerts_ng.py [--dry]
"""
import datetime as dt, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_ID = '4f354e28-c33a-4836-8a3a-f25d58b2ba49'
DATA = os.path.join(ROOT, 'editions', 'ng', 'football.json')
STATE = os.path.join(ROOT, 'push', 'football-ng.json')
WAT = dt.timezone(dt.timedelta(hours=1))
SITE = 'https://swipe2news.com/'
DAY_MAX = 10


def score(m): return f"{m['h']} {m.get('hg') or 0}–{m.get('ag') or 0} {m['a']}"


def worth_ft(m):
    return m['ng'] or m['big'] or m['naija'] or m['code'] in ('uefa.champions', 'caf.nations', 'fifa.worldq.caf', 'fifa.world', 'caf.nations_qual')


def send(key, head, text, url, topic, dry):
    body = {'app_id': APP_ID, 'target_channel': 'push',
            'filters': [{'field': 'tag', 'key': 'edition', 'relation': '=', 'value': 'ng'}, {'field': 'tag', 'key': 'fb', 'relation': '=', 'value': '1'}],
            'headings': {'en': head}, 'contents': {'en': text}, 'url': url, 'chrome_web_icon': SITE + 'icon-192.png',
            'chrome_web_badge': SITE + 'icon-192.png', 'web_push_topic': topic, 'ttl': 3 * 3600}
    if dry or not key:
        print(f'[{"dry" if dry else "no key"}] {head} | {text}'); return True
    req = urllib.request.Request('https://api.onesignal.com/notifications', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Key ' + key})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: res = json.loads(r.read().decode() or '{}')
        print('sent', head, '|', text, res.get('id'), res.get('errors') or ''); return True
    except Exception as e:
        print('FAILED', head, e); return False


def main():
    dry = '--dry' in sys.argv
    key = os.environ.get('ONESIGNAL_REST_KEY', '').strip()
    now = dt.datetime.now(WAT); today = now.strftime('%Y-%m-%d')
    try: st = json.load(open(STATE, encoding='utf-8'))
    except Exception: st = {}
    sent = set(st.get('sent', [])); goals = st.get('goals', {}); cnt = st.get('count', {})
    ms = json.load(open(DATA, encoding='utf-8')).get('matches', [])
    quiet = now.hour >= 23 or now.hour < 7
    url = SITE + 'ng/?fb=1'
    for m in ms:
        try: t = dt.datetime.fromisoformat(m['t'].replace('Z', '+00:00')).astimezone(WAT)
        except Exception: continue
        mid = m['id']
        if m['ng']:
            if m['state'] == 'pre' and dt.timedelta(0) < t - now <= dt.timedelta(minutes=40) and f'ko:{mid}' not in sent:
                if send(key, '⚽ Super Eagles don ready!', f"{m['h']} vs {m['a']} – kick-off {t:%H:%M} WAT ({m['lg']}). Make we support our boys! 🇳🇬", url, 'ng-fb-' + mid, dry): sent.add(f'ko:{mid}')
            if m['state'] in ('in', 'post'):
                g = f"{m.get('hg') or 0}-{m.get('ag') or 0}"
                if goals.get(mid) is not None and goals[mid] != g and g != '0-0':
                    if send(key, '⚽ GOAL! 🔥', f"{score(m)} ({m.get('clock') or m.get('detail')})", url, 'ng-fb-' + mid, dry): pass
                goals[mid] = g
        if m['state'] == 'post' and m.get('done') and f'ft:{mid}' not in sent and worth_ft(m):
            if t < now - dt.timedelta(hours=6): sent.add(f'ft:{mid}'); continue  # too old (first run)
            if not m['ng'] and (quiet or cnt.get(today, 0) >= DAY_MAX): continue
            head = '🏁 Full time – Super Eagles!' if m['ng'] else f"🏁 Full time · {m['lg']}"
            extra = f" · 🇳🇬 {m['naija']}" if m['naija'] else ''
            if send(key, head, score(m) + extra, url, 'ng-fb-' + mid, dry):
                sent.add(f'ft:{mid}')
                if not m['ng']: cnt[today] = cnt.get(today, 0) + 1
    keep = {m['id'] for m in ms}
    st = {'sent': sorted(x for x in sent if x.split(':', 1)[1] in keep), 'goals': {k: v for k, v in goals.items() if k in keep},
          'count': {d: n for d, n in cnt.items() if d >= (now - dt.timedelta(days=3)).strftime('%Y-%m-%d')}}
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, 'w', encoding='utf-8'), indent=0)


if __name__ == '__main__':
    main()
