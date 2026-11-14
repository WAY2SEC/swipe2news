#!/usr/bin/env python3
import re
"""Swipe2News: make a WhatsApp link-preview page + picture for every story and job.

  s/<id>.html   full article page (also gives WhatsApp the story picture) + web/index.html (website home)
  cards/<id>.jpg 1200x630 preview picture (same look as the app cards)

Run from anywhere:  python3 tools/build_previews.py
Only new stories get pictures (existing ones are kept). Pictures of news older than KEEP_DAYS
are removed again to keep the site small; their pages then show the general Swipe2News picture.
Needs Playwright + Chromium (pre-installed in the cloud sessions).
"""
import json, os, glob, base64, html, threading, functools, datetime, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://swipe2news.com"
# link-preview pictures: first from our own site (WhatsApp shows these reliably), then the same file on GitHub as a backup
IMG = "https://swipe2news.com"
KEEP_DAYS = 21
# Swipe2News promo flyer under every article (set PROMO_ON = False to switch it off)
PROMO_ON = True
PROMO_HTML = ('<a class="w2promo" href="https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138" target="_blank" rel="noopener">'
  '<img src="/promo/swipe2news-promo.jpg" alt="Swipe2News – మీ ఊరి వార్తలు ఇప్పుడే మీ చేతిలో! WhatsApp ఛానెల్‌లో జాయిన్ అవ్వండి" loading="lazy" width="1199" height="1312"></a>') if PROMO_ON else ''

def load(p, d):
    try:
        with open(os.path.join(ROOT, p), encoding="utf-8") as f: return json.load(f)
    except Exception: return d

def dmy(d):
    try: return datetime.datetime.strptime(d, "%d.%m.%Y").date()
    except Exception: return None

SITE_SECS = [('telangana','తెలంగాణ'),('ap','ఆంధ్రప్రదేశ్'),('india','దేశం'),('world','ప్రపంచం'),('ai','AI & టెక్'),('jobs','ఉద్యోగ వార్తలు'),('business','బిజినెస్'),('education','విద్య'),('agri','వ్యవసాయం'),('weather','వాతావరణం'),('sports','క్రీడలు')]
ARTICLE_CSS = """
.ar .byl{font-size:13px;color:var(--muted,#6B7280);margin:6px 0 0;line-height:1.7}.ar .byl a{color:var(--brand);font-weight:700}
.ar .entr{margin:18px 0 4px;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:var(--soft);font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.ar .entr h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#6B7280);margin:0 0 6px}
.ar .entr h3{font-size:18px;margin:0 0 6px;line-height:1.35}.ar .entr p,.ar .entr li{font-size:15px;line-height:1.65}
html.l-en .ar .entr,html.l-hi .ar .entr{display:none}
.corr{margin:14px 0 0;padding:10px 14px;border-left:4px solid #E0A100;background:#FFF4D6;color:#5C3900;border-radius:10px;font-size:15px;line-height:1.7}.corr b{color:#7A4B00}
.wdn{margin:14px 0;padding:14px 16px;border-left:4px solid #4A0E3F;background:#FDECEE;color:#5C0A16;border-radius:12px;display:grid;gap:6px;font-size:16px;line-height:1.7}
.agrid{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:28px;margin-top:28px;align-items:start}
@media (max-width:1020px){.agrid{grid-template-columns:1fr}}
.ar{border-radius:24px;background:var(--paper);box-shadow:var(--shadow);overflow:hidden}
.ar .pnl{position:relative;padding:28px 32px;color:#fff;min-height:220px;display:flex;flex-direction:column;justify-content:space-between;background:radial-gradient(130% 120% at 85% 0%,color-mix(in srgb,var(--hl) 70%,#fff) 0,var(--hl) 45%,color-mix(in srgb,var(--hl) 70%,#000) 100%)}
.ar .pnl .art2{position:absolute;right:-10px;bottom:-24px;width:270px;height:270px;opacity:.2}
.ar .chips{display:flex;flex-wrap:wrap;gap:8px}
.ar .stat{font:400 clamp(40px,5.5vw,68px)/1 var(--display);margin-top:16px}
.ar .stat.te{font:800 clamp(34px,4.6vw,54px)/1.25 var(--body)}
.ar .statl{font-weight:800;font-size:18px;max-width:34ch}
.ar .in{padding:26px 32px 30px}
@media (max-width:640px){.ar .pnl,.ar .in{padding-left:20px;padding-right:20px}}
.ar h1{margin:0 0 12px;font-size:clamp(26px,3.4vw,40px);line-height:1.35;color:var(--hlink)}
.ar .alead{font-size:19px;line-height:1.85;margin:16px 0 18px}
.ar .pts{margin:0 0 18px;padding:16px 20px 16px 40px;border-radius:16px;background:var(--soft);border:1px solid var(--line)}
.ar .pts li{margin:6px 0;font-weight:700}
.ar .why{margin:0 0 20px;padding:16px 20px;border-radius:16px;border-left:5px solid var(--hl);background:var(--soft);font-weight:700}
.ar .why small{display:block;color:var(--hlink);font-size:13px;font-weight:800}
.ar .src{margin:0 0 22px;font-size:15px;color:var(--muted);font-weight:700}.ar .src a{color:var(--brand);text-decoration:underline}
table.jd{width:100%;border-collapse:collapse;margin:16px 0 20px;border-radius:16px;overflow:hidden;border:1px solid var(--line)}
table.jd th,table.jd td{text-align:left;padding:11px 16px;border-top:1px solid var(--line);font-size:15.5px;vertical-align:top}
table.jd tr:first-child th,table.jd tr:first-child td{border-top:0}
table.jd th{width:34%;color:var(--muted);font-weight:800;background:var(--soft)}
.warnj{margin:0 0 20px;padding:12px 16px;border-radius:12px;background:#F6EEF3;color:#8A0B20;font-weight:800;font-size:14.5px}
:root[data-theme="dark"] .warnj{background:#3A1630;color:#FFB3BF}
.acts{display:flex;flex-wrap:wrap;gap:10px}
.acts .cta.ghost{background:var(--soft);color:var(--ink);border:1px solid var(--line)}
.aside{display:flex;flex-direction:column;gap:18px;position:sticky;top:70px}
@media (max-width:1020px){.aside{position:static}}
.aside .latest{flex:none}
.avid{display:block;width:100%;max-width:420px;max-height:78vh;margin:0 auto 18px;border-radius:16px;background:#000}
.w2promo{display:block;padding:0 32px 30px}.w2promo img{display:block;width:100%;max-width:560px;height:auto;margin:0 auto;border-radius:16px;box-shadow:0 6px 20px rgba(0,0,0,.12)}
@media (max-width:640px){.w2promo{padding:0 20px 24px}}
.brk{background:#4A0E3F!important;border-color:#4A0E3F!important;color:#fff!important;animation:brk 1.6s ease-in-out infinite}
@keyframes brk{50%{box-shadow:0 0 0 6px rgba(200,16,46,.25)}}
"""
COLS = {'--c-election':'#B3400F','--c-gov':'#1F6B3A','--c-money':'#16406E','--c-water':'#0B5CAD','--c-power':'#5B3A8C','--c-city':'#7A4A12','--c-job':'#0F6E5C'}
PLACES = {'hyderabad':'హైదరాబాద్','rangareddy':'రంగారెడ్డి','medchal':'మేడ్చల్','adilabad':'ఆదిలాబాద్','bhadradri':'భద్రాద్రి','hanumakonda':'హనుమకొండ','jagtial':'జగిత్యాల','jangaon':'జనగామ','bhupalpally':'భూపాలపల్లి','gadwal':'గద్వాల','kamareddy':'కామారెడ్డి','karimnagar':'కరీంనగర్','khammam':'ఖమ్మం','asifabad':'ఆసిఫాబాద్','mahabubabad':'మహబూబాబాద్','mahabubnagar':'మహబూబ్‌నగర్','mancherial':'మంచిర్యాల','medak':'మెదక్','mulugu':'ములుగు','nagarkurnool':'నాగర్‌కర్నూల్','nalgonda':'నల్గొండ','narayanpet':'నారాయణపేట','nirmal':'నిర్మల్','nizamabad':'నిజామాబాద్','peddapalli':'పెద్దపల్లి','sircilla':'సిరిసిల్ల','sangareddy':'సంగారెడ్డి','siddipet':'సిద్దిపేట','suryapet':'సూర్యాపేట','vikarabad':'వికారాబాద్','wanaparthy':'వనపర్తి','warangal':'వరంగల్','yadadri':'యాదాద్రి','AP':'ఆంధ్రప్రదేశ్'}

