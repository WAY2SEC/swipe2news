#!/usr/bin/env python3
"""Swipe2News birthday greetings for leaders (PM, TG/AP CMs, Dy CMs, ministers, MLAs, MPs).

Data: leaders/birthdays.json  (see its "about" field)

  python3 tools/birthday.py due   [--date YYYY-MM-DD]   # who has a birthday that day (verified ones are postable)
  python3 tools/birthday.py render <id> [--date ...]     # poster only -> photos/bday-<year>-<id>.jpg (+ -wide.jpg)
  python3 tools/birthday.py post   <id> [--date ...]     # render + add story to news.json and archive/<date>.json
  python3 tools/birthday.py stats                        # how many birthdays are known / verified

Poster follows the user's template (Swipe2News logo, Telugu role + name, "జన్మదిన శుభాకాంక్షలు!",
Telugu wish, "Birthday Greetings to", English role, maroon name ribbon, English wish).
Same words for every leader and every party. Leader photos are used ONLY when the user has
supplied one (field "photo"); otherwise a drawn cake/balloon illustration is used.
"""
import json, os, sys, math, random, datetime, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'tools', 'fonts')
DATA = os.path.join(ROOT, 'leaders', 'birthdays.json')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

MAROON = (139, 16, 34); MAROON_D = (100, 8, 22); NAVY = (18, 40, 74)
GOLD = (201, 152, 52); GOLD_L = (246, 212, 138); INK = (30, 30, 34)
W, H = 1200, 1312

STATE = {
    'TG': dict(te='తెలంగాణ', en='Telangana', hi='तेलंगाना'),
    'AP': dict(te='ఆంధ్రప్రదేశ్', en='Andhra Pradesh', hi='आंध्र प्रदेश'),
    'IN': dict(te='దేశ', en='India', hi='देश'),
}


def F(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size, layout_engine=ImageFont.Layout.RAQM)
    if wght:
        try:
            f.set_variation_by_axes([wght, 100])
        except Exception:
            pass
    return f


def tel(size, wght=700): return F('NotoSansTelugu.ttf', size, wght)
def disp(size): return F('Ramabhadra-Regular.ttf', size)
def pf(size): return F('PlayfairDisplay-Bold.ttf', size)
def pfi(size): return F('PlayfairDisplay-BoldItalic.ttf', size)


def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]


def fit(d, s, maker, size, maxw, minsize=18):
    while size > minsize and tw(d, s, maker(size)) > maxw:
        size -= 2
    return maker(size)


