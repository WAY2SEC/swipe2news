#!/usr/bin/env python3
"""Search-friendly static pages for Swipe2News (13 Nov 2026).

Writes, from news.json + the last days of archive/ + jobs.json:
  en/index.html, te/index.html, hi/index.html  real-HTML news homepages (hreflang, canonical, OG, JSON-LD)
  index.html                                   refreshes the server-rendered block between <!--SSR--> and <!--/SSR-->
  sitemap.xml                                  root sitemap (home, language pages, static pages, every story)
  robots.txt                                   points to the sitemaps
Run by tools/build_previews.py at the end of every build; can also be run alone: python3 tools/build_lang.py
"""
import datetime, glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://swipe2news.com"
LANGS = ["en", "te", "hi"]
e = lambda t: html.escape(str(t if t is not None else ""), quote=True)

UI = {
 "en": {"name": "English", "html": "en", "title": "Swipe2News – Telangana, Andhra Pradesh, India & World news in short",
        "desc": "Short, sourced news from Telangana and Andhra Pradesh districts, India and the world. Every story links to its original source. Know More. Scroll Less.",
        "top": "Top stories", "latest": "Latest updates", "sec": {"telangana": "Telangana", "ap": "Andhra Pradesh", "india": "India", "world": "World", "business": "Business & Tech", "fact": "Fact checks"},
        "local": "District news", "jobs": "Jobs & deadlines", "src": "Source", "read": "Read story", "cards": "Swipe cards", "app": "Get the Swipe2News app",
        "appd": "Free. One story per screen, listen in your language, WhatsApp sharing and morning briefing.", "install": "Install the app", "channel": "WhatsApp channel",
        "why": "Why it matters", "last": "Last date", "more": "More news", "about": "About", "policy": "Editorial policy", "corr": "Corrections", "contact": "Contact", "privacy": "Privacy", "terms": "Terms",
        "tag": "Know More. Scroll Less.", "upd": "Updated", "lbl": {"fact": "FACT", "claim": "CLAIM", "opinion": "OPINION", "misleading": "MISLEADING"}},
 "te": {"name": "తెలుగు", "html": "te", "title": "Swipe2News – తెలంగాణ, ఆంధ్రప్రదేశ్, దేశం, ప్రపంచ వార్తలు క్లుప్తంగా",
        "desc": "తెలంగాణ, ఆంధ్రప్రదేశ్ జిల్లాల వార్తలు, దేశం, ప్రపంచ ముఖ్య వార్తలు – క్లుప్తంగా, ప్రతి వార్తకు అసలు మూలంతో. తక్కువ స్క్రోల్, ఎక్కువ సమాచారం.",
        "top": "ముఖ్య వార్తలు", "latest": "తాజా అప్‌డేట్‌లు", "sec": {"telangana": "తెలంగాణ", "ap": "ఆంధ్రప్రదేశ్", "india": "దేశం", "world": "ప్రపంచం", "business": "బిజినెస్ & టెక్", "fact": "ఫ్యాక్ట్ చెక్"},
        "local": "జిల్లా వార్తలు", "jobs": "ఉద్యోగాలు · చివరి తేదీలు", "src": "మూలం", "read": "వార్త చదవండి", "cards": "స్వైప్ కార్డులు", "app": "Swipe2News యాప్ పొందండి",
        "appd": "ఉచితం. ఒక్కో స్క్రీన్‌కు ఒక వార్త, మీ భాషలో వినండి, WhatsApp షేర్, ఉదయం బ్రీఫింగ్.", "install": "యాప్ ఇన్‌స్టాల్ చేయండి", "channel": "WhatsApp ఛానెల్",
        "why": "ఇది ఎందుకు ముఖ్యం", "last": "చివరి తేదీ", "more": "మరిన్ని వార్తలు", "about": "మా గురించి", "policy": "సంపాదకీయ విధానం", "corr": "సవరణలు", "contact": "సంప్రదించండి", "privacy": "గోప్యత", "terms": "నిబంధనలు",
        "tag": "తక్కువ స్క్రోల్, ఎక్కువ సమాచారం", "upd": "అప్‌డేట్", "lbl": {"fact": "వాస్తవం", "claim": "వాదన", "opinion": "అభిప్రాయం", "misleading": "తప్పుదోవ"}},
 "hi": {"name": "हिन्दी", "html": "hi", "title": "Swipe2News – तेलंगाना, आंध्र प्रदेश, देश और दुनिया की छोटी खबरें",
        "desc": "तेलंगाना और आंध्र प्रदेश के ज़िलों, देश और दुनिया की छोटी, स्रोत सहित खबरें। हर खबर के साथ मूल स्रोत का लिंक। कम स्क्रॉल, ज़्यादा जानकारी।",
        "top": "मुख्य खबरें", "latest": "ताज़ा अपडेट", "sec": {"telangana": "तेलंगाना", "ap": "आंध्र प्रदेश", "india": "देश", "world": "दुनिया", "business": "बिज़नेस और टेक", "fact": "फ़ैक्ट चेक"},
        "local": "ज़िले की खबरें", "jobs": "नौकरियाँ · अंतिम तिथियाँ", "src": "स्रोत", "read": "खबर पढ़ें", "cards": "स्वाइप कार्ड", "app": "Swipe2News ऐप पाएँ",
        "appd": "मुफ़्त। हर स्क्रीन पर एक खबर, अपनी भाषा में सुनें, WhatsApp शेयर, सुबह की ब्रीफ़िंग।", "install": "ऐप इंस्टॉल करें", "channel": "WhatsApp चैनल",
        "why": "यह क्यों अहम है", "last": "अंतिम तिथि", "more": "और खबरें", "about": "हमारे बारे में", "policy": "संपादकीय नीति", "corr": "सुधार", "contact": "संपर्क", "privacy": "गोपनीयता", "terms": "शर्तें",
        "tag": "कम स्क्रॉल, ज़्यादा जानकारी", "upd": "अपडेट", "lbl": {"fact": "तथ्य", "claim": "दावा", "opinion": "राय", "misleading": "भ्रामक"}},
}
CHANNEL = "https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138"