def iso_time(s):
    d = dmy(s.get("d", ""))
    if not d: return None
    t = s.get("t") or "12:00"
    return f"{d.isoformat()}T{t}:00+05:30"

SHELL = {}
def shell():
    """Reuse the website's look (styles, top bar, ticker, side rails, footer) from tools/web_template.html."""
    if SHELL: return SHELL
    t = open(os.path.join(ROOT, "tools", "web_template.html"), encoding="utf-8").read()
    SHELL["css"] = t[t.index("<style>") + 7:t.index("</style>")] + "\n" + open(os.path.join(ROOT, "web", "s2n.css"), encoding="utf-8").read()
    hd = t[t.index('<header class="top">'):t.index('<aside class="rail l"')]
    nav = "".join(f'<a href="/?sec={k}">{n}</a>' for k, n in [('telangana','తెలంగాణ'),('ap','ఆంధ్రప్రదేశ్'),('india','దేశం'),('world','ప్రపంచం'),('business','బిజినెస్'),('sports','క్రీడలు')])
    more = '<div class="s2more"><button type="button" aria-haspopup="true">మరిన్ని ▾</button><div class="menu"><a href="/epaper/">📰 ఈ-పేపర్ · E-paper</a><a href="/mandi/">🌾 మండీ ధరలు · Mandi prices</a><a href="/?jobs=1">💼 ఉద్యోగాలు · Jobs</a><a href="/?sec=ai">🤖 AI & టెక్</a><a href="/?sec=education">🎓 విద్య</a><a href="/?dates=1">📅 పాత వార్తలు · Archive</a><a href="/reporter/join.html">🎙️ రిపోర్టర్ అవ్వండి</a></div></div>'
    hd = hd.replace('<nav class="secs" id="secs" aria-label="విభాగాలు"></nav>', f'<nav class="secs" aria-label="విభాగాలు"><a href="/">ముఖ్య వార్తలు</a>{nav}{more}</nav>')
    hd = hd.replace('<label class="search">', '<form class="search" action="/" method="get" role="search"><label style="display:contents">').replace('<kbd>/</kbd></label>', '<kbd>↵</kbd></label></form>')
    hd = hd.replace('<input id="q" type="search"', '<input id="q" name="q" type="search"')
    SHELL["header"] = hd
    SHELL["footer"] = t[t.index("<footer>"):t.index("</footer>") + 9]
    ad = t.index('<a class="ad tall adslot"'); SHELL["ad"] = t[ad:t.index("</a>", ad) + 4].replace("ad tall adslot", "ad adslot").replace('data-ad="rail"', 'data-ad="article" style="min-height:300px"')
    return SHELL

