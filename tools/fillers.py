"""Janadhwani e-paper space fillers (user, 25 Nov 2026).

Builds the day's filler modules from tools/fillers.json (+ live mandi.json and tools/quotes.json).
Nothing here calls Claude: the library is plain JSON that the team can edit.
Every module comes in up to three sizes (l, m, s) for one column (about 59 mm wide);
the e-paper's layout script measures each empty space and puts in the largest module that fits.
"""
import datetime, html, json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc = lambda s: html.escape(str(s or ''), quote=False)
MON = ['జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్', 'జులై', 'ఆగస్టు', 'సెప్టెంబర్', 'అక్టోబర్', 'నవంబర్', 'డిసెంబర్']
LABEL = {'mandi': 'మార్కెట్ ధరలు', 'onthisday': 'చరిత్రలో ఈ రోజు', 'anniv': 'జయంతి · వర్ధంతి', 'quote': 'నేటి మంచి మాట',
         'proverb': 'సామెత – అర్థం', 'health': 'ఆరోగ్యం · అవగాహన', 'gk': 'జనరల్ నాలెడ్జ్', 'fact': 'మీకు తెలుసా?',
         'heritage': 'మన వారసత్వం', 'sudoku': 'సుడోకు', 'riddle': 'పొడుపు కథలు', 'promo': 'Swipe2News', 'reporter': 'మీ ఊరి వార్త',
         'channels': 'మీ జిల్లా వాట్సాప్ ఛానెల్', 'bizad': 'ప్రకటనలు', 'paid': 'ప్రకటన'}
PROMO = {'promo', 'reporter', 'channels', 'bizad'}


def load(name, default):
    try: return json.load(open(os.path.join(ROOT, name), encoding='utf-8'))
    except Exception: return default


def box(k, body, foot='', cls=''):
    return (f'<div class="fm fm-{k} {cls}"><div class="fmh"><i></i><span>{esc(LABEL.get(k, k))}</span></div>'
            f'{body}{f"<div class=fmf>{foot}</div>" if foot else ""}</div>')


def rot(lst, n, seed):
    """n items from lst, starting at a different place every day"""
    if not lst: return []
    st = seed % len(lst)
    return [lst[(st + i) % len(lst)] for i in range(min(n, len(lst)))]


def upside(t):
    return f'<p class="fans">{t}</p>'