def load(rel, d):
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f: return json.load(f)
    except Exception: return d


def sid(s):
    if s.get("_sid"): return s["_sid"]
    h = 5381
    b = ((s.get("url") or "") + "|" + (s.get("h") or "")).encode("utf-16-le")
    for i in range(0, len(b), 2):  # JavaScript charCodeAt works on UTF-16 code units
        h = ((h << 5) + h + (b[i] | (b[i + 1] << 8))) & 0xFFFFFFFF
    # JavaScript works on signed 32-bit, then >>>0 back to unsigned: same digits
    n, out = h, ""
    digs = "0123456789abcdefghijklmnopqrstuvwxyz"
    while True:
        n, r = divmod(n, 36); out = digs[r] + out
        if not n: break
    return out


def ts(s):
    if s.get("pub"):
        try: return datetime.datetime.fromisoformat(s["pub"]).timestamp()
        except Exception: pass
    m = re.match(r"(\d\d)\.(\d\d)\.(\d{4})$", s.get("d") or ""); t = re.match(r"(\d\d):(\d\d)$", s.get("t") or "")
    if not m: return 0
    try: return datetime.datetime(int(m[3]), int(m[2]), int(m[1]), int(t[1]) if t else 12, int(t[2]) if t else 0, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30))).timestamp()
    except Exception: return 0


def iso(s):
    t = ts(s)
    return datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=5, minutes=30))).isoformat(timespec="minutes") if t else ""


def tr(s, l):
    o = dict(s)
    x = s.get(l) if l != "te" else None
    if isinstance(x, dict):
        for k in ("h", "p", "why", "cat", "statl", "pts"):
            if x.get(k): o[k] = x[k]
    o["_ok"] = l == "te" or (isinstance(x, dict) and bool(x.get("h")))
    return o


def secs(s): return s.get("sec") if isinstance(s.get("sec"), list) else ([s["sec"]] if s.get("sec") else [])


def stories():
    news = load("news.json", {}).get("stories", [])
    idx = load("archive/index.json", {}).get("dates", [])[:3]
    arch = []
    for d in idx: arch += load(f"archive/{d.get('iso')}.json", {}).get("stories", [])
    seen, out = set(), []
    for s in news + arch:
        k = sid(s)
        if k in seen or s.get("wd"): continue
        seen.add(k); s["_id"] = k; out.append(s)
    out.sort(key=ts, reverse=True)
    return out