ART_JS = {}
def page(sid, s, kind, img, has_card, target, desc, related):
    e = lambda t: html.escape(str(t or ""), quote=True)
    sh = shell()
    colvar = s.get("col") or ("--c-job" if kind == "job" else "--c-gov")
    title = s.get("h", "Swipe2News")
    _v = str(s.get("vid") or "")
    vid_html = (f'<video class="avid" controls playsinline preload="metadata" poster="/{e(s.get("img",""))}" src="/{e(_v)}"></video>'
                if _v.startswith("videos/") and _v.endswith(".mp4") else "")
    place = PLACES.get(s.get("place") or "", "")
    brk = '<span class="chip brk">🔴 BREAKING</span>' if s.get("brk") else ""
    chips = brk + f'<span class="chip">{e(s.get("cat") or "వార్త")}</span>' + (f'<span class="chip">📍 {e(place)}</span>' if place else "")
    stat = str(s.get("stat") or "")
    te = any("ఀ" <= c <= "౿" for c in stat)
    if kind == "job":
        meta = [x for x in [s.get("org"), s.get("d") and f"ప్రచురణ {s['d']}"] if x]
        rows = [("posts", "పోస్టులు", s.get("posts")), ("qual", "అర్హత", s.get("qual")), ("exp", "అనుభవం", s.get("exp")), ("loc", "ఎక్కడ", s.get("loc")), ("age", "వయసు", s.get("age")),
                ("pay", "జీతం", s.get("pay")), ("last", "చివరి తేదీ", s.get("last")), ("walk", "వాక్-ఇన్", s.get("walk")), ("how", "ఎలా దరఖాస్తు", s.get("how"))]
        body = (f'<p class="alead">{e(s.get("sum") or s.get("p"))}</p>' +
                '<table class="jd">' + "".join(f'<tr data-k="{rk}"><th>{k}</th><td>{e(v)}</td></tr>' for rk, k, v in rows if v) + "</table>" +
                '<p class="warnj">⚠️ ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి. అధికారిక వెబ్‌సైట్‌లోనే దరఖాస్తు చేయండి.</p>')
        apply = s.get("apply") or s.get("url")
        src = f'<p class="src">మూలం: {e(s.get("src"))}' + (f' · <a href="{e(apply)}" target="_blank" rel="noopener nofollow">అధికారిక వెబ్‌సైట్‌లో దరఖాస్తు →</a>' if apply else "") + "</p>"
    else:
        meta = [x for x in [s.get("d"), s.get("t"), s.get("src") and f"Source: {s['src']}"] if x]
        pts = s.get("pts") or []
        body = (f'<p class="alead">{e(s.get("p"))}</p>' +
                ('<ul class="pts">' + "".join(f"<li>{e(x)}</li>" for x in pts) + "</ul>" if pts else "") +
                (f'<p class="why"><small>ఇది ఎందుకు ముఖ్యం?</small>{e(s.get("why"))}</p>' if s.get("why") else ""))
        src = f'<p class="src">మూలం: {e(s.get("src"))}' + (f' · <a href="{e(s.get("url"))}" target="_blank" rel="noopener nofollow">పూర్తి వార్త చదవండి →</a>' if s.get("url") else "") + "</p>"
        # who prepared it + other languages (AdSense / reader trust, 11 Nov 2026)
        if s.get("local") or s.get("rep"):
            by = f'✍️ {e(s.get("repn") or "Swipe2News రిపోర్టర్")} · Swipe2News రిపోర్టర్{(" · " + e(s.get("loc"))) if s.get("loc") else ""} · ఎడిటర్ ఆమోదించిన స్థానిక వార్త'
        else:
            by = '✍️ Swipe2News డెస్క్ · అసలు వార్త ఆధారంగా మా మాటల్లో క్లుప్తంగా'
        src += (f'<p class="byl">{by} · <a href="/editorial-policy.html">మేము వార్తలు ఎలా సిద్ధం చేస్తాం</a> · '
                f'<a href="/contact.html">తప్పు కనిపించిందా? తెలియజేయండి</a></p>')
        en = s.get("en") if isinstance(s.get("en"), dict) else {}
        if en.get("h") and en.get("p") and not s.get("wd"):
            src += ('<section class="entr" lang="en"><h2>In English</h2>' + f'<h3>{e(en["h"])}</h3><p>{e(en["p"])}</p>' +
                    ('<ul>' + "".join(f"<li>{e(x)}</li>" for x in (en.get("pts") or [])) + '</ul>' if en.get("pts") else "") +
                    (f'<p><b>Why it matters:</b> {e(en["why"])}</p>' if en.get("why") else "") + '</section>')
        c = s.get("corr") if isinstance(s.get("corr"), dict) else {}
        if s.get("wd"):   # withdrawn (corrections policy, 10 Nov 2026): keep the link alive, show only the notice
            body = (f'<p class="wdn"><b>⚠️ ఈ వార్తను Swipe2News ఉపసంహరించుకుంది{(" · " + e(c.get("at"))) if c.get("at") else ""}</b>'
                    f'<span>{e(c.get("te") or "ఈ వార్తలోని సమాచారం సరైనది కాదని తేలింది. పాఠకులకు క్షమాపణలు.")}</span></p>')
        elif c.get("te"):
            body += f'<p class="corr"><b>✏️ సవరణ{(" · " + e(c.get("at"))) if c.get("at") else ""}:</b> <span>{e(c["te"])}</span></p>'
    share_text = f"{title}\n{SITE}/s/{sid}"
    trs = {l: {k: s[l][k] for k in ("h", "p", "pts", "why", "cat", "stat", "statl", "posts", "qual", "exp", "loc", "age", "how", "walk") if isinstance(s.get(l), dict) and s[l].get(k)} for l in ("en", "hi") if isinstance(s.get(l), dict)}
    trs = {l: v for l, v in trs.items() if v.get("h")}
    if isinstance(s.get("corr"), dict) and not s.get("wd"):
        for l, lab in (("en", "✏️ Correction"), ("hi", "✏️ सुधार")):
            if l in trs and s["corr"].get(l):
                trs[l]["corr"] = s["corr"][l]; trs[l]["corrl"] = lab + (f' · {s["corr"]["at"]}' if s["corr"].get("at") else "") + ":"
    tr_json = ('<script type="application/json" id="w2sTr">' + json.dumps(trs, ensure_ascii=False).replace("</", "<\\/") + "</script>") if trs else ""
    import urllib.parse as up
    rel_cards = "".join(
        f'<a class="card" href="/s/{rid}" style="--hl:var({r.get("col") or "--c-gov"});--hlink:var({r.get("col") or "--c-gov"})"><div class="pnl">{r.get("_scene","")}{'<span class="chip brk">🔴 BREAKING</span>' if r.get("brk") else f'<span class="chip">{e(r.get("cat") or "వార్త")}</span>'}<div class="stat">{e(r.get("stat"))}</div></div><div class="bd"><h3>{e(r.get("h"))}</h3><div class="m">{e(r.get("src"))} · {e(r.get("d"))}</div></div></a>'
        for rid, r in related)
    published = iso_time(s)
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": title[:110], "image": [img],
          "datePublished": published, "dateModified": published, "inLanguage": "te",
          "author": {"@type": "Organization", "name": "Swipe2News", "url": SITE},
          "publisher": {"@type": "Organization", "name": "Swipe2News", "logo": {"@type": "ImageObject", "url": SITE + "/icon-512.png"}},
          "mainEntityOfPage": f"{SITE}/s/{sid}", "isBasedOn": (s.get("url") if kind == "news" else s.get("apply")) or None}
    ld = {k: v for k, v in ld.items() if v}
    return f"""<!doctype html><html lang="te"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)} | Swipe2News</title>
{'<meta name="robots" content="noindex">' if s.get("wd") else '<meta name="robots" content="max-image-preview:large">'}<meta name="description" content="{e(desc)}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Swipe2News">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/s/{sid}">
<meta property="og:url" content="{SITE}/s/{sid}">
<meta property="og:image" content="{e(img.replace(IMG, SITE))}"><meta property="og:image:secure_url" content="{e(img.replace(IMG, SITE))}"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{e(img)}">
<meta name="theme-color" content="#2E0827"><link rel="icon" href="/favicon-48.png"><link rel="manifest" href="/manifest.webmanifest">
<meta name="google-adsense-account" content="ca-pub-5189488674224327"><script async src="https://www.googletagmanager.com/gtag/js?id=G-2179H3TXWP"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-2179H3TXWP');</script><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5189488674224327" crossorigin="anonymous"></script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>{tr_json}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&family=Noto+Sans+Telugu:wght@400;600;700;800&display=swap">
<style>{sh["css"]}{ARTICLE_CSS}</style>
</head><body>
{sh["header"]}
<main class="wrap">
<div class="agrid">
<article class="ar" style="--hl:var({colvar});--hlink:var({colvar})">
  <div class="pnl">{s.get("_scene","")}
    <div class="chips">{chips}</div>
    <div><div class="stat{' te' if te else ''}">{e(stat)}</div><div class="statl">{e(s.get("statl"))}</div></div></div>
  <div class="in">
    {vid_html}
    <h1>{e(title)}</h1>
    <div class="meta">{'<span class="dot"></span>'.join(f"<span>{e(x)}</span>" for x in meta)}</div>
    {body}
    {src}
    <div class="acts">
      <a class="cta wa" href="https://wa.me/?text={e(up.quote(share_text))}" target="_blank" rel="noopener">WhatsAppలో షేర్ చేయండి</a>
      <button class="cta ghost" type="button" id="listen">🔊 తెలుగులో వినండి</button>
      <a class="cta ghost" href="{e(target)}">📱 కార్డుల్లో చూడండి</a>
    </div>
  </div>
  {PROMO_HTML}
</article>
<aside class="aside">
  <div class="latest"><h3>⚡ తాజా వార్తలు</h3><div id="latest"></div></div>
  {sh["ad"]}
  <div class="rbox" id="railJobs" hidden><h4>⏰ చివరి తేదీ దగ్గర</h4><div id="railJobsList"></div></div>
  <div class="rbox rqr"><h4>📲 Swipe2News ఛానెల్</h4><img src="/qr.png" alt="Swipe2News WhatsApp ఛానెల్ QR"><p>స్కాన్ చేసి ప్రతి 30 నిమిషాలకు వార్తలు పొందండి</p></div>
</aside>
</div>
{('<section class="sec"><div class="sh"><h2>ఇవి కూడా చదవండి</h2></div><div class="grid">' + rel_cards + '</div></section>') if rel_cards else ''}
<section class="sec"><div class="sh"><h2>మరిన్ని తాజా వార్తలు</h2><a href="/">హోమ్ →</a></div><div class="grid" id="more"></div></section>
</main>
{sh["footer"]}
<script src="/scenes.js?v=20261114i" defer></script><script src="/web/site.js" defer></script><script src="/web/s2n.js?v=3" defer></script>
</body></html>
"""