# ---------- sudoku: a fresh puzzle every day, made from the date (same date = same puzzle) ----------
def sudoku(n, seed):
    br, bc = (3, 3) if n == 9 else (2, 3)
    rnd = random.Random(seed)
    base = lambda r, c: (bc * (r % br) + r // br + c) % n
    rows = [g * br + r for g in rnd.sample(range(n // br), n // br) for r in rnd.sample(range(br), br)]
    cols = [g * bc + c for g in rnd.sample(range(n // bc), n // bc) for c in rnd.sample(range(bc), bc)]
    nums = rnd.sample(range(1, n + 1), n)
    sol = [[nums[base(r, c)] for c in cols] for r in rows]
    grid = [row[:] for row in sol]

    def count(g, lim=2):
        for i in range(n * n):
            r, c = divmod(i, n)
            if g[r][c] == 0:
                tot = 0
                for v in range(1, n + 1):
                    if all(g[r][x] != v for x in range(n)) and all(g[x][c] != v for x in range(n)) and \
                       all(g[r // br * br + a][c // bc * bc + b] != v for a in range(br) for b in range(bc)):
                        g[r][c] = v; tot += count(g, lim - tot); g[r][c] = 0
                        if tot >= lim: break
                return tot
        return 1
    cells = list(range(n * n)); rnd.shuffle(cells)
    keep = 26 if n == 9 else 12
    for i in cells:
        if sum(1 for row in grid for v in row if v) <= keep: break
        r, c = divmod(i, n); v = grid[r][c]; grid[r][c] = 0
        if count([row[:] for row in grid]) != 1: grid[r][c] = v
    def table(g, cls):
        trs = ''
        for r in range(n):
            tds = ''.join(f'<td class="{"bR " if (c + 1) % bc == 0 and c < n - 1 else ""}{"bB" if (r + 1) % br == 0 and r < n - 1 else ""}">{g[r][c] or ""}</td>' for c in range(n))
            trs += f'<tr>{tds}</tr>'
        return f'<table class="{cls}">{trs}</table>'
    return table(grid, f'sdk n{n}'), ' '.join(''.join(str(v) for v in row) for row in sol)


def build(iso, edition_seed=None):
    lib = load('tools/fillers.json', {})
    st = lib.get('settings', {})
    mods = st.get('modules', {})
    on = lambda k: mods.get(k, {}).get('on', True)
    pri = lambda k: mods.get(k, {}).get('pri', 5)
    d = datetime.date.fromisoformat(iso)
    seed = edition_seed if edition_seed is not None else d.toordinal()
    out = []

    def add(k, variants, promo=None):
        vs = [v for v in variants if v]
        if vs and on(k.split(':')[0]):
            out.append({'k': k, 'pri': pri(k.split(':')[0]), 'promo': bool(promo if promo is not None else k in PROMO), 'v': vs})

    # paid ads first (while their dates run)
    for a in lib.get('ads', []):
        if not a.get('on'): continue
        if a.get('from') and iso < a['from']: continue
        if a.get('to') and iso > a['to']: continue
        img = f'<img class="fadimg" src="{esc(a["img"])}" alt="">' if a.get('img') else ''
        body = f'{img}<h4>{esc(a.get("title"))}</h4><p>{esc(a.get("text"))}</p><p class="fct">{esc(a.get("contact"))}</p><small class="fadv">{esc(a.get("advertiser"))}</small>'
        add('paid:' + str(a.get('id')), [box('paid', body, cls='paid')], promo=False)

    # market prices from today's Agmarknet data
    m = load('mandi.json', {})
    crops = {'paddy': 'వరి', 'cotton': 'పత్తి', 'maize': 'మొక్కజొన్న', 'turmeric': 'పసుపు', 'groundnut': 'వేరుశనగ', 'chilli': 'ఎండు మిర్చి',
             'redgram': 'కందులు', 'jowar': 'జొన్నలు', 'onion': 'ఉల్లిపాయ', 'tomato': 'టమాటా', 'banana': 'అరటి', 'soybean': 'సోయాబీన్'}
    best = {}
    for r in (m.get('rows') or []):
        try: age = (d - datetime.date.fromisoformat(r.get('date'))).days
        except Exception: continue
        if r.get('crop') in crops and 0 <= age <= 5 and r.get('modal'):
            b = best.get(r['crop'])
            if not b or (r.get('st') == 'TG', r['modal']) > (b.get('st') == 'TG', b['modal']): best[r['crop']] = r  # Telangana markets first
    if best:
        ordered = sorted(best.values(), key=lambda r: list(crops).index(r['crop']))
        dt = max(r['date'] for r in ordered); dd = datetime.date.fromisoformat(dt)
        def mtab(n):
            rows = ''.join(f'<tr><td>{esc(crops[r["crop"]])}<small>{esc(r.get("mkt"))}{" (ఏపీ)" if r.get("st") == "AP" else ""}</small></td><td class="n">₹{r["modal"]:,}</td></tr>' for r in ordered[:n])
            return box('mandi', f'<table class="fmt"><tr><th>పంట · మార్కెట్</th><th class="n">ధర/క్వింటా</th></tr>{rows}</table>',
                       f'అత్యధిక సగటు ధర · {dd.day} {MON[dd.month - 1]} · ఆధారం: Agmarknet')
        add('mandi', [mtab(7) if len(ordered) >= 6 else '', mtab(5) if len(ordered) >= 4 else '', mtab(3)])

    # on this day / anniversaries (only checked dates from the library)
    day = lib.get('days', {}).get(f'{d.month:02d}-{d.day:02d}', [])
    ev = [x for x in day if x.get('k') == 'e']; pe = [x for x in day if x.get('k') in ('b', 'd')]
    head = f'<p class="fdate">{d.day} {MON[d.month - 1]}</p>'
    if ev: add('onthisday', [box('onthisday', head + ''.join(f'<p class="fev">{esc(x["t"])}</p>' for x in ev))])
    if pe: add('anniv', [box('anniv', head + ''.join(f'<p class="fev"><b>{"🌼" if x["k"] == "b" else "🕯️"}</b> {esc(x["t"])}</p>' for x in pe)),
                         box('anniv', head + f'<p class="fev"><b>{"🌼" if pe[0]["k"] == "b" else "🕯️"}</b> {esc(pe[0]["t"])}</p>') if len(pe) > 1 else ''])

    # good word (a different one from the front page's)
    qs = load('tools/quotes.json', [])
    if qs:
        q = qs[(d.toordinal() + 17) % len(qs)]
        add('quote', [box('quote', f'<p class="fq">“{esc(q.get("t"))}”</p>' + (f'<p class="fqa">– {esc(q.get("a"))}</p>' if q.get('a') else ''))])

    pv = lib.get('proverbs', [])
    pvh = lambda l: ''.join(f'<p class="fpv"><b>{esc(x["t"])}</b><span>{esc(x["m"])}</span></p>' for x in l)
    add('proverb', [box('proverb', pvh(rot(pv, 4, seed * 3))), box('proverb', pvh(rot(pv, 2, seed * 3))), box('proverb', pvh(rot(pv, 1, seed * 3)))])

    hl = lib.get('health', []); hp = lib.get('helplines', [])
    tip = lambda l: ''.join(f'<p class="fht"><b>{esc(x["t"])}</b>{esc(x["b"])}</p>' for x in l)
    hpl = lambda n: '<div class="fhl">' + ''.join(f'<span>{esc(a)}<b>{esc(b)}</b></span>' for a, b in hp[:n]) + '</div>'
    add('health', [box('health', tip(rot(hl, 2, seed)) + hpl(8)), box('health', tip(rot(hl, 1, seed)) + hpl(4)), box('health', tip(rot(hl, 1, seed)))])

    gk = lib.get('gk', [])
    def gkb(n):
        l = rot(gk, n, seed * 5)
        return box('gk', '<ol class="fgk">' + ''.join(f'<li>{esc(x["q"])}</li>' for x in l) + '</ol>' +
                   upside('జవాబులు: ' + ' · '.join(f'{i + 1}) {esc(x["a"])}' for i, x in enumerate(l))))
    add('gk', [gkb(5), gkb(3), gkb(2)])

    fc = lib.get('facts', [])
    fch = lambda l: ''.join(f'<p class="ffc">{esc(x)}</p>' for x in l)
    add('fact', [box('fact', fch(rot(fc, 3, seed * 7))), box('fact', fch(rot(fc, 2, seed * 7))), box('fact', fch(rot(fc, 1, seed * 7)))])

    hr = lib.get('heritage', [])
    hrh = lambda l: ''.join(f'<div class="fhr"><h4>{esc(x["n"])}</h4><small>📍 {esc(x["w"])}</small><p>{esc(x["b"])}</p></div>' for x in l)
    add('heritage', [box('heritage', hrh(rot(hr, 2, seed * 11))), box('heritage', hrh(rot(hr, 1, seed * 11)))])

    g9, a9 = sudoku(9, seed); g6, a6 = sudoku(6, seed)
    add('sudoku', [box('sudoku', '<p class="fsd">ప్రతి అడ్డు వరుస, నిలువు వరుస, 3×3 గడిలో 1 నుంచి 9 వరకు అంకెలు ఒక్కసారే రావాలి.</p>' + g9 + upside('జవాబు: ' + a9)),
                   box('sudoku', '<p class="fsd">ప్రతి వరుసలో, 2×3 గడిలో 1 నుంచి 6 అంకెలు ఒక్కసారే.</p>' + g6 + upside('జవాబు: ' + a6))])

    rd = lib.get('riddles', [])
    def rdb(n):
        l = rot(rd, n, seed * 13)
        return box('riddle', '<ol class="fgk">' + ''.join(f'<li>{esc(x["q"])}</li>' for x in l) + '</ol>' +
                   upside('జవాబులు: ' + ' · '.join(f'{i + 1}) {esc(x["a"])}' for i, x in enumerate(l))))
    add('riddle', [rdb(4), rdb(2), rdb(1)])

    # our own notices (at most settings.max_promos per edition, chosen by the layout script)
    add('promo', [box('promo', '<div class="fqr"><img src="/qr.png" alt=""><div><h4>ప్రతి 30 నిమిషాలకు తాజా వార్తలు</h4><p>మీ జిల్లా వార్తలు, ఉద్యోగాలు, మండీ ధరలు – Swipe2News యాప్‌లో ఉచితంగా.</p><p class="fct">swipe2news.com</p></div></div>', cls='pr')])
    add('reporter', [box('reporter', '<h4>మీ ఊరి రిపోర్టర్ అవ్వండి</h4><p>మీ గ్రామం, మండలం వార్తలు పంపండి – పరిశీలించి ప్రచురిస్తాం.</p><p class="fct">swipe2news.com/reporter/join.html</p>', cls='pr')])
    ch = lib.get('district_channels', {}) or {}
    if ch:
        try:
            import qrcode, qrcode.image.svg
            def qsvg(u):
                im = qrcode.make(u, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
                return im.to_string(encoding='unicode')
            items = list(ch.items())
            cell = lambda l: '<div class="fch">' + ''.join(f'<figure>{qsvg(u)}<figcaption>{esc(n)}</figcaption></figure>' for n, u in l) + '</div>'
            add('channels', [box('channels', cell(rot(items, 6, seed)) + '<p class="fsd">స్కాన్ చేసి మీ జిల్లా ఛానెల్‌లో చేరండి.</p>', cls='pr'),
                             box('channels', cell(rot(items, 2, seed)), cls='pr')])
        except Exception:
            pass
    add('bizad', [box('bizad', '<h4>ఈ స్థలం మీ ప్రకటన కోసం</h4><p>మీ దుకాణం, వ్యాపారం, సేవల ప్రకటన జనధ్వని ఈ-పేపర్, Swipe2News యాప్‌లో.</p><p class="fct">📞 +91 70326 56422 · swipe2news@gmail.com</p>', cls='pr')])

    # paid first, then priority; ties change order every day so the paper does not look the same daily
    rnd = random.Random(seed)
    for x in out: x['r'] = rnd.random()
    out.sort(key=lambda x: (0 if x['k'].startswith('paid:') else 1, x['pri'], x['r']))
    for x in out: x.pop('r', None)
    return {'list': out, 'min_col_mm': st.get('min_col_mm', 34), 'min_row_mm': st.get('min_row_mm', 30), 'max_promos': st.get('max_promos', 2)}


if __name__ == '__main__':
    import sys
    b = build(sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat())
    for x in b['list']: print(x['pri'], x['k'], len(x['v']), 'promo' if x['promo'] else '')
