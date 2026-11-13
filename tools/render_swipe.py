"""Render Swipe2News swipe-page stories into WhatsApp-ready images and captions.

Usage: python3 render_swipe.py <swipe.html> <out_dir> <qr.png>
Fonts: install Nirmala.ttc and ariblk.ttf into ~/.fonts and run fc-cache first.

Writes to <out_dir>:
  00_headlines.jpg  one card listing every story's headline (post this one per run)
  01_story.jpg ...  one card per story
  captions.txt      ready-to-paste WhatsApp captions (headlines post + one per story)
  instagram/        NN_post.jpg (1080x1350), NN_story.jpg (1080x1920), instagram_captions.txt
"""
import sys, base64, pathlib, html as H
import html as H_
from playwright.sync_api import sync_playwright

CHANNEL = "https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138"
src, out, qr = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
qr_uri = "data:image/png;base64," + base64.b64encode(open(qr, "rb").read()).decode()
page_html = open(src, encoding="utf-8").read()
extra = f"""<style>
.bottom{{display:none!important}} .hint{{display:none!important}}
.qrfoot{{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 16px;background:#16130F;color:#FBF7F0;font-weight:800;font-size:13px}}
.qrfoot img{{width:64px;height:64px;background:#fff;padding:3px;box-sizing:border-box}}
</style>"""
page = ('<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        '<body style="margin:0;font:14px system-ui">' + page_html + extra + '</body></html>')
tmp = out / "_render.html"
tmp.write_text(page, encoding="utf-8")

HEAD_CSS = """
*{box-sizing:border-box} body{margin:0;background:#FFFDF5;font-family:'Nirmala UI','Noto Sans Telugu',sans-serif;color:#1A1410}
.card{width:400px}
header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:#fff;border-bottom:4px solid #4A0E3F}
header img{height:40px} .d{text-align:right;font-size:12px;font-weight:600;line-height:1.35} .d b{font-family:'Arial Black',sans-serif;font-size:14px}
.t{padding:14px 16px 6px} .t small{color:#4A0E3F;font-weight:800;font-size:11px;letter-spacing:1px} .t h1{margin:2px 0 0;font-size:24px;line-height:1.3}
ol{list-style:none;margin:0;padding:0 16px}
li{display:flex;gap:10px;padding:9px 0;border-top:1px solid #E3D9C8} li:first-child{border-top:2px solid #1A1410}
.n{font-family:'Arial Black',sans-serif;color:#4A0E3F;font-size:15px;width:24px;flex-shrink:0;padding-top:2px}
.h{font-size:15px;font-weight:700;line-height:1.45} .s{font-size:10.5px;color:#5E5246;font-weight:600;margin-top:2px}
.qrfoot{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;padding:8px 16px;background:#16130F;color:#FBF7F0;font-weight:800;font-size:13px}
.qrfoot img{width:64px;height:64px;background:#fff;padding:3px}
"""


COLS = {'--c-election':'#B3400F','--c-gov':'#1F6B3A','--c-money':'#16406E','--c-water':'#0B5CAD','--c-power':'#5B3A8C','--c-city':'#7A4A12'}
APP = "swipe2news.com"
IG_CSS = """
*{box-sizing:border-box} body{margin:0;font-family:'Nirmala UI','Noto Sans Telugu',sans-serif;color:#1A1410}
.c{width:400px;display:flex;flex-direction:column;background:#FFFDF5;overflow:hidden}
.pn{position:relative;color:#fff;padding:16px 18px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;flex-shrink:0}
.pn svg{position:absolute;right:-6px;top:8px;bottom:8px;height:calc(100% - 16px);opacity:.28}
.pn>*:not(svg){position:relative}
.top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.chip{border:1.5px solid #fff;border-radius:99px;padding:2px 11px;font-size:12px;font-weight:800}
.dt{font-size:11px;font-weight:700}
.st{font-family:'Arial Black',sans-serif;font-size:44px;line-height:1.05;letter-spacing:-1px}
.st.te{font-family:'Nirmala UI',sans-serif;font-weight:800;font-size:38px}
.sl{font-size:15px;font-weight:800;line-height:1.35;max-width:21ch}
.sb{background:#2E0827;color:#fff;padding:8px 18px;flex-shrink:0}
.sb .a{font-family:'Arial Black',sans-serif;font-size:15px;letter-spacing:1px}.sb .a i{font-style:normal;color:#E8243F}
.sb .t{font-size:14px;font-weight:800;color:#F5A23A;margin-left:6px}
.sb .r{font-size:10.5px;font-weight:800;color:#D6DEEA;margin-top:2px}.sb .r span{color:#AFC0D6;font-weight:600}
.tx{flex:1;min-height:0;padding:12px 18px 8px;display:flex;flex-direction:column;gap:7px;overflow:hidden}
h2,p,.src{flex-shrink:0}
h2{margin:0;font-size:19px;line-height:1.38;font-weight:800}
p{margin:0;font-size:14px;line-height:1.6;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
.src{margin-top:auto;padding-top:6px;border-top:1px solid #E3D9C8;font-size:11.5px;color:#5E5246;font-weight:600}.src b{color:#1A1410}
.ft{background:#16130F;color:#FBF7F0;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 18px;font-size:12.5px;font-weight:800;flex-shrink:0}
.ft img.q{width:58px;height:58px;background:#fff;padding:3px}
.ft img.l{height:20px}
.story h2{font-size:23px}.story p{font-size:16px}.story .st{font-size:56px}.story .st.te{font-size:46px}.story .sl{font-size:17px}
"""
def ig_tags(s):
    t = ["#Swipe2News", "#TeluguNews", "#తెలుగువార్తలు"]
    sec = s.get("sec") or []
    if "telangana" in sec or s.get("place", "TS") != "TS": t += ["#TelanganaNews", "#Telangana"]
    if s.get("place") == "hyderabad": t += ["#HyderabadNews", "#Hyderabad"]
    extra = {"india": "#IndiaNews", "world": "#WorldNews", "ai": "#AINews", "jobs": "#Jobs", "business": "#BusinessNews",
             "education": "#Education", "agri": "#Farmers", "weather": "#Weather", "sports": "#Sports", "culture": "#Culture", "innovation": "#Innovation"}
    t += [extra[k] for k in sec if k in extra]
    seen = []
    [seen.append(x) for x in t if x not in seen]
    return " ".join(seen[:10])

def insta(b, stories, art, logo_light, date):
    ig = out / "instagram"; ig.mkdir(exist_ok=True)
    pg = b.new_page(viewport={"width": 400, "height": 800}, device_scale_factor=2.7, color_scheme="light")
    caps = []
    for k, s in enumerate(stories):
        col = COLS.get(s.get("col"), "#1F6B3A")
        te = any("ఀ" <= ch <= "౿" for ch in str(s.get("stat", "")))
        svg = f'<svg viewBox="0 0 200 200" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{art.get(s.get("art"), "")}</svg>'
        for kind, H, PH in (("post", 500, 178), ("story", 711, 250)):
            html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{IG_CSS}</style></head><body>'
                    f'<div class="c {kind}" style="height:{H}px"><div class="pn" style="background:{col};height:{PH}px">{svg}'
                    f'<div class="top"><span class="chip">{H_.escape(s.get("cat",""))}</span><span class="dt">{H_.escape(s.get("d") or date)}</span></div>'
                    f'<div><div class="st{" te" if te else ""}">{H_.escape(str(s.get("stat","")))}</div><div class="sl">{H_.escape(s.get("statl",""))}</div></div></div>'
                    f'<div class="sb"><span class="a">WAY<i>2</i>SEC</span><span class="t">ఒక్క స్వైప్‌లో వార్తలు!</span>'
                    f'<div class="r">Know More. Scroll Less. <span>· తక్కువ స్క్రోల్, ఎక్కువ సమాచారం</span></div></div>'
                    f'<div class="tx"><h2 style="color:{col}">{H_.escape(s["h"])}</h2><p id="p">{H_.escape(s["p"])}</p>'
                    f'<div class="src">Source | మూలం: <b>{H_.escape(s.get("src",""))}</b></div></div>'
                    f'<div class="ft">' + (f'<span>పూర్తి వార్తలు: {APP}<br>లింక్ బయోలో ↑</span><img class="l" src="{logo_light}">' if kind == "post"
                    else f'<span>Swipe2News యాప్: {APP}<br>స్కాన్ చేసి ఛానెల్‌లో చేరండి</span><img class="q" src="{qr_uri}">') +
                    '</div></div></body></html>')
            pg.set_content(html); pg.wait_for_timeout(150)
            # shrink the summary until everything fits
            pg.evaluate("""()=>{const c=document.querySelector('.c'),t=document.querySelector('.tx'),p=document.getElementById('p');
              for(let n=12;n>=2;n--){p.style.webkitLineClamp=n; if(t.scrollHeight<=t.clientHeight+1) break;}
              if(t.scrollHeight>t.clientHeight+1){p.style.display='none'}}""")
            pg.locator(".c").screenshot(path=str(ig / f"{k+1:02d}_{kind}.jpg"), type="jpeg", quality=90)
        caps += ["", f"--- {k+1:02d}_post.jpg / {k+1:02d}_story.jpg ---", f"🔴 {s['h']}", "", s["p"], "",
                 f"Source | మూలం: {s.get('src','')}", f"📲 పూర్తి వార్తలు, జిల్లా వార్తలు: {APP} (link in bio)", "", ig_tags(s)]
    pg.close()
    head = ["Instagram captions – Swipe2News", "Feed: post NN_post.jpg (1080x1350). Story: NN_story.jpg (1080x1920) + link sticker https://" + APP, "=" * 40]
    (ig / "instagram_captions.txt").write_text("\n".join(head + caps) + "\n", encoding="utf-8")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 400, "height": 820}, device_scale_factor=2.7, color_scheme="light")
    pg.goto(tmp.resolve().as_uri()); pg.wait_for_timeout(500)
    stories = pg.evaluate("typeof STORIES!=='undefined' ? STORIES : []")
    logo = pg.evaluate("(document.querySelector('header img')||{}).src || ''")
    date = pg.evaluate("((document.querySelector('header .hmeta b')||{}).textContent||'').trim()")
    # one card per story, each with a QR footer
    pg.evaluate("""(qr)=>{document.querySelectorAll('.story').forEach(s=>{const d=document.createElement('div');d.className='qrfoot';d.innerHTML='<span>స్కాన్ చేసి Swipe2News ఛానెల్‌లో చేరండి</span><img alt="" src="'+qr+'">';s.appendChild(d);});}""", qr_uri)
    n = pg.evaluate("document.querySelectorAll('.story').length")
    for i in range(n):
        pg.evaluate(f"document.querySelectorAll('.story')[{i}].scrollIntoView({{behavior:'auto'}})")
        pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / f"{i+1:02d}_story.jpg"), type="jpeg", quality=90)
    # one headlines card listing every story (max 8 so it stays readable)
    items = "".join(
        f'<li><div class="n">{k+1:02d}</div><div><div class="h">{H.escape(s["h"])}</div>'
        f'<div class="s">Source | మూలం: {H.escape(s["src"])}</div></div></li>'
        for k, s in enumerate(stories[:8]))
    head = (f'<!doctype html><html><head><meta charset="utf-8"><style>{HEAD_CSS}</style></head><body><div class="card">'
            f'<header><img src="{logo}" alt=""><div class="d"><b>{H.escape(date)}</b><br>తెలంగాణ వార్తలు</div></header>'
            f'<div class="t"><small>TELANGANA · తెలంగాణ</small><h1>తాజా ముఖ్యాంశాలు</h1></div><ol>{items}</ol>'
            f'<div class="qrfoot"><span>పూర్తి వార్తల కోసం స్కాన్ చేసి Swipe2News ఛానెల్‌లో చేరండి</span><img alt="" src="{qr_uri}"></div>'
            f'</div></body></html>')
    hp = b.new_page(viewport={"width": 400, "height": 600}, device_scale_factor=2.7, color_scheme="light")
    hp.set_content(head); hp.wait_for_timeout(300)
    hp.locator(".card").screenshot(path=str(out / "00_headlines.jpg"), type="jpeg", quality=90)
    art = pg.evaluate("typeof ART!=='undefined' ? ART : {}")
    logo_light = pg.evaluate("typeof LOGO_LIGHT!=='undefined' ? LOGO_LIGHT : ''") or logo
    insta(b, stories, art, logo_light, date)
    b.close()
tmp.unlink()

# captions
lines = [f"🔴 Swipe2News | తెలంగాణ వార్తలు – {date}", ""]
lines += [f"{k+1}. {s['h']}" for k, s in enumerate(stories[:8])]
srcs = sorted({x.strip() for s in stories[:8] for x in s["src"].split("·")})
lines += ["", "Source | మూలం: " + ", ".join(srcs), "", f"👉 Swipe2News ఛానెల్‌లో చేరండి: {CHANNEL}", ""]
lines += ["=" * 40, "ఒక్కో కార్డు క్యాప్షన్ (Caption for each card)", "=" * 40]
for k, s in enumerate(stories):
    lines += ["", f"--- {k+1:02d}_story.jpg ---", f"🔴 {s['h']}", "", s["p"], "",
              f"Source | మూలం: {s['src']}", f"పూర్తి వార్త: {s['url']}", f"👉 {CHANNEL}"]
(out / "captions.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(n, "story cards + 00_headlines.jpg + captions.txt written to", out)