def center(d, cx, y, s, f, fill, stroke=0, sfill=None):
    b = d.textbbox((0, 0), s, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y - b[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return y + (b[3] - b[1])


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def divider(d, cx, y, half=170):
    d.line([(cx - half, y), (cx - 22, y)], fill=GOLD, width=3)
    d.line([(cx + 22, y), (cx + half, y)], fill=GOLD, width=3)
    for dx in (-half, half):
        d.ellipse([cx + dx - 4, y - 4, cx + dx + 4, y + 4], fill=GOLD)
    d.polygon([(cx, y - 14), (cx + 12, y), (cx, y + 14), (cx - 12, y)], fill=GOLD)
    d.polygon([(cx, y - 7), (cx + 6, y), (cx, y + 7), (cx - 6, y)], fill=(255, 244, 214))


def background():
    im = Image.new('RGB', (W, H), (255, 252, 246))
    px = im.load()
    for y in range(H):
        t = y / H
        r = int(255 - 6 * t); g = int(248 + 6 * t - 10 * max(0, t - .7)); b = int(236 + 16 * t)
        for x in range(W):
            px[x, y] = (r, min(255, g), min(255, b))
    glow = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse([520, -260, 1500, 560], fill=120); gd.ellipse([-300, 500, 520, 1200], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    im = Image.composite(Image.new('RGB', (W, H), (255, 231, 178)), im, glow)
    # faint sun rays
    rays = Image.new('L', (W, H), 0); rd = ImageDraw.Draw(rays)
    ox, oy = 1150, 40
    for i in range(26):
        a1 = math.radians(90 + i * 7); a2 = a1 + math.radians(3)
        rd.polygon([(ox, oy), (ox + 1800 * math.cos(a1), oy + 1800 * math.sin(a1)),
                    (ox + 1800 * math.cos(a2), oy + 1800 * math.sin(a2))], fill=20)
    rays = rays.filter(ImageFilter.GaussianBlur(6))
    im = Image.composite(Image.new('RGB', (W, H), (255, 214, 140)), im, rays)
    return im


def bottom_band(im, d):
    # maroon wave with gold edge
    pts = []
    for x in range(0, W + 1, 10):
        pts.append((x, 1232 - 34 * math.sin((x / W) * math.pi * 0.9 + 0.3) + 18 * (x / W)))
    gold = pts + [(W, H), (0, H)]
    d.polygon([(x, y - 9) for x, y in pts] + [(W, H), (0, H)], fill=GOLD)
    d.polygon([(x, y - 3) for x, y in pts] + [(W, H), (0, H)], fill=GOLD_L)
    d.polygon(gold, fill=MAROON)
    d.polygon([(x, y + 26) for x, y in pts] + [(W, H), (0, H)], fill=MAROON_D)
    f = pf(26)
    s = 'swipe2news.com   •   WhatsApp 70326 56422'
    center(d, W / 2, H - 52, s, f, GOLD_L)


def balloon(d, x, y, r, col):
    d.line([(x, y + r * 1.25), (x + 6, y + r * 1.25 + 60), (x - 4, y + r * 1.25 + 120)], fill=(170, 150, 120), width=2)
    d.ellipse([x - r, y - r * 1.2, x + r, y + r * 1.2], fill=col)
    d.polygon([(x - 7, y + r * 1.25), (x + 7, y + r * 1.25), (x, y + r * 1.12)], fill=col)
    hl = tuple(min(255, c + 70) for c in col)
    d.ellipse([x - r * .55, y - r * .85, x - r * .15, y - r * .35], fill=hl)


def illustration(im):
    """Drawn birthday art for leaders without a user-supplied photo."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    cx, cy, R = 285, 690, 230
    # halo + rings
    halo = Image.new('L', (W, H), 0); ImageDraw.Draw(halo).ellipse([cx - R - 60, cy - R - 60, cx + R + 60, cy + R + 60], fill=150)
    halo = halo.filter(ImageFilter.GaussianBlur(45))
    im.paste(Image.new('RGB', (W, H), (255, 236, 190)), (0, 0), halo)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 250, 238, 255), outline=GOLD + (255,), width=8)
    d.ellipse([cx - R + 16, cy - R + 16, cx + R - 16, cy + R - 16], outline=GOLD_L + (255,), width=3)
    for i in range(36):
        a = math.radians(i * 10)
        x, y = cx + (R + 22) * math.cos(a), cy + (R + 22) * math.sin(a)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD + (255,))
    # cake
    def tier(top, h, w, col, icing):
        d.rounded_rectangle([cx - w / 2, top, cx + w / 2, top + h], 14, fill=col)
        d.rounded_rectangle([cx - w / 2 - 4, top - 6, cx + w / 2 + 4, top + 16], 10, fill=icing)
        n = int(w // 38)
        for k in range(n):
            x = cx - w / 2 + 19 + k * (w - 38) / max(1, n - 1)
            d.ellipse([x - 13, top + 4, x + 13, top + 34], fill=icing)
    tier(750, 110, 300, (139, 16, 34, 255), (255, 246, 230, 255))
    tier(660, 92, 220, (186, 46, 62, 255), (255, 246, 230, 255))
    tier(582, 80, 150, (139, 16, 34, 255), (255, 246, 230, 255))
    for k, x in enumerate((-110, -55, 0, 55, 110)):
        d.ellipse([cx + x - 7, 800, cx + x + 7, 814], fill=GOLD_L + (255,))
    for x in (-125, -62, 62, 125):
        d.ellipse([cx + x - 6, 712, cx + x + 6, 724], fill=GOLD_L + (255,))
    d.rounded_rectangle([cx - 200, 858, cx + 200, 876], 9, fill=GOLD + (255,))
    # candles
    for x in (-40, 0, 40):
        d.rounded_rectangle([cx + x - 7, 522, cx + x + 7, 582], 4, fill=(18, 40, 74, 255))
        for s in range(3):
            d.line([(cx + x - 7, 532 + s * 16), (cx + x + 7, 540 + s * 16)], fill=(255, 255, 255, 255), width=3)
        d.ellipse([cx + x - 10, 488, cx + x + 10, 520], fill=(255, 176, 40, 255))
        d.ellipse([cx + x - 5, 500, cx + x + 5, 518], fill=(255, 238, 150, 255))
    im.paste(layer, (0, 0), layer)
    d2 = ImageDraw.Draw(im)
    balloon(d2, 95, 330, 48, (190, 30, 50)); balloon(d2, 175, 260, 44, GOLD); balloon(d2, 60, 470, 38, (18, 40, 74))
    random.seed(7)
    cols = [MAROON, GOLD, NAVY, (230, 120, 60)]
    for _ in range(46):
        x = random.randint(20, 540); y = random.randint(380, 1100)
        if (x - cx) ** 2 + (y - cy) ** 2 < (R + 40) ** 2: continue
        c = random.choice(cols); s = random.randint(5, 10)
        if random.random() < .5: d2.ellipse([x, y, x + s, y + s], fill=c)
        else: d2.polygon([(x, y), (x + s * 1.6, y + 3), (x + s, y + s)], fill=c)


def paste_photo(im, path):
    """User-supplied photo on the left, faded into the background (faces kept whole: fit by height, no crop of head)."""
    ph = Image.open(path).convert('RGB')
    box_w, box_h, top = 600, 1110, 100
    s = max(box_w / ph.width, box_h / ph.height)
    ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    left = (ph.width - box_w) // 2
    ph = ph.crop((left, 0, left + box_w, box_h))  # keep the top (head) of the photo
    mask = Image.new('L', (box_w, box_h), 255); md = mask.load()
    for y in range(box_h):
        for x in range(box_w):
            a = 1.0
            if x > box_w - 170: a *= max(0, (box_w - x) / 170)
            if y > box_h - 220: a *= max(0, (box_h - y) / 220)
            md[x, y] = int(255 * a)
    im.paste(ph, (0, top), mask)


def poster(L, date):
    st = STATE.get(L['state'], STATE['IN'])
    im = background()
    if L.get('photo') and os.path.exists(os.path.join(ROOT, L['photo'])):
        paste_photo(im, os.path.join(ROOT, L['photo']))
    else:
        illustration(im)
    d = ImageDraw.Draw(im)
    bottom_band(im, d)
    cx, maxw = 868, 600
    logo = Image.open(os.path.join(ROOT, 'logo.png')).convert('RGBA')
    lw = 470; logo = logo.resize((lw, int(logo.height * lw / logo.width)))
    im.paste(logo, (int(cx - lw / 2), 46), logo)
    d.line([(cx - 250, 152), (cx + 250, 152)], fill=(205, 40, 50), width=2)

    y = 190
    role = L['te']['role']
    y = center(d, cx, y, role, fit(d, role, lambda s: tel(s, 700), 40, maxw), INK) + 18
    nm = L['te']['name'] + ' గారికి'
    y = center(d, cx, y, nm, fit(d, nm, disp, 62, maxw + 20), MAROON) + 24
    divider(d, cx, y); y += 26
    y = center(d, cx, y, 'జన్మదిన', disp(104), NAVY) + 12
    y = center(d, cx, y, 'శుభాకాంక్షలు!', fit(d, 'శుభాకాంక్షలు!', disp, 94, maxw), MAROON) + 14
    # brush swoosh
    d.arc([cx - 170, y - 34, cx + 170, y + 22], 15, 165, fill=MAROON, width=5)
    y += 24
    place = st['te']
    lines = [f'ప్రజల సంక్షేమం, {place} సమగ్ర అభివృద్ధి కోసం', 'మీ సేవలు మరింత విస్తరించాలని,',
             'మీకు ఆయురారోగ్యాలు, సుదీర్ఘ ప్రజాసేవా జీవితం', 'లభించాలని మనస్ఫూర్తిగా కోరుకుంటున్నాం.']
    f = min((fit(d, l, lambda z: tel(z, 500), 28, maxw - 20) for l in lines), key=lambda q: q.size)
    for line in lines:
        y = center(d, cx, y, line, f, INK) + 9
    y += 12; divider(d, cx, y); y += 22
    y = center(d, cx, y, 'Birthday Greetings to', pfi(42), MAROON) + 12
    post = ("Hon'ble " + L['post']) if L['house'] in ('pm',) or 'Minister' in L['post'] or 'Speaker' in L['post'] else L['post']
    f = fit(d, post, pf, 33, maxw + 40)
    for line in wrap(d, post, f, maxw + 40):
        y = center(d, cx, y, line, f, INK) + 8
    y += 14
    # ribbon
    title = ('Smt. ' if L.get('female') else 'Shri ') + L['show'] + (' Ji' if L['house'] == 'pm' else ' Garu')
    rf = fit(d, title, pf, 52, 640, 26)
    rw = max(520, tw(d, title, rf) + 90); rh = 86
    x0, x1 = cx - rw / 2, cx + rw / 2
    x0 = max(x0, 450); x1 = x0 + rw
    if x1 > W - 22: x1 = W - 22; x0 = x1 - rw
    rcx = (x0 + x1) / 2
    shape = [(x0, y + rh / 2), (x0 + 30, y), (x1 - 30, y), (x1, y + rh / 2), (x1 - 30, y + rh), (x0 + 30, y + rh)]
    d.polygon([(px + (4 if px > rcx else -4), py + (-4 if py < y + rh / 2 else 4 if py > y + rh / 2 else 0)) for px, py in shape], fill=GOLD)
    d.polygon(shape, fill=MAROON)
    inner = [(x0 + 12, y + rh / 2), (x0 + 36, y + 8), (x1 - 36, y + 8), (x1 - 12, y + rh / 2), (x1 - 36, y + rh - 8), (x0 + 36, y + rh - 8)]
    d.line(inner + [inner[0]], fill=GOLD_L, width=2)
    b = d.textbbox((0, 0), title, font=rf)
    d.text((rcx - (b[2] - b[0]) / 2 - b[0], y + (rh - (b[3] - b[1])) / 2 - b[1] - 2), title, font=rf, fill=GOLD_L)
    y += rh + 16
    ew = f"Wishing you good health, happiness and many more years of dedicated service to the people of {st['en']}."
    f = pfi(26)
    for line in wrap(d, ew, f, maxw + 20):
        y = center(d, cx, y, line, f, INK) + 6
    if y > 1190:
        print('WARNING: text runs into the bottom band (y=%d) – shorten name/role' % y, file=sys.stderr)
    return im


def wide(p):
    w = Image.new('RGB', (2099, 1312)); px = w.load()
    for x in range(2099):
        t = x / 2099
        c = (int(22 + 30 * t), int(42 - 4 * t), int(82 + 18 * t))
        for y in range(1312): px[x, y] = c
    sh = Image.new('L', (2099, 1312), 0); ImageDraw.Draw(sh).rectangle([450 + 10, 10, 450 + 1200 + 10, 1312], fill=160)
    sh = sh.filter(ImageFilter.GaussianBlur(18)); w.paste((5, 10, 25), (0, 0), sh)
    w.paste(p, (450, 0))
    return w


def load():
    return json.load(open(DATA, encoding='utf-8'))


def save(doc):
    doc['updated'] = datetime.datetime.now(IST).strftime('%Y-%m-%d')
    json.dump(doc, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def md(L):
    return (L.get('dob') or '')[-5:]


def get(doc, i):
    for L in doc['leaders']:
        if L['id'] == i: return L
    sys.exit('no leader with id ' + i)


def render(L, date):
    yr = date[:4]
    p = poster(L, date)
    base = f'photos/bday-{yr}-{L["id"]}'
    p.save(os.path.join(ROOT, base + '.jpg'), quality=90)
    wide(p).save(os.path.join(ROOT, base + '-wide.jpg'), quality=86)
    return base


def story(L, date, base):
    st = STATE.get(L['state'], STATE['IN'])
    now = datetime.datetime.now(IST)
    dd = datetime.date.fromisoformat(date).strftime('%d.%m.%Y')
    te, hi = L['te'], L['hi']
    pre_en = 'Smt.' if L.get('female') else 'Shri'
    hon = "Hon'ble " if (L['house'] == 'pm' or 'Minister' in L['post'] or 'Speaker' in L['post']) else ''
    tname = te['name']; short = tname.replace('శ్రీమతి ', '').replace('శ్రీ ', '')
    sec = ['india'] if L['state'] == 'IN' else ['telangana']
    s = {
        'cat': '🎂 జన్మదిన శుభాకాంక్షలు', 'col': '--c-gov', 'art': 'land', 'stat': '🎂',
        'statl': f'{short} గారికి జన్మదిన శుభాకాంక్షలు',
        'h': f'{te["role"]} {tname} గారికి జన్మదిన శుభాకాంక్షలు',
        'p': (f'{te["role"]} గౌరవ {tname} గారికి జన్మదిన శుభాకాంక్షలు! మీరు ఆయురారోగ్యాలతో, సుఖసంతోషాలతో ఉండాలని, '
              f'{"దేశ" if L["state"] == "IN" else st["te"]} ప్రజలకు మరెన్నో సంవత్సరాలు సేవలందించాలని ఆకాంక్షిస్తున్నాం. – Swipe2News'),
        'src': 'Swipe2News', 'url': '', 'sec': sec, 'st': L['state'] if L['state'] != 'IN' else 'IN',
        'place': {'TG': 'TS', 'AP': 'AP'}.get(L['state'], 'IN'), 'loc': '',
        'pts': [f'🎂 {short} గారికి జన్మదిన శుభాకాంక్షలు', 'ఆయురారోగ్యాలతో ప్రజాసేవ కొనసాగించాలని ఆకాంక్ష', '— Team SWIPE2NEWS.COM'],
        'why': f'ప్రజల సంక్షేమం, {st["te"]} సమగ్ర అభివృద్ధి కోసం మీ సేవలు మరింత విస్తరించాలని కోరుకుంటున్నాం.',
        'en': {'cat': '🎂 Birthday wishes', 'stat': '🎂', 'statl': f'Happy Birthday to {L["show"]}',
               'h': f'Happy Birthday to {hon}{L["post"]} {pre_en} {L["show"]}',
               'p': (f'Wishing {hon}{L["post"]} {pre_en} {L["show"]} Garu a very Happy Birthday! May you be blessed with good health, '
                     f'happiness and many more years of service to the people of {st["en"]}. — Team Swipe2News'),
               'pts': [f'🎂 Happy Birthday to {L["show"]}', 'Wishing good health and many more years of service', '— Team SWIPE2NEWS.COM'],
               'why': f'We wish your service grows stronger for people\'s welfare and the all-round development of {st["en"]}.'},
        'hi': {'cat': '🎂 जन्मदिन की शुभकामनाएँ', 'stat': '🎂', 'statl': f'{hi["name"]} को जन्मदिन की शुभकामनाएँ',
               'h': f'{hi["role"]} {hi["name"]} को जन्मदिन की हार्दिक शुभकामनाएँ',
               'p': (f'{hi["role"]} माननीय {hi["name"]} को जन्मदिन की हार्दिक शुभकामनाएँ! आप स्वस्थ और प्रसन्न रहें और कई वर्षों तक '
                     f'{st["hi"]} की जनता की सेवा करते रहें। — टीम Swipe2News'),
               'pts': [f'🎂 {hi["name"]} को जन्मदिन की शुभकामनाएँ', 'अच्छे स्वास्थ्य और लंबी जनसेवा की कामना', '— टीम SWIPE2NEWS.COM'],
               'why': f'जनकल्याण और {st["hi"]} के समग्र विकास के लिए आपकी सेवा और मज़बूत हो, यही कामना है।'},
        'd': dd, 't': now.strftime('%H:%M'), 'img': base + '-wide.jpg', 'imgfy': 0.3, 'imgfx': 0.5,
        'local': True, 'bday': L['id'],
    }
    return s


def add_story(s, date):
    nj = os.path.join(ROOT, 'news.json'); doc = json.load(open(nj, encoding='utf-8'))
    doc['stories'] = [x for x in doc['stories'] if x.get('bday') != s['bday'] or x.get('d') != s['d']]
    doc['stories'].insert(0, s)
    json.dump(doc, open(nj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ap = os.path.join(ROOT, 'archive', date + '.json')
    if os.path.exists(ap):
        a = json.load(open(ap, encoding='utf-8'))
    else:
        a = {'date': datetime.date.fromisoformat(date).strftime('%d.%m.%Y'), 'iso': date, 'count': 0, 'stories': []}
    a['stories'] = [x for x in a['stories'] if x.get('bday') != s['bday']]
    a['stories'].insert(0, s); a['count'] = len(a['stories'])
    json.dump(a, open(ap, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ip = os.path.join(ROOT, 'archive', 'index.json')
    idx = json.load(open(ip, encoding='utf-8')) if os.path.exists(ip) else {'dates': []}
    idx['dates'] = [e for e in idx['dates'] if e.get('iso') != date] + [{'iso': date, 'date': a['date'], 'count': a['count']}]
    idx['dates'].sort(key=lambda e: e['iso'], reverse=True)
    json.dump(idx, open(ip, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['due', 'render', 'post', 'stats'])
    ap.add_argument('id', nargs='?')
    ap.add_argument('--date', default=datetime.datetime.now(IST).strftime('%Y-%m-%d'))
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    doc = load()
    if a.cmd == 'stats':
        Ls = doc['leaders']
        print(len(Ls), 'leaders;', sum(1 for L in Ls if L.get('dob')), 'with a date;', sum(1 for L in Ls if L.get('verified')), 'verified')
        return
    if a.cmd == 'due':
        m = a.date[5:]
        for L in doc['leaders']:
            if md(L) == m:
                ok = L.get('verified') and L.get('last_posted') != a.date[:4]
                print(('POST  ' if ok else 'CHECK ') + L['id'], '|', L['show'], '|', L['post'], '| verified=%s last_posted=%s te=%s hi=%s' % (
                    L.get('verified'), L.get('last_posted'), bool(L['te']['name']), bool(L['hi']['name'])))
        return
    L = get(doc, a.id)
    for k in ('te', 'hi'):
        if not (L[k]['name'] and L[k]['role']):
            sys.exit(f'fill {k}.name and {k}.role for {L["id"]} in leaders/birthdays.json first')
    if a.cmd == 'render':
        print(render(L, a.date) + '.jpg'); return
    if not a.force:
        if not L.get('verified'): sys.exit('date not verified – verify it from a reputable source first')
        if md(L) != a.date[5:]: sys.exit('not this leader\'s birthday (%s)' % L.get('dob'))
        if L.get('last_posted') == a.date[:4]: sys.exit('already posted this year')
    base = render(L, a.date)
    add_story(story(L, a.date, base), a.date)
    L['last_posted'] = a.date[:4]; save(doc)
    print('posted', L['id'], base + '.jpg')


if __name__ == '__main__':
    main()