PLACES = {}
def place_names():
    try:
        t = open(os.path.join(ROOT, "tools", "web_template.html"), encoding="utf-8").read()
        m = re.search(r"const PLACES=(\{[^}]*\})", t)
        if m:
            for k, v in re.findall(r"(\w+):'([^']*)'", m.group(1)): PLACES[k] = v
    except Exception: pass


CSS = """*{box-sizing:border-box}body{margin:0;background:#F8F9FB;color:#202124;font-family:Inter,'Noto Sans Telugu','Noto Sans Devanagari',system-ui,sans-serif;line-height:1.55}
a{color:inherit;text-decoration:none}.wrap{max-width:1160px;margin:0 auto;padding:0 18px}
header{background:#fff;border-bottom:1px solid #E6E8EC;position:sticky;top:0;z-index:5}.hb{display:flex;align-items:center;gap:14px;min-height:62px}
.hb img{height:30px;width:auto}.tg{font:600 13px Outfit,sans-serif;color:#5F6368;border-left:1px solid #E6E8EC;padding-left:12px}.sp{flex:1}
.lg{display:flex;gap:4px}.lg a{padding:6px 10px;border-radius:16px;font:700 13px Outfit,'Noto Sans Telugu',sans-serif;color:#4A0E3F;border:1px solid #E6E8EC}.lg a[aria-current]{background:#4A0E3F;color:#fff;border-color:#4A0E3F}
.btn{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:20px;background:#4A0E3F;color:#fff;font:700 14px Outfit,'Noto Sans Telugu',sans-serif}
nav.cat{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;border-top:1px solid #E6E8EC}nav.cat a{padding:12px 12px;font:700 14.5px Outfit,'Noto Sans Telugu',sans-serif;white-space:nowrap}
h1{font:800 26px/1.25 Outfit,'Noto Sans Telugu',sans-serif;margin:22px 0 14px}h2{font:800 21px Outfit,'Noto Sans Telugu',sans-serif;margin:30px 0 12px;display:flex;align-items:center;gap:10px}h2:before{content:"";width:4px;height:22px;border-radius:2px;background:#4A0E3F}
.lead{display:grid;grid-template-columns:1.4fr 1fr;gap:18px}@media(max-width:820px){.lead{grid-template-columns:1fr}.tg{display:none}}
.card{background:#fff;border:1px solid #E6E8EC;border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:8px;box-shadow:0 1px 2px rgba(32,33,36,.05)}
.card h3{margin:0;font:700 17px/1.4 Outfit,'Noto Sans Telugu','Noto Sans Devanagari',sans-serif}.big h3{font-size:23px}.card p{margin:0;font-size:15px;color:#3C4043}
.m{font-size:12.5px;color:#5F6368;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.m b{color:#202124}
.l{font-size:10.5px;font-weight:800;border-radius:6px;padding:2px 7px;letter-spacing:.03em}.l.fact{background:#0E7A3E;color:#fff}.l.claim{background:#F5A23A;color:#2E0827}.l.opinion{border:1px solid #E6E8EC}.l.misleading{background:#B3261E;color:#fff}
.w{font-size:13.5px}.w b{color:#4A0E3F}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.list{display:flex;flex-direction:column}.list a{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #E6E8EC;font-weight:600;font-size:14.5px}.list a span{flex:none;color:#4A0E3F;font:700 12.5px Outfit,sans-serif;width:42px}
.dist{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}.dist .card h4{margin:0;font:800 14px Outfit,'Noto Sans Telugu',sans-serif;color:#4A0E3F}
.app{margin:34px 0;border-radius:22px;padding:24px;color:#fff;background:radial-gradient(120% 140% at 100% 0%,#6E2361 0,#4A0E3F 55%,#2E0827 100%);display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.app h2{color:#fff;margin:0}.app h2:before{background:#F5A23A}.app p{margin:6px 0 0;color:#E3D3DE}.app .b{display:flex;gap:10px;flex-wrap:wrap}.app .b a{background:#fff;color:#4A0E3F}.app .b a.wa{background:#0E7A3E;color:#fff}
footer{background:#fff;border-top:1px solid #E6E8EC;padding:22px 0 30px;font-size:14px;color:#5F6368}footer nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px}footer nav a{color:#4A0E3F;font-weight:600}"""