STATIC_PAGES = {
 "about.html": ("మా గురించి | About Swipe2News – మీ సమయానికి విలువ. మీ ఊరి వార్తకు వేదిక.", "SWIPE2NEWS — మీ సమయానికి విలువ. మీ ఊరి వార్తకు వేదిక. ముఖ్యమైన వార్తలను సులభమైన తెలుగులో, క్లుప్తంగా, వేగంగా అందించడమే మా లక్ష్యం.", """
<div class="ab-hero">
  <span class="ab-k">మా గురించి · ABOUT SWIPE2NEWS</span>
  <h1><span class="ab-b">SWIPE2NEWS</span><span class="ab-l1"><span class="ab-pray" aria-hidden="true">🙏</span> మీ సమయానికి విలువ.</span><span class="ab-l2">మీ ఊరి వార్తకు వేదిక.</span></h1>
  <p>ముఖ్యమైన వార్తలను సులభమైన తెలుగులో, క్లుప్తంగా, వేగంగా.</p>
</div>
<div class="ab-body">
  <h2>ఈ ఆలోచన ఎలా పుట్టింది</h2>
  <p class="alead">ఈ రోజుల్లో సమాచారం ఎక్కువగా ఉంది. కానీ <b>ఏం జరిగింది, ఎందుకు జరిగింది, మనకు ఎందుకు ముఖ్యమో</b> తెలుసుకోవడానికి ఎన్నో పేజీలు చదవాల్సి వస్తోంది.</p>
  <p class="alead">ఆ అవసరం నుంచే SWIPE2NEWS ఆలోచన పుట్టింది. ముఖ్యమైన వార్తలను <b>సులభమైన తెలుగులో, క్లుప్తంగా, వేగంగా</b> అందించాలనేది మా లక్ష్యం.</p>

  <h2>మా దృష్టిలో వార్త అంటే</h2>
  <p class="alead">మా దృష్టిలో వార్త అంటే పెద్ద నగరాల్లో జరిగేది మాత్రమే కాదు.</p>
  <div class="ab-grid3">
    <div class="ab-c"><b>🏘️</b><span>ఒక గ్రామంలో పరిష్కారం కోసం ఎదురుచూస్తున్న సమస్య</span></div>
    <div class="ab-c"><b>🎓</b><span>ఒక విద్యార్థి సాధించిన విజయం</span></div>
    <div class="ab-c"><b>🌾</b><span>ఒక రైతు అనుభవం</span></div>
  </div>
  <p class="alead">ఇవి కూడా ప్రజలకు తెలియాల్సిన వార్తలే.</p>

  <h2>AI తో, ఖచ్చితత్వంతో</h2>
  <p class="alead">AI సాంకేతికతను ఉపయోగించి సమాచారాన్ని సులభంగా అందిస్తూ, ప్రతి వార్తలో <b>ఖచ్చితత్వానికి, సందర్భానికి</b> ప్రాధాన్యం ఇవ్వాలనేది మా సంకల్పం.</p>

  <h2>SWIPE2NEWS అనే పేరు</h2>
  <p class="alead">SWIPE2NEWS అనే పేరు <b>వేగానికి ప్రతీక</b>. ప్రతి వార్తను రెండు సెకన్లలో చదవాలనే అర్థం కాదు — కొద్దిసమయంలో ముఖ్యమైన విషయం అర్థమయ్యేలా అందించాలనే ఆలోచన.</p>
</div>

<blockquote class="ab-q">
  <small>మా పెద్ద ఆలోచన ఒక్కటే</small>
  <p>ప్రపంచ వార్త మీ చేతిలోకి రావాలి.</p>
  <p>మీ ఊరి వార్త ప్రపంచానికి చేరాలి.</p>
</blockquote>

<div class="ab-body">
  <h2>మా విలువలు</h2>
  <div class="ab-grid">
    <div class="ab-v"><b>⚡ వేగం</b><span>ప్రతి 30 నిమిషాలకు తాజా వార్తలు – ముఖ్యమైన విషయం కొద్ది సమయంలో.</span></div>
    <div class="ab-v"><b>✍️ సులభమైన తెలుగు</b><span>మా సొంత మాటల్లో, అందరికీ అర్థమయ్యేలా క్లుప్తంగా.</span></div>
    <div class="ab-v"><b>✅ ఖచ్చితత్వం</b><span>నమ్మకమైన వార్తా సంస్థలు, అధికారిక ప్రకటనల నుంచే. ప్రతి వార్తకు అసలు మూలం పేరు, లింక్.</span></div>
    <div class="ab-v"><b>🧭 సందర్భం</b><span>"ఇది ఎందుకు ముఖ్యం?" – ప్రతి వార్తలో మీకు ఏం అర్థం అనేది కూడా.</span></div>
    <div class="ab-v"><b>⚖️ తటస్థత</b><span>రాజకీయ వార్తల్లో వాస్తవాలకే పరిమితం. ఊహాగానాలు, అభిప్రాయాలు ఉండవు.</span></div>
    <div class="ab-v"><b>📍 మీ ఊరు</b><span>గ్రామం, మండలం, జిల్లా నుంచి దేశం, ప్రపంచం వరకు – మీ ప్రాంత వార్తలు ముందుగా.</span></div>
  </div>

  <h2>మీరూ భాగస్వాములు కండి</h2>
  <p class="alead">మీ ఊరిలో జరిగిన ముఖ్యమైన విషయం, పరిష్కారం కావాల్సిన సమస్య, ఎవరైనా సాధించిన విజయం – మాకు పంపండి. పరిశీలించి ప్రపంచానికి చేరుస్తాం.</p>
  <div class="acts"><a class="cta" href="/?tip=1&amp;cards=1" style="background:var(--brand)">📝 మీ ఊరి వార్త పంపండి</a><a class="cta wa" href="https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138" target="_blank" rel="noopener">WhatsApp ఛానెల్‌లో చేరండి</a><a class="cta" href="/contact.html">సంప్రదించండి</a></div>

  <h2>మేము ఎవరు · Who we are</h2>
  <p class="alead">SWIPE2NEWS ను <b>Swipe2News టీమ్</b> నడుపుతోంది. మా కేంద్రం <b>ఆలేరు, యాదాద్రి భువనగిరి జిల్లా, తెలంగాణ</b>. ఆలేరు, యాదాద్రి ప్రాంతంలోని మా స్థానిక రిపోర్టర్లు గ్రామ వార్తలు పంపుతారు; ప్రతి స్థానిక వార్తను మా ఎడిటర్ పరిశీలించి ఆమోదించిన తర్వాతే ప్రచురిస్తాం.</p>
  <table class="jd">
  <tr><th>📍 చిరునామా · Based in</th><td>ఆలేరు, యాదాద్రి భువనగిరి జిల్లా, తెలంగాణ, భారత్ · Aler, Yadadri Bhuvanagiri district, Telangana, India</td></tr>
  <tr><th>📧 ఈమెయిల్ · Email</th><td><a href="mailto:swipe2news@gmail.com" style="color:var(--brand);font-weight:800">swipe2news@gmail.com</a></td></tr>
  <tr><th>📲 WhatsApp</th><td><a href="https://wa.me/917032656422" target="_blank" rel="noopener" style="color:var(--brand);font-weight:800">+91 70326 56422</a></td></tr>
  </table>

  <h2>మేము ఏమి అందిస్తాం · What we publish</h2>
  <div class="ab-grid">
    <div class="ab-v"><b>📍 స్థానిక వార్తలు</b><span>మా రిపోర్టర్లు స్వయంగా సేకరించిన ఆలేరు, యాదాద్రి, చుట్టుపక్కల గ్రామాల వార్తలు – ఫోటోలతో.</span></div>
    <div class="ab-v"><b>🗞️ తెలంగాణ, ఏపీ, దేశం, ప్రపంచం</b><span>నమ్మకమైన వార్తా సంస్థలు, అధికారిక ప్రకటనల ఆధారంగా మా మాటల్లో క్లుప్త వార్తలు – అసలు మూలం పేరు, లింక్‌తో.</span></div>
    <div class="ab-v"><b>💼 ఉద్యోగాలు</b><span>ప్రభుత్వ, ప్రైవేట్ ఉద్యోగ ప్రకటనలు – అధికారిక వెబ్‌సైట్ లింక్‌తోనే. ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి.</span></div>
    <div class="ab-v"><b>📰 జనధ్వని ఈ-పేపర్</b><span>ప్రతి ఉదయం నిన్నటి ముఖ్య వార్తలు, ఈరోజు ముఖ్య ఘట్టాలతో రోజువారీ ఈ-పేపర్.</span></div>
  </div>
  <p class="alead">మేము వార్తలు ఎలా సిద్ధం చేస్తామో, తప్పులు ఎలా సరిచేస్తామో మా <a href="/editorial-policy.html" style="color:var(--brand);font-weight:800">సంపాదకీయ విధానం (Editorial policy)</a>లో వివరంగా చదవండి.</p>

  <h2>In English</h2>
  <p><b>SWIPE2NEWS — your time matters; a platform for your village's news.</b> Information is everywhere today, yet understanding what happened, why it happened and why it matters to us still means reading page after page. SWIPE2NEWS was born from that need: to deliver the important news in simple Telugu – short, clear and fast. For us, news is not only what happens in big cities; a village problem waiting for a solution, a student's achievement or a farmer's experience is news people deserve to know. We use AI to make information easy to read, while putting accuracy and context first in every story – each one names its original source. Swipe2News is run by the Swipe2News team from Aler, Yadadri Bhuvanagiri district, Telangana (swipe2news@gmail.com · +91 70326 56422). Local stories come from our own reporters and are approved by our editor before they are published; read how we work in our <a href="/editorial-policy.html" style="color:var(--brand);font-weight:800">Editorial policy</a>. The name SWIPE2NEWS stands for speed: not reading every story in two seconds, but understanding what matters in very little time. Our one big idea: <b>the world's news should reach your hands, and your village's news should reach the world.</b></p>
  <p class="why"><small>తప్పు కనిపించిందా? · Spotted an error?</small>ఏదైనా వార్తలో తప్పు ఉంటే <a href="/contact.html" style="color:var(--brand)">మాకు తెలియజేయండి</a> – వెంటనే సరిచేస్తాం.</p>
</div>
"""),
 "contact.html": ("సంప్రదించండి | Contact Swipe2News", "Swipe2News ను సంప్రదించండి – వార్తలు, సవరణలు, ప్రకటనలు.", """
<h1>సంప్రదించండి · Contact us</h1>
<p class="alead">వార్తల సమాచారం, తప్పుల సవరణ, ప్రకటనలు లేదా ఏ ప్రశ్నకైనా మమ్మల్ని సంప్రదించండి.</p>
<table class="jd">
<tr><th>📧 ఈమెయిల్ · Email</th><td><a href="mailto:swipe2news@gmail.com" style="color:var(--brand);font-weight:800">swipe2news@gmail.com</a></td></tr>
<tr><th>📝 మీ ఊరి వార్త పంపండి</th><td><a href="/?tip=1&amp;cards=1" style="color:var(--brand);font-weight:800">వార్త పంపే ఫారం →</a></td></tr>
<tr><th>📢 ప్రకటనలు · Advertising</th><td><a href="https://wa.me/917032656422?text=Swipe2News%20advertising" target="_blank" rel="noopener" style="color:var(--brand);font-weight:800">WhatsAppలో సంప్రదించండి →</a></td></tr>
<tr><th>📲 WhatsApp ఛానెల్</th><td><a href="https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138" target="_blank" rel="noopener" style="color:var(--brand);font-weight:800">Swipe2News ఛానెల్‌లో చేరండి →</a></td></tr>
<tr><th>📍 చిరునామా · Address</th><td>Swipe2News టీమ్, ఆలేరు, యాదాద్రి భువనగిరి జిల్లా, తెలంగాణ, భారత్</td></tr>
<tr><th>📲 WhatsApp</th><td><a href="https://wa.me/917032656422" target="_blank" rel="noopener" style="color:var(--brand);font-weight:800">+91 70326 56422</a></td></tr>
<tr><th>🔒 గోప్యత · Privacy</th><td><a href="/privacy.html" style="color:var(--brand);font-weight:800">Privacy Policy →</a></td></tr>
<tr><th>📜 విధానాలు · Policies</th><td><a href="/editorial-policy.html" style="color:var(--brand);font-weight:800">Editorial policy</a> · <a href="/terms.html" style="color:var(--brand);font-weight:800">Terms of use</a></td></tr>
</table>
<p class="why"><small>సవరణలు · Corrections</small>ఏదైనా వార్తలో తప్పు కనిపిస్తే, ఆ వార్త లింక్‌తో ఈమెయిల్ చేయండి. పరిశీలించి సరిచేస్తాం.</p>
"""),
 "editorial-policy.html": ("సంపాదకీయ విధానం | Editorial policy – Swipe2News", "Swipe2News వార్తలను ఎలా సిద్ధం చేస్తుంది, మూలాలు, AI వినియోగం, తటస్థత, తప్పుల సవరణ విధానం. How Swipe2News prepares news, sources, use of AI, neutrality and corrections.", """
<h1>సంపాదకీయ విధానం · Editorial policy</h1>
<p class="alead">Swipe2News లో ప్రతి వార్తను ఎలా ఎంచుకుంటాం, ఎలా రాస్తాం, తప్పులను ఎలా సరిచేస్తాం – ఇక్కడ స్పష్టంగా చెబుతున్నాం. పాఠకుల నమ్మకమే మా బలం.</p>

<h2>1. మూలాలు · Sources</h2>
<p>తెలంగాణ, ఏపీ, దేశ, ప్రపంచ వార్తలను <b>నమ్మకమైన వార్తా సంస్థలు</b> (ఉదా: PTI, The Hindu, Eenadu, Sakshi, Telangana Today, Reuters, BBC) మరియు <b>అధికారిక ప్రకటనలు</b> (ప్రభుత్వ పత్రికా ప్రకటనలు, IMD, TGPSC/APPSC, PIB) ఆధారంగా అందిస్తాం. ప్రతి వార్త కింద <b>అసలు మూలం పేరు, లింక్</b> ఇస్తాం – పూర్తి వివరాలు అక్కడ చదవవచ్చు. సోషల్ మీడియాలో మాత్రమే కనిపించే, నిర్ధారణ కాని సమాచారాన్ని ప్రచురించం.</p>
<p><i>English:</i> National, state and world stories are based on reputable news organisations and official releases. Every story names and links its original source. We do not publish claims that appear only on social media and cannot be confirmed.</p>

<h2>2. స్థానిక వార్తలు · Local reporting</h2>
<p>ఆలేరు, యాదాద్రి భువనగిరి, చుట్టుపక్కల గ్రామాల వార్తలను <b>మా స్వంత రిపోర్టర్లు</b> సేకరిస్తారు. ప్రతి రిపోర్టర్‌కు ఒక గుర్తింపు సంఖ్య (PIN) ఉంటుంది. వారు పంపిన ప్రతి వార్తను <b>మా ఎడిటర్ చదివి, అవసరమైతే రిపోర్టర్‌తో మాట్లాడి, ఆమోదించిన తర్వాతే</b> ప్రచురిస్తాం. వార్తపై రిపోర్టర్ పేరు ఉంటుంది.</p>
<p><i>English:</i> Local news is gathered by our own registered reporters. Every local story is read and approved by our editor before publication, and carries the reporter's name.</p>

<h2>3. AI వినియోగం · How we use AI</h2>
<p>వార్తలను వేగంగా, సులభమైన తెలుగులో అందించేందుకు AI సాధనాలను ఉపయోగిస్తాం: మూల వార్తలను చదివి <b>మా సొంత మాటల్లో క్లుప్త సారాంశం</b>, ముఖ్యాంశాలు, "ఇది ఎందుకు ముఖ్యం" వివరణ, ఇంగ్లీష్, హిందీ అనువాదాలు తయారు చేయడానికి. AI కి కఠిన నియమాలు ఉన్నాయి: మూలంలో లేని సంఖ్యలు, పేర్లు, కోట్స్ జోడించకూడదు; ఊహాగానాలు, అభిప్రాయాలు రాయకూడదు; ప్రతి వార్తకు మూలం చూపాలి. పాఠకులు తప్పు చెబితే మా టీమ్ పరిశీలించి సరిచేస్తుంది.</p>
<p><i>English:</i> We use AI tools to write short summaries of source reports in our own words, add key points and a "why it matters" line, and translate into English and Hindi. The AI works under strict rules: no numbers, names or quotes that are not in the source, no speculation or opinion, and the source is always shown. Our team checks and corrects stories when errors are found or reported.</p>

<h2>4. తటస్థత · Neutrality</h2>
<p>రాజకీయ వార్తల్లో అన్ని పార్టీలకు ఒకే ప్రమాణం. వాస్తవాలకే పరిమితం – ఏ పార్టీకి, అభ్యర్థికి మద్దతు లేదా వ్యతిరేకత ఉండదు. నిర్ధారణ కాని ఆరోపణలను వాస్తవాలుగా రాయం. నేరాల వార్తల్లో బాధితులు, అనుమానితులు, పిల్లల పేర్లు వెల్లడించం; హింసాత్మక వివరాలు రాయం.</p>
<p><i>English:</i> Political news follows the same standard for every party, sticks to facts and takes no side. Unproven allegations are never presented as fact. In crime news we do not name victims, suspects or children, and avoid graphic detail.</p>

<h2>5. తప్పుల సవరణ · Corrections</h2>
<p>ఏదైనా వార్తలో తప్పు కనిపిస్తే, ఆ వార్త లింక్‌తో <a href="mailto:swipe2news@gmail.com" style="color:var(--brand);font-weight:800">swipe2news@gmail.com</a> కు ఈమెయిల్ చేయండి లేదా <a href="https://wa.me/917032656422" target="_blank" rel="noopener" style="color:var(--brand);font-weight:800">WhatsApp 70326 56422</a> కు పంపండి. పరిశీలించి, తప్పు అయితే <b>వెంటనే సరిచేస్తాం</b>. తీవ్రమైన తప్పు అయితే వార్తను తొలగిస్తాం.</p>
<p><i>English:</i> If you find an error, send us the story link by email or WhatsApp. We check it and correct it promptly; a story with a serious error is removed.</p>

<h2>6. ప్రకటనలు · Advertising</h2>
<p>ప్రకటనలు ఎప్పుడూ "ప్రకటన · Sponsored" అని స్పష్టంగా గుర్తించి ఉంటాయి. ప్రకటనదారులు మా వార్తలను ప్రభావితం చేయలేరు. ఉద్యోగ ప్రకటనలకు అధికారిక లింక్ మాత్రమే ఇస్తాం – <b>ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి</b>.</p>
<p><i>English:</i> Ads are always clearly labelled "ప్రకటన · Sponsored", and advertisers have no say over our news. Job listings link only to official pages.</p>

<h2>7. కాపీరైట్ · Copyright</h2>
<p>మా సారాంశాలు మా సొంత మాటల్లో ఉంటాయి; ఇతర సంస్థల వ్యాసాలను, వార్తా ఫోటోలను కాపీ చేయం. కాపీరైట్ సమస్య ఉంటే మమ్మల్ని సంప్రదించండి – వెంటనే చర్య తీసుకుంటాం.</p>
<p class="why"><small>సంప్రదించండి · Contact</small>Swipe2News టీమ్ · ఆలేరు, యాదాద్రి భువనగిరి జిల్లా, తెలంగాణ · swipe2news@gmail.com · +91 70326 56422</p>
"""),
 "terms.html": ("ఉపయోగ నిబంధనలు | Terms of use – Swipe2News", "Swipe2News వెబ్‌సైట్, యాప్ ఉపయోగ నిబంధనలు. Terms of use for the Swipe2News website and app.", """
<h1>ఉపయోగ నిబంధనలు · Terms of use</h1>
<p class="alead">Swipe2News వెబ్‌సైట్ (swipe2news.com), యాప్‌ను ఉపయోగించడం ద్వారా మీరు ఈ నిబంధనలను అంగీకరిస్తున్నారు. చివరి మార్పు: 11 నవంబర్ 2026.</p>

<h2>1. సేవ · The service</h2>
<p>Swipe2News ఉచిత తెలుగు వార్తా సేవ – వార్తలు, ఉద్యోగ సమాచారం, ఈ-పేపర్, ఇంగ్లీష్, హిందీ అనువాదాలతో. ఈ సమాచారం సాధారణ అవగాహన కోసం మాత్రమే. ఆరోగ్యం, చట్టం, డబ్బు, ఉద్యోగ దరఖాస్తుల వంటి ముఖ్య నిర్ణయాల ముందు అధికారిక మూలాన్ని తప్పకుండా చూసుకోండి.</p>
<p><i>English:</i> Swipe2News is a free Telugu news service. Its content is for general information; please check the official source before acting on anything important.</p>

<h2>2. మా కంటెంట్ · Our content</h2>
<p>Swipe2News సారాంశాలు, డిజైన్, కార్డ్ చిత్రాలు, ఈ-పేపర్ Swipe2News కు చెందినవి. మా లింక్‌తో, Swipe2News పేరుతో షేర్ చేయడానికి స్వాగతం. అనుమతి లేకుండా మొత్తం కంటెంట్‌ను కాపీ చేసి వేరే చోట ప్రచురించకూడదు. మూల వార్తల హక్కులు ఆయా సంస్థలవే.</p>
<p><i>English:</i> Our summaries, designs, cards and e-paper belong to Swipe2News. Sharing with our link and name is welcome; republishing our content in bulk without permission is not. Rights in original source articles belong to their publishers.</p>

<h2>3. మీరు పంపే వార్తలు · What you send us</h2>
<p>మీరు లేదా మా రిపోర్టర్లు పంపే వార్తలు, ఫోటోలు, వీడియోలు నిజమైనవి, మీ స్వంతవి (లేదా ప్రచురించే అనుమతి ఉన్నవి) అయి ఉండాలి. ఎవరినీ కించపరిచే, తప్పుడు, ద్వేషపూరిత కంటెంట్ పంపకూడదు. పంపడం ద్వారా Swipe2News యాప్, వెబ్‌సైట్, ఈ-పేపర్, సోషల్ మీడియాలో దానిని ప్రచురించే అనుమతి ఇస్తున్నారు. ఏ వార్తను ప్రచురించాలో, ఎలా సవరించాలో ఎడిటర్ నిర్ణయిస్తారు.</p>
<p><i>English:</i> Anything you send must be true and yours (or you must have permission to share it), and must not be defamatory, false or hateful. By sending it you allow Swipe2News to publish it across its app, website, e-paper and social channels. The editor decides what is published and may edit it.</p>

<h2>4. ప్రకటనలు, బయటి లింకులు · Ads and external links</h2>
<p>Swipe2News లో ప్రకటనలు "ప్రకటన · Sponsored" అని గుర్తించి ఉంటాయి. ప్రకటనదారుల ఉత్పత్తులు, సేవలకు వారే బాధ్యులు. మూల వార్తలు, ఉద్యోగ వెబ్‌సైట్ల వంటి బయటి లింకులపై మాకు నియంత్రణ ఉండదు. ఉద్యోగం కోసం ఎవరికీ డబ్బులు చెల్లించకండి.</p>
<p><i>English:</i> Ads are labelled as such and advertisers are responsible for their own offers. We do not control external sites we link to. Never pay anyone for a job.</p>

<h2>5. బాధ్యత పరిమితి · Limitation of liability</h2>
<p>సమాచారం ఖచ్చితంగా ఉండేలా ప్రయత్నిస్తాం, కానీ ప్రతి వివరం సరైనదని లేదా తాజాగా ఉందని హామీ ఇవ్వలేం. Swipe2News సమాచారం ఆధారంగా తీసుకున్న నిర్ణయాల వల్ల కలిగే నష్టాలకు Swipe2News బాధ్యత వహించదు.</p>
<p><i>English:</i> We work to keep information accurate but cannot guarantee every detail is complete or current, and are not liable for decisions made on the basis of it.</p>

<h2>6. గోప్యత, మార్పులు · Privacy and changes</h2>
<p>మీ సమాచారాన్ని ఎలా ఉపయోగిస్తామో <a href="/privacy.html" style="color:var(--brand);font-weight:800">గోప్యతా విధానం</a>లో చూడండి. ఈ నిబంధనలను అవసరమైనప్పుడు మారుస్తాం; తాజా వెర్షన్ ఎప్పుడూ ఈ పేజీలో ఉంటుంది. ఈ నిబంధనలకు భారతదేశ చట్టాలు వర్తిస్తాయి.</p>
<p class="why"><small>సంప్రదించండి · Contact</small>Swipe2News టీమ్ · ఆలేరు, యాదాద్రి భువనగిరి జిల్లా, తెలంగాణ · swipe2news@gmail.com · +91 70326 56422</p>
"""),
}

