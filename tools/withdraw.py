#!/usr/bin/env python3
"""Correct or withdraw a published Swipe2News story (India or Nigeria) – editorial_policy.md §9.

  python3 tools/withdraw.py EDITION STORY KIND "NOTE"

  EDITION  in | ng
  STORY    the story id from its share link (…/s/<id>, …/ng/s/<id>.html or ?s=<id>), the full link, or the
           original article URL
  KIND     withdraw  – hide the story's text everywhere; the card shows "Withdrawn" + NOTE
           correct   – keep the story, show "Corrected: NOTE" on the card (fix the text itself separately if needed)
           remove    – delete the card from the feed completely (legal/takedown requests); no public note
  NOTE     one plain sentence for readers (English; for India it is also used as the Telugu/Hindi line unless
           you add them later)

Updates the edition's news file (India: news.json and the archive file of that day too) and its public
corrections list. Run from GitHub: Actions → "Correct or withdraw a story" → Run workflow.
"""
import datetime as dt, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sid(s):
    if s.get("_sid"): return s["_sid"]
    h = 5381
    for ch in (s.get("url") or "") + "|" + (s.get("h") or ""):
        h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    out = ""
    while True:
        h, r = divmod(h, 36)
        out = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + out
        if not h: return out


def key_of(arg):
    a = arg.strip()
    m = re.search(r"/ng/s/([0-9a-z]+)\.html", a) or re.search(r"/s/([0-9a-z]+)(?:\.html)?(?:[?#]|$)", a) or re.search(r"[?&]s=([0-9a-z]+)", a)
    return (m.group(1), None) if m else ((None, a) if a.startswith("http") else (a, None))


def match(s, k, url):
    return (k and sid(s) == k) or (url and (s.get("url") or "").split("#")[0] == url.split("#")[0])


def main():
    if len(sys.argv) < 5: sys.exit(__doc__)
    ed, story, kind, note = sys.argv[1].lower(), sys.argv[2], sys.argv[3].lower(), sys.argv[4].strip()
    if ed not in ("in", "ng") or kind not in ("withdraw", "correct", "remove") or not note: sys.exit(__doc__)
    k, url = key_of(story)
    tz = dt.timezone(dt.timedelta(hours=1 if ed == "ng" else 5, minutes=0 if ed == "ng" else 30))
    at = dt.datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    files = [os.path.join(ROOT, "editions/ng/news.json")] if ed == "ng" else \
        [os.path.join(ROOT, "news.json")] + sorted(glob.glob(os.path.join(ROOT, "archive/20*.json")))[-4:]
    found = None
    for f in files:
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        lst = d.get("stories") or []
        hit = [s for s in lst if isinstance(s, dict) and match(s, k, url)]
        if not hit: continue
        for s in hit:
            found = found or dict(s)
            if kind == "remove":
                lst.remove(s); continue
            if not s.get("_sid") and ed == "in": s["_sid"] = sid(s)
            c = {"at": at, "en": note}
            if ed == "in": c.update({"te": note, "hi": note})
            s["corr"] = c
            if kind == "withdraw": s["wd"] = True
        if "count" in d: d["count"] = len(lst)
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("updated", os.path.relpath(f, ROOT))
    if not found: sys.exit(f"story not found: {story}")
    if kind != "remove":
        cf = os.path.join(ROOT, "editions/ng/corrections.json" if ed == "ng" else "corrections.json")
        try: c = json.load(open(cf, encoding="utf-8"))
        except Exception: c = {"items": []}
        item = {"at": at, "h": found.get("h", ""), "kind": "withdrawn" if kind == "withdraw" else "corrected",
                "url": found.get("url", ""), "en": note}
        if ed == "in": item.update({"en_h": (found.get("en") or {}).get("h", ""), "te": note, "hi": note})
        c.setdefault("items", []).insert(0, item)
        json.dump(c, open(cf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("updated", os.path.relpath(cf, ROOT))
    print(f"{kind}: {found.get('h')}")


if __name__ == "__main__":
    main()