def card(s, U, l, big=False):
    k = s.get("lbl") if s.get("lbl") in U["lbl"] else ""
    lab = f'<span class="l {k}">{e(U["lbl"][k])}</span>' if k else ""
    why = f'<div class="w"><b>{e(U["why"])}:</b> {e(s.get("why"))}</div>' if s.get("why") else ""
    q = "" if l == "te" else f"?l={l}"
    return (f'<article class="card{" big" if big else ""}"><div class="m">{lab}<span>{e((s.get("cat") or "").strip())}</span><time datetime="{e(iso(s))}">{e(s.get("d"))} {e(s.get("t") or "")}</time></div>'
            f'<h3><a href="/s/{s["_id"]}{q}">{e(s.get("h"))}</a></h3><p>{e(s.get("p"))}</p>{why}'
            f'<div class="m">{e(U["src"])}: <b>{e(s.get("src") or "Swipe2News")}</b></div></article>')


def alternates(path_for):
    links = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{path_for(l)}">' for l in LANGS)
    return links + f'<link rel="alternate" hreflang="x-default" href="{SITE}/en/">'


def org_ld():
    return [
        {"@context": "https://schema.org", "@type": "NewsMediaOrganization", "name": "Swipe2News", "url": SITE + "/", "logo": SITE + "/icon-512.png",
         "slogan": "Know More. Scroll Less.", "sameAs": ["https://www.instagram.com/swipe2newsapp", CHANNEL],
         "publishingPrinciples": SITE + "/editorial-policy.html", "correctionsPolicy": SITE + "/editorial-policy.html#corrections"},
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Swipe2News", "url": SITE + "/", "inLanguage": ["te", "en", "hi"],
         "potentialAction": {"@type": "SearchAction", "target": SITE + "/?q={search_term_string}", "query-input": "required name=search_term_string"}},
        {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Swipe2News", "operatingSystem": "Android, iOS (web app)", "applicationCategory": "NewsApplication",
         "url": SITE + "/install.html", "image": SITE + "/icon-512.png", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"}},
    ]