def static_page(title, desc, body, name=""):
    sh = shell(); e = lambda t: html.escape(t or "", quote=True)
    return f"""<!doctype html><html lang="te"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{name}">
<meta name="theme-color" content="#2E0827"><link rel="icon" href="/favicon-48.png"><link rel="manifest" href="/manifest.webmanifest">
<meta name="google-adsense-account" content="ca-pub-5189488674224327"><script async src="https://www.googletagmanager.com/gtag/js?id=G-2179H3TXWP"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-2179H3TXWP');</script><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5189488674224327" crossorigin="anonymous"></script>
<meta property="og:title" content="{e(title)}"><meta property="og:image" content="{IMG}/og-image.jpg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&family=Noto+Sans+Telugu:wght@400;600;700;800&display=swap">
<style>{sh["css"]}{ARTICLE_CSS}.ar .in h2{{font-size:22px;margin:26px 0 10px}}.ar .in p{{line-height:1.85}}
.ab-hero{{margin:-26px -32px 24px;padding:44px 32px 40px;color:#fff;background:radial-gradient(120% 140% at 100% 0%,#3B2A7A 0,#1A2C55 45%,#22061D 100%);position:relative;overflow:hidden}}
.ab-hero:after{{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(200,16,46,.55),transparent 65%)}}
.ab-k{{font:400 12px/1 var(--display);letter-spacing:.14em;color:var(--gold)}}
.ab-hero h1{{margin:14px 0 12px;line-height:1.3;color:#fff;position:relative;z-index:1}}
.ab-b{{display:block;font:400 clamp(30px,4.6vw,48px)/1.1 var(--display);letter-spacing:.02em;margin-bottom:10px}}
.ab-l1{{display:block;white-space:nowrap;color:var(--gold);font-size:clamp(22px,3.5vw,38px)}}
.ab-l2{{display:block;font-size:clamp(22px,3.5vw,38px)}}
.ab-pray{{display:inline-block;margin-right:4px;animation:pray 2.4s ease-in-out infinite;transform-origin:50% 80%}}
@keyframes pray{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(-8deg) scale(1.08)}}}}
@media (prefers-reduced-motion:reduce){{.ab-pray{{animation:none}}}}
.ab-hero p{{margin:0;font-size:18px;color:#D6DEEA;font-weight:700;position:relative;z-index:1}}
.ab-grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:6px 0 14px}}@media (max-width:640px){{.ab-grid3{{grid-template-columns:1fr}}}}
.ab-c{{padding:18px;border-radius:16px;background:var(--soft);border:1px solid var(--line);font-weight:800;line-height:1.5}}.ab-c b{{display:block;font-size:30px;margin-bottom:6px}}
.ab-q{{margin:28px -32px;padding:34px 32px;background:linear-gradient(135deg,#4A0E3F,#8A0B20);color:#fff;text-align:center}}
.ab-q small{{display:block;font-weight:800;color:#F5A23A;letter-spacing:.04em;margin-bottom:10px}}.ab-q p{{margin:4px 0;font-size:clamp(22px,3.4vw,34px);font-weight:800;line-height:1.45}}
.ab-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}@media (max-width:640px){{.ab-grid{{grid-template-columns:1fr}}}}
.ab-v{{padding:16px 18px;border-radius:16px;border:1px solid var(--line);background:var(--paper);border-left:5px solid var(--brand)}}.ab-v b{{display:block;font-size:17px;margin-bottom:4px}}.ab-v span{{color:var(--muted);font-weight:600;font-size:15px;line-height:1.6}}
@media (max-width:640px){{.ab-hero,.ab-q{{margin-left:-20px;margin-right:-20px;padding-left:20px;padding-right:20px}}}}
</style>
</head><body>
{sh["header"]}
<main class="wrap"><div class="agrid"><article class="ar" style="--hl:var(--c-money);--hlink:var(--c-money)"><div class="in">{body}</div></article>
<aside class="aside"><div class="latest"><h3>⚡ తాజా వార్తలు</h3><div id="latest"></div></div><div class="rbox rqr"><h4>📲 Swipe2News ఛానెల్</h4><img src="/qr.png" alt="Swipe2News WhatsApp ఛానెల్ QR"><p>స్కాన్ చేసి ప్రతి 30 నిమిషాలకు వార్తలు పొందండి</p></div></aside></div></main>
{sh["footer"]}
<script src="/scenes.js?v=20261114i" defer></script><script src="/web/site.js" defer></script><script src="/web/s2n.js?v=3" defer></script>
</body></html>
"""

