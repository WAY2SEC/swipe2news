#!/usr/bin/env python3
"""Swipe2News Nigeria: a WhatsApp link-preview page for every story in editions/ng/news.json.

  ng/s/<id>.html   small article page with og: tags (WhatsApp/Facebook/X show title, summary and picture).
                   Every visitor (owner 26 Nov 2026: "open the link to everyone") jumps straight into the Nigeria app at
                   /ng/?s=<id>, wherever they are; link-preview bots just read the og: tags.
  ng/cards/<id>.jpg 1200x630 preview picture, only for stories with a photo (pic != "logo").
                   Stories without a photo use art/ng/og.jpg (the Swipe2News Nigeria picture).

Pages/cards of stories no longer in the feed are removed to keep the site small.
Needs only Pillow. Run: python3 tools/ng/build_previews_ng.py
"""
import json, os, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://swipe2news.com"
e = lambda x: html.escape(str(x or ""), quote=True)


def sid(s):  # same id as the app (djb2 over url|h, base36)
    h = 5381
    for ch in (s.get("url") or "") + "|" + (s.get("h") or ""):
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    n, out = h, ""
    while True:
        n, r = divmod(n, 36)
        out = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + out
        if not n: return out


def card(s, k):
    """1200x630 crop of the story photo (top-weighted so faces stay in)."""
    out = os.path.join(ROOT, "ng/cards", k + ".jpg")
    if os.path.exists(out): return True
    src = os.path.join(ROOT, "art/ng", s["pic"] + ".jpg")
    if not os.path.exists(src): return False
    from PIL import Image
    im = Image.open(src).convert("RGB")
    W, H = im.size
    r = 1200 / 630
    if W / H > r:
        nw = int(H * r); box = ((W - nw) // 2, 0, (W - nw) // 2 + nw, H)
    else:
        nh = int(W / r); top = int((H - nh) * 0.25); box = (0, top, W, top + nh)
    im.crop(box).resize((1200, 630), Image.LANCZOS).save(out, quality=84, optimize=True)
    return True


def page(s, k, img):
    url = f"{SITE}/ng/s/{k}.html"
    title, desc = s.get("h", ""), s.get("p", "")
    short = desc if len(desc) <= 190 else desc[:187].rsplit(" ", 1)[0] + "…"
    if s.get("wd"): short = "Withdrawn: " + ((s.get("corr") or {}).get("en") or "")
    pic = (f'<img class="ph" src="/ng/cards/{k}.jpg" alt="">' if img != "/art/ng/og.jpg" else "")
    cr = f'<div class="cr">{e(s.get("cr"))}</div>' if s.get("cr") and pic else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Swipe2News Nigeria</title>
<meta name="robots" content="noindex">
<meta name="description" content="{e(short)}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Swipe2News Nigeria">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(short)}">
<meta property="og:url" content="{url}"><link rel="canonical" href="{url}">
<meta property="og:image" content="{SITE}{img}"><meta property="og:image:secure_url" content="{SITE}{img}">
<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}{img}">
<meta name="theme-color" content="#4A0E3F"><link rel="icon" href="/art/logo.svg">
<script>try{{if(!/[?&]stay/.test(location.search)&&!/bot|crawl|spider|facebookexternalhit|WhatsApp|Twitterbot|TelegramBot/i.test(navigator.userAgent))location.replace('/ng/?s={k}');}}catch(x){{}}</script>
<style>body{{margin:0;background:#F5EBDD;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#202124}}
.w{{max-width:560px;margin:0 auto;background:#FFFDF5;min-height:100vh}}
.hd{{display:flex;align-items:center;gap:10px;padding:12px 16px;background:#FFFDF5}}.hd img{{width:38px;height:38px;border-radius:10px}}
.hd b{{font:800 22px system-ui,sans-serif;color:#4A0E3F}}.hd b i{{color:#F5A23A;font-style:normal}}.ng{{background:#0E7A3E;color:#fff;font:800 11px system-ui;padding:3px 8px;border-radius:6px;letter-spacing:1px}}
.pw{{position:relative;background:#4A0E3F}}.ph{{display:block;width:100%;aspect-ratio:1200/630;object-fit:cover}}
.cr{{position:absolute;right:10px;top:10px;background:rgba(0,0,0,.5);color:#fff;font-size:11px;padding:3px 7px;border-radius:6px}}
.in{{padding:18px 18px 28px}}.cat{{display:inline-block;background:#4A0E3F;color:#FFFDF5;font-size:12px;font-weight:700;padding:4px 10px;border-radius:99px}}
h1{{font-size:25px;line-height:1.28;margin:12px 0 6px}}.m{{color:#666;font-size:13px}}p{{font-size:17px;line-height:1.6}}
.src{{font-size:14px;color:#555}}.src a{{color:#4A0E3F;font-weight:700}}
.go{{display:block;text-align:center;margin:22px 0 0;background:#F5A23A;color:#2E0827;font-weight:800;font-size:17px;padding:15px;border-radius:14px;text-decoration:none}}</style>
</head><body><div class="w">
<div class="hd"><img src="/icon-192.png" alt=""><b>swipe2news<i>.</i></b><span class="ng">NIGERIA</span></div>
{('<div class="pw">' + pic + cr + '</div>') if pic else ''}
<div class="in"><span class="cat">{e(s.get("cat"))}</span>
<h1>{e(title)}</h1><div class="m">{e(s.get("d"))} · {e(s.get("t"))} WAT</div>
{('<p style="color:#B3261E"><b>Withdrawn.</b> ' + e((s.get("corr") or {}).get("en")) + '</p>') if s.get("wd") else '<p>' + e(desc) + '</p>'}{('<p style="color:#7a4b00;font-size:14px"><b>Corrected ' + e((s.get("corr") or {}).get("at")) + ':</b> ' + e((s.get("corr") or {}).get("en")) + '</p>') if (s.get("corr") and not s.get("wd")) else ''}
<div class="src">Source: {e(s.get("src"))} · <a href="{e(s.get("url"))}" target="_blank" rel="noopener">Read full story ›</a></div>
<a class="go" href="/ng/?s={k}">Read more Nigeria news on Swipe2News ›</a></div>
</div></body></html>"""


def main():
    d = json.load(open(os.path.join(ROOT, "editions/ng/news.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ROOT, "ng/s"), exist_ok=True); os.makedirs(os.path.join(ROOT, "ng/cards"), exist_ok=True)
    keep = set()
    for s in d.get("stories", []):
        if not s.get("h"): continue
        k = sid(s); keep.add(k)
        img = f"/ng/cards/{k}.jpg" if (s.get("pic") and s["pic"] != "logo" and card(s, k)) else "/art/ng/og.jpg"
        body = page(s, k, img)
        p = os.path.join(ROOT, "ng/s", k + ".html")
        if not os.path.exists(p) or open(p, encoding="utf-8").read() != body:
            open(p, "w", encoding="utf-8").write(body)
    for f in glob.glob(os.path.join(ROOT, "ng/s/*.html")) + glob.glob(os.path.join(ROOT, "ng/cards/*.jpg")):
        if os.path.splitext(os.path.basename(f))[0] not in keep: os.remove(f)
    print(len(keep), "Nigeria preview pages")


if __name__ == "__main__":
    main()