def lang_page(l, S, jobs):
    U = UI[l]
    T = [tr(s, l) for s in S]
    T = [s for s in T if s["_ok"]] or [tr(s, "te") for s in S]
    used = set()
    def take(lst, n):
        out = []
        for s in lst:
            if s["_id"] in used: continue
            out.append(s); used.add(s["_id"])
            if len(out) >= n: break
        return out
    lead = take([s for s in T if s.get("brk")] + T, 1)
    side = take(T, 8)
    blocks = []
    def isap(s): return s.get("st") == "AP" or str(s.get("place", "")).startswith("ap-")
    groups = [("telangana", [s for s in T if s.get("st") == "TG" or (("telangana" in secs(s)) and not isap(s))]), ("ap", [s for s in T if isap(s)]),
              ("india", [s for s in T if s.get("st") not in ("TG", "AP", "WORLD") and "india" in secs(s)]), ("world", [s for s in T if s.get("st") == "WORLD" or "world" in secs(s)]),
              ("business", [s for s in T if set(secs(s)) & {"business", "ai", "innovation"}]), ("fact", [s for s in T if s.get("lbl") == "misleading"])]
    for k, lst in groups:
        got = take(lst, 6)
        if got: blocks.append((k, got))
    # district news
    by = {}
    for s in T:
        p = s.get("place") or ""
        if p in PLACES or p.startswith("ap-"): by.setdefault(p, []).append(s)
    dists = sorted(by.items(), key=lambda kv: -len(kv[1]))[:9]
    dhtml = "".join(f'<div class="card"><h4>📍 {e(PLACES.get(p) or (x[0].get("loc") or p))}</h4><div class="list">'
                    + "".join(f'<a href="/s/{s["_id"]}{"" if l == "te" else "?l=" + l}"><span>{e(s.get("t") or "")}</span>{e(s.get("h"))}</a>' for s in x[:4]) + "</div></div>" for p, x in dists)
    today = datetime.date.today()
    def dleft(j):
        m = re.match(r"(\d\d)\.(\d\d)\.(\d{4})$", j.get("last") or "")
        if not m: return None
        try: return (datetime.date(int(m[3]), int(m[2]), int(m[1])) - today).days
        except Exception: return None
    J = sorted([j for j in jobs if (dleft(j) or -1) >= 0], key=dleft)[:6]
    jh = "".join(f'<a href="/s/{sid({"url": j.get("url") or j.get("apply") or "", "h": j.get("h")})}"><span>{dleft(j)}d</span>{e((j.get(l) or {}).get("h") if l != "te" and isinstance(j.get(l), dict) else j.get("h"))} · {e(j.get("org") or "")} · {e(U["last"])} {e(j.get("last"))}</a>' for j in J)
    upd = iso(S[0]) if S else ""
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/s/{s['_id']}"} for i, s in enumerate((lead + side)[:10])]
    ld = org_ld() + [{"@context": "https://schema.org", "@type": "CollectionPage", "name": U["title"], "url": f"{SITE}/{l}/", "inLanguage": U["html"],
                      "dateModified": upd, "mainEntity": {"@type": "ItemList", "itemListElement": items}}]
    nav = "".join(f'<a href="#{k}">{e(U["sec"][k])}</a>' for k, _ in blocks) + (f'<a href="#local">{e(U["local"])}</a>' if dhtml else "") + (f'<a href="#jobs">{e(U["jobs"])}</a>' if jh else "")
    langs = "".join(f'<a href="/{x}/" hreflang="{x}"{" aria-current=page" if x == l else ""}>{e(UI[x]["name"])}</a>' for x in LANGS)
    secs_html = "".join(f'<section id="{k}"><h2>{e(U["sec"][k])}</h2><div class="grid">{"".join(card(s, U, l) for s in lst)}</div></section>' for k, lst in blocks)
    return f"""<!doctype html>
<html lang="{U['html']}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(U['title'])}</title>
<meta name="description" content="{e(U['desc'])}">
<meta name="robots" content="max-image-preview:large">
<link rel="canonical" href="{SITE}/{l}/">
{alternates(lambda x: f'/{x}/')}
<meta property="og:type" content="website"><meta property="og:site_name" content="Swipe2News"><meta property="og:title" content="{e(U['title'])}">
<meta property="og:description" content="{e(U['desc'])}"><meta property="og:url" content="{SITE}/{l}/"><meta property="og:image" content="{SITE}/og-image.jpg">
<meta property="og:locale" content="{ {'en': 'en_IN', 'te': 'te_IN', 'hi': 'hi_IN'}[l] }"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#4A0E3F"><link rel="icon" href="/favicon-48.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap"><div class="hb"><a href="/{l}/"><img src="/logo.png" alt="Swipe2News" width="152" height="30"></a><span class="tg">{e(U['tag'])}</span><span class="sp"></span>
<nav class="lg" aria-label="Language">{langs}</nav><a class="btn" href="/?cards=1&amp;l={l}">📱 {e(U['cards'])}</a></div>
<nav class="cat" aria-label="Sections">{nav}</nav></div></header>
<main class="wrap">
<h1>{e(U['top'])}</h1>
<div class="lead"><div>{"".join(card(s, U, l, True) for s in lead)}</div><div class="card"><h3>{e(U['latest'])}</h3><div class="list">
{"".join(f'<a href="/s/{s["_id"]}{"" if l == "te" else "?l=" + l}"><span>{e(s.get("t") or "")}</span>{e(s.get("h"))}</a>' for s in side)}
</div></div></div>
{secs_html}
{f'<section id="local"><h2>{e(U["local"])}</h2><div class="dist">{dhtml}</div></section>' if dhtml else ''}
{f'<section id="jobs"><h2>{e(U["jobs"])}</h2><div class="card"><div class="list">{jh}</div></div></section>' if jh else ''}
<section class="app" aria-label="{e(U['app'])}"><div style="flex:1;min-width:240px"><h2>{e(U['app'])}</h2><p>{e(U['appd'])}</p></div>
<div class="b"><a class="btn" href="/install.html">📲 {e(U['install'])}</a><a class="btn" href="/?cards=1&amp;l={l}">{e(U['cards'])}</a><a class="btn wa" href="{CHANNEL}" rel="noopener">{e(U['channel'])}</a></div></section>
</main>
<footer><div class="wrap"><b style="color:#202124">Swipe2News</b> – {e(U['tag'])} · {e(U['upd'])}: <time datetime="{e(upd)}">{e(upd.replace('T', ' ')[:16])}</time>
<nav><a href="/about.html">{e(U['about'])}</a><a href="/editorial-policy.html">{e(U['policy'])}</a><a href="/editorial-policy.html#corrections">{e(U['corr'])}</a><a href="/contact.html">{e(U['contact'])}</a><a href="/privacy.html">{e(U['privacy'])}</a><a href="/terms.html">{e(U['terms'])}</a></nav></div></footer>
</body>
</html>
"""


