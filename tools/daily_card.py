"""Daily Morning Briefing card (owner, 26 Nov 2026): one 4K picture every morning.
Top 5 stories (no sad ones) + Hyderabad weather (IMD) + gold rate, drawn with tools/daily_card.html in Chrome.
Writes promo/daily/<date>.jpg (4K, for WhatsApp) and promo/daily/<date>-app.jpg (1080 wide, for the app pop-up and the alert),
and adds a pop-up item to tools/announce.json. The 7 AM good-morning alert uses the picture (tools/push_news.py)."""
import datetime, functools, json, os, re, sys, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
DAYS = ['సోమవారం', 'మంగళవారం', 'బుధవారం', 'గురువారం', 'శుక్రవారం', 'శనివారం', 'ఆదివారం']
MON = ['జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్', 'జులై', 'ఆగస్టు', 'సెప్టెంబర్', 'అక్టోబర్', 'నవంబర్', 'డిసెంబర్']
SAD = re.compile(r'లంచ|ఏసీబీ|మోసం|మృతి|మరణ|చనిపో|హత్య|ఆత్మహత్య|ప్రమాద|మునిగి|గల్లంతు|దుర్మరణ|అత్యాచార|లైంగిక|వేధింపు|అరెస్ట్|జైలు|died|death|dead|killed|murder|suicide|drown|accident|rape|arrest|मौत|मृत|हत्या|हादसा')
STN = {'TG': 'తెలంగాణ', 'AP': 'ఆంధ్రప్రదేశ్', 'IN': 'జాతీయం'}

def load(p, d):
    try: return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
    except Exception: return d

def lakh(n): s = f'{int(n):,}'; return '₹' + (re.sub(r'(\d+)(\d{2}),(\d{3})$', lambda m: f"{int(m.group(1)):,}".replace(',', ',') + ',' + m.group(2) + ',' + m.group(3), s) if len(str(int(n))) == 6 else s)

def inr(n):
    n = str(int(n)); last = n[-3:]; rest = n[:-3]
    parts = []
    while len(rest) > 2: parts.insert(0, rest[-2:]); rest = rest[:-2]
    if rest: parts.insert(0, rest)
    return '₹' + ','.join(parts + [last]) if parts else '₹' + last

def build(day):
    news = load('news.json', {}).get('stories', [])
    items, seen = [], set()
    for s in news:
        t = ' '.join([s.get('h') or '', s.get('statl') or '', (s.get('en') or {}).get('h') or ''])
        if SAD.search(t) or s.get('kind') or s.get('st') not in ('TG', 'AP', 'IN') or s.get('h') in seen: continue
        if str(s.get('pub') or '')[:10] < (day - datetime.timedelta(days=1)).isoformat(): continue
        place = (s.get('cat') or '').split('·')[-1].strip()
        x = dict(s); x['cat'] = STN[s['st']] + (' · ' + place if place and place not in STN.values() else '')
        items.append(x); seen.add(s.get('h'))
        if len(items) == 12: break
    # stories with a real picture first (a card full of logos looks empty), keep feed order otherwise
    items = ([x for x in items if x.get('pic') != 'logo'] + [x for x in items if x.get('pic') == 'logo'])[:5]
    wx = None
    hy = (load('weather.json', {}).get('d') or {}).get('hyderabad')
    if hy:
        dd = next((x for x in hy.get('days', []) if x.get('date') == day.isoformat()), None) or (hy.get('days') or [None])[0]
        if dd:
            w = 'వర్షం' if (dd.get('rain') or 0) >= 2.5 else ('మేఘావృతం' if (dd.get('cloud') or 0) >= 6 else 'పొడి వాతావరణం')
            wx = {'t': f"{round(dd['tmax'])}° / {round(dd['tmin'])}°", 's': 'గరిష్ఠం / కనిష్ఠం · ' + w}
    gold = None
    m = load('metals.json', {})
    cities = m.get('cities') or []
    c = next((x for x in cities if x.get('city') == 'Hyderabad' and x.get('g22')), None) or next((x for x in cities if x.get('g22')), None)
    if c:
        tel = {'Hyderabad': 'హైదరాబాద్', 'Mumbai': 'ముంబై', 'Delhi': 'ఢిల్లీ', 'Chennai': 'చెన్నై', 'Bengaluru': 'బెంగళూరు', 'Kolkata': 'కోల్‌కతా'}.get(c['city'], c['city'])
        up = str(m.get('updated') or '')
        try:
            u = datetime.datetime.fromisoformat(up); h = u.hour % 12 or 12
            when = f"{u.day} {MON[u.month-1][:4]}., {'ఉ.' if u.hour < 12 else 'సా.'} {h}:{u.minute:02d}"
        except Exception: when = ''
        sv = next((x.get('silver') for x in cities if x.get('city') == c['city'] and x.get('silver')), None) or next((x.get('silver') for x in cities if x.get('silver')), None)
        gold = {'v': inr(c['g22']), 's': (f"వెండి {inr(sv)} / కిలో" if sv else ''), 'u': f"{tel} మార్కెట్" + (f" · {when}" if when else '')}
    return {'date': f"{DAYS[day.weekday()]} · {day.day} {MON[day.month-1]} {day.year}", 'wx': wx, 'gold': gold, 'items': items}

def main():
    day = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(IST).date()
    D = build(day)
    if len(D['items']) < 3: print('not enough stories'); return
    class Q(SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.sync_api import sync_playwright
    out = os.path.join(ROOT, 'promo', 'daily'); os.makedirs(out, exist_ok=True)
    png = os.path.join(out, f'{day}.png')
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or ('/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None))
        pg = b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=2)
        pg.add_init_script('window.D=' + json.dumps(D, ensure_ascii=False))
        pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/tools/daily_card.html')
        pg.wait_for_function('document.body.dataset.ready', timeout=30000)
        pg.screenshot(path=png); b.close()
    from PIL import Image
    im = Image.open(png).convert('RGB')
    im.save(os.path.join(out, f'{day}.jpg'), quality=88, optimize=True, progressive=True)
    im.resize((1080, 1920), Image.LANCZOS).save(os.path.join(out, f'{day}-app.jpg'), quality=84, optimize=True, progressive=True)
    os.remove(png)
    # pop-up once per reader, 7 AM – 11 AM (no extra alert: the 7 AM greeting carries the picture)
    a = load('tools/announce.json', {'items': []})
    a['items'] = [x for x in a['items'] if not str(x.get('id', '')).startswith('daily-') or x['id'] >= f'daily-{day - datetime.timedelta(days=3)}']
    a['items'] = [x for x in a['items'] if x.get('id') != f'daily-{day}'] + [{'id': f'daily-{day}', 'pop': f'promo/daily/{day}-app.jpg', 'dl': f'promo/daily/{day}.jpg', 'from': f'{day}T06:30', 'to': f'{day}T11:30', 'nopush': True}]
    json.dump(a, open(os.path.join(ROOT, 'tools', 'announce.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # keep 14 days of cards
    for f in os.listdir(out):
        m2 = re.match(r'(\d{4}-\d\d-\d\d)', f)
        if m2 and m2.group(1) < str(day - datetime.timedelta(days=14)): os.remove(os.path.join(out, f))
    print('daily card', day, [x['h'] for x in D['items']])

if __name__ == '__main__': main()