def main():
    news = load("news.json", {}).get("stories", [])
    days = []
    for p in sorted(glob.glob(os.path.join(ROOT, "archive", "20*.json"))):
        days += load(os.path.relpath(p, ROOT), {}).get("stories", [])
    jobs = load("jobs.json", {}).get("jobs", [])
    wishes = load("wishes.json", {}).get("stories", [])
    os.makedirs(os.path.join(ROOT, "cards"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "s"), exist_ok=True)

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=ROOT)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    from playwright.sync_api import sync_playwright
    today = datetime.date.today()
    made = pages = removed = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        pg = b.new_page()
        pg.route("**/*", lambda r: r.abort() if not r.request.url.startswith(base) and not r.request.url.startswith("data:") else r.continue_())
        pg.goto(base + "/index.html?build=1")
        pg.add_style_tag(content="""
@font-face{font-family:'Noto Sans Telugu';src:url(/tools/fonts/NotoSansTelugu.ttf);font-weight:100 900}
@font-face{font-family:'Archivo Black';src:url(/tools/fonts/Outfit-ExtraBold.ttf)}""")
        pg.add_script_tag(path=os.path.join(ROOT, "tools", "og.js"))
        pg.evaluate("Promise.all([document.fonts.load(\"800 40px 'Noto Sans Telugu'\"),document.fonts.load(\"600 40px 'Noto Sans Telugu'\"),document.fonts.load(\"40px 'Archivo Black'\")])")

        raw = [("news", s) for s in wishes + news + days] + [("job", j) for j in jobs]
        normed = pg.evaluate("(arr)=>arr.map(a=>{const s=a[0]==='job'?normJob(a[1]):a[1]; s._scene=sceneSVG(s,'scene'); return [a[0], s, sid(s)];})", raw)
        uniq, seen = [], set()
        for kind, s, sid in normed:
            if sid in seen: continue
            seen.add(sid); uniq.append((kind, s, sid))
        secs = lambda s: s.get("sec") if isinstance(s.get("sec"), list) else ([s.get("sec")] if s.get("sec") else [])
        for kind, s, sid in uniq:
            d = dmy(s.get("d", ""))
            old = kind == "news" and d and (today - d).days > KEEP_DAYS
            img_path = os.path.join(ROOT, "cards", sid + ".jpg")
            if old:
                if os.path.exists(img_path): os.remove(img_path); removed += 1
                img = IMG + "/og-image.jpg"
            else:
                if not os.path.exists(img_path):
                    url = pg.evaluate("(s)=>ogImage(s)", s)
                    with open(img_path, "wb") as f: f.write(base64.b64decode(url.split(",", 1)[1]))
                    made += 1
                img = f"{IMG}/cards/{sid}.jpg"
            if kind == "job":
                target = f"/?jobs=1&s={sid}"
                desc = " · ".join(x for x in [s.get("posts") and f"{s['posts']} పోస్టులు", s.get("last") and f"చివరి తేదీ {s['last']}", s.get("org")] if x)
                related = [(rid, r) for k2, r, rid in uniq if k2 == "job" and rid != sid][:4]
            else:
                iso = d.isoformat() if d else ""
                target = f"/?wishes=1&s={sid}" if "wishes" in secs(s) else (f"/?d={iso}&s={sid}" if iso else f"/?s={sid}")
                _lb = {"claim": "వాదన / ఆరోపణ", "misleading": "తప్పుదోవ", "opinion": "అభిప్రాయం"}.get(s.get("lbl"), "")
                desc = ((_lb + " · " + (s.get("src") or "") + " ప్రకారం · ") if _lb else "") + (s.get("p") or "")
                desc = desc[:200]
                mine = set(secs(s))
                related = [(rid, r) for k2, r, rid in uniq if k2 == "news" and rid != sid and not r.get("wd") and mine & set(secs(r))][:4]
            out = page(sid, s, kind, img, os.path.exists(img_path), target, desc, related)
            sp = os.path.join(ROOT, "s", sid + ".html")
            prev = open(sp, encoding="utf-8").read() if os.path.exists(sp) else None
            if prev != out:
                with open(sp, "w", encoding="utf-8") as f: f.write(out)
                pages += 1
        # old article pages no longer in the data (headline/link changed): point Google to the
        # current page with the same headline, else to themselves (fixes "Duplicate without user-selected canonical")
        cur = {sid for _, _, sid in uniq}
        by_title = {}
        for _, s, sid in uniq: by_title.setdefault(s.get("h", "Swipe2News"), sid)
        for fp in glob.glob(os.path.join(ROOT, "s", "*.html")):
            oid = os.path.basename(fp)[:-5]
            if oid in cur: continue
            h0 = open(fp, encoding="utf-8").read()
            m = re.search(r"<title>(.*?) \| Swipe2News</title>", h0)
            tgt = by_title.get(html.unescape(m.group(1)) if m else None) or oid
            link = f'<link rel="canonical" href="{SITE}/s/{tgt}">'
            h1 = re.sub(r'<link rel="canonical"[^>]*>\n?', "", h0).replace('<meta property="og:url"', link + "\n" + '<meta property="og:url"', 1)
            if h1 != h0:
                with open(fp, "w", encoding="utf-8") as f: f.write(h1)
        # shared script for article pages (ticker, latest, jobs, more news, theme, listen)
        app0 = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        b0 = app0.index("const ART = {"); b1 = app0.index("\n};", b0) + 3
        site_js = open(os.path.join(ROOT, "tools", "site_js.js"), encoding="utf-8").read().replace("/*ART*/", app0[b0:b1])
        os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
        sj = os.path.join(ROOT, "web", "site.js")
        if not os.path.exists(sj) or open(sj, encoding="utf-8").read() != site_js:
            with open(sj, "w", encoding="utf-8") as f: f.write(site_js)
        for name, (t, dsc, body) in STATIC_PAGES.items():
            out = static_page(t, dsc, body, name); fp = os.path.join(ROOT, name)
            if not os.path.exists(fp) or open(fp, encoding="utf-8").read() != out:
                with open(fp, "w", encoding="utf-8") as f: f.write(out)
        # sitemap for Google (home, sections, static pages, every article) + robots.txt
        urls = [(SITE + "/", None), (SITE + "/about.html", None), (SITE + "/contact.html", None), (SITE + "/privacy.html", None), (SITE + "/editorial-policy.html", None), (SITE + "/terms.html", None), (SITE + "/epaper/", None)]
        for kind, s, sid in uniq:
            if s.get("wd"): continue
            urls.append((f"{SITE}/s/{sid}", iso_time(s)))
        sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for u, lm in urls:
            sm.append(f"<url><loc>{html.escape(u)}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>")
        sm.append("</urlset>")
        with open(os.path.join(ROOT, "web", "sitemap.xml"), "w", encoding="utf-8") as f: f.write("\n".join(sm) + "\n")
        # Google News sitemap: news articles of the last 2 days (Google News reads only the last 48 hours)
        ns = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">']
        nn = 0
        for kind, s, sid in uniq:
            d = dmy(s.get("d", ""))
            if kind != "news" or s.get("wd") or not d or (today - d).days > 1 or "wishes" in secs(s) or nn >= 1000: continue
            ns.append(f"<url><loc>{SITE}/s/{sid}</loc><news:news><news:publication><news:name>Swipe2News</news:name><news:language>te</news:language></news:publication>"
                      f"<news:publication_date>{iso_time(s)}</news:publication_date><news:title>{html.escape(str(s.get('h') or ''))}</news:title></news:news></url>")
            nn += 1
        ns.append("</urlset>")
        with open(os.path.join(ROOT, "web", "news-sitemap.xml"), "w", encoding="utf-8") as f: f.write("\n".join(ns) + "\n")
        rb = f"User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /editor/\nDisallow: /reporter/\n\nSitemap: {SITE}/web/sitemap.xml\nSitemap: {SITE}/web/news-sitemap.xml\n"
        with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f: f.write(rb)
        # website home page (template + the app's card drawings)
        app = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
        a0 = app.index("const ART = {"); a1 = app.index("\n};", a0) + 3
        tpl = open(os.path.join(ROOT, "tools", "web_template.html"), encoding="utf-8").read()
        os.makedirs(os.path.join(ROOT, "web"), exist_ok=True)
        web = tpl.replace("/*ART*/", app[a0:a1])
        wp = os.path.join(ROOT, "web", "index.html")
        if not os.path.exists(wp) or open(wp, encoding="utf-8").read() != web:
            with open(wp, "w", encoding="utf-8") as f: f.write(web)
        b.close()
    srv.shutdown()
    print(f"previews: {made} new pictures, {pages} pages written, {removed} old pictures removed")
    try:  # search-friendly language homepages, root headlines, sitemap.xml (tools/build_lang.py)
        import importlib.util
        sp = importlib.util.spec_from_file_location("build_lang", os.path.join(ROOT, "tools", "build_lang.py"))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); m.main()
    except Exception as ex:
        print("build_lang failed:", ex)

if __name__ == "__main__":
    sys.exit(main())