def ssr_block(S):
    """English headlines for the root page (search engines, link previews, no-JS readers); the app replaces it at once."""
    T = [tr(s, "en") for s in S[:24]]
    li = "".join(f'<li><a href="/s/{s["_id"]}?l=en">{e(s.get("h"))}</a> <small>{e(s.get("src") or "")} · {e(s.get("d"))} {e(s.get("t") or "")}</small></li>' for s in T)
    return ('<!--SSR--><div class="ssr" lang="en"><h1>Swipe2News – Telangana, Andhra Pradesh, India &amp; World news in short</h1>'
            '<p>Know More. Scroll Less. Short, sourced news from every district of Telangana and Andhra Pradesh, plus the most important news from India and the world – in Telugu, English and Hindi. Every story names and links its original source.</p>'
            '<p><a href="/en/">English news</a> · <a href="/te/">తెలుగు వార్తలు</a> · <a href="/hi/">हिन्दी खबरें</a> · <a href="/web/">Latest news website</a> · <a href="/install.html">Install the app</a> · <a href="/epaper/">E-paper</a> · <a href="/mandi/">Mandi prices</a> · <a href="/?jobs=1">Jobs</a></p>'
            f'<h2>Top stories</h2><ul>{li}</ul>'
            '<p class="ssrf"><a href="/about.html">About</a> · <a href="/editorial-policy.html">Editorial policy</a> · <a href="/editorial-policy.html#corrections">Corrections</a> · <a href="/contact.html">Contact</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a></p>'
            '<p class="ssrw">Loading news… · వార్తలు లోడ్ అవుతున్నాయి…</p></div><!--/SSR-->')


def main():
    place_names()
    S = stories()
    jobs = load("jobs.json", {}).get("jobs", [])
    for l in LANGS:
        os.makedirs(os.path.join(ROOT, l), exist_ok=True)
        out = lang_page(l, S, jobs); fp = os.path.join(ROOT, l, "index.html")
        if not os.path.exists(fp) or open(fp, encoding="utf-8").read() != out:
            open(fp, "w", encoding="utf-8").write(out)
    # root page: server-rendered English headlines + structured data
    ip = os.path.join(ROOT, "index.html"); app = open(ip, encoding="utf-8").read()
    if "<!--SSR-->" in app:
        new = re.sub(r"<!--SSR-->.*?<!--/SSR-->", lambda m: ssr_block(S), app, count=1, flags=re.S)
        ldtag = '<script type="application/ld+json" id="s2nld">' + json.dumps(org_ld(), ensure_ascii=False) + "</script>"
        new = re.sub(r'<script type="application/ld\+json" id="s2nld">.*?</script>', lambda m: ldtag, new, count=1, flags=re.S)
        if new != app: open(ip, "w", encoding="utf-8").write(new)
    # sitemap.xml at the root
    urls = [(SITE + "/", None)] + [(f"{SITE}/{l}/", iso(S[0]) if S else None) for l in LANGS] + \
           [(SITE + p, None) for p in ("/web/", "/mandi/", "/epaper/", "/install.html", "/about.html", "/editorial-policy.html", "/contact.html", "/privacy.html", "/terms.html")]
    seen = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "s", "*.html"))):
        k = os.path.basename(f)[:-5]
        if k in seen: continue
        seen.add(k)
        h0 = open(f, encoding="utf-8").read(4000)
        if 'content="noindex"' in h0: continue
        m = re.search(r'"datePublished": "([^"]+)"', h0)
        urls.append((f"{SITE}/s/{k}", m.group(1) if m else None))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, lm in urls:
        alt = ""
        if u.rstrip("/").split("/")[-1] in LANGS:
            alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}/{l}/"/>' for l in LANGS)
        sm.append(f"<url><loc>{html.escape(u)}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + alt + "</url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    rb = (f"User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /editor/\nDisallow: /reporter/\n\n"
          f"Sitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/web/news-sitemap.xml\n")
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(rb)
    print(f"lang pages: {', '.join(LANGS)} · stories {len(S)} · sitemap {len(urls)} urls")


if __name__ == "__main__":
    main()
