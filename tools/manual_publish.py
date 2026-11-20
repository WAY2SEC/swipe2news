#!/usr/bin/env python3
"""Swipe2News manual publishing (no Claude needed) – run by .github/workflows/publish-manual.yml.

  python3 tools/manual_publish.py fetch     # queued drafts from the newsroom Sheet -> news.json + archive (+ report)
  python3 tools/manual_publish.py mark      # after a successful push: mark them published / rejected in the Sheet

The editor writes a card at /editor/ (tab ✍️ New story); the newsroom Apps Script keeps it in the "Drafts" sheet.
Environment (GitHub secrets / variables – never in files):
  NEWSROOM_URL       the newsroom web app URL (Apps Script)
  NEWSROOM_BOT_KEY   the newsroom BOT_KEY
  S2N_SITE           site address used in links (default https://swipe2news.com)

Safe to run again: every published card carries "mid" (the draft id). A draft whose mid is already in news.json or
any archive day is never added twice – it is only marked published again. Drafts that fail the story checker
(tools/check_news.py) are not published and are marked "rejected" with the reasons.
"""
import datetime, glob, json, os, re, sys, urllib.request, ssl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_news  # noqa: E402  (reuse the newsroom's own checks)

SITE = os.environ.get("S2N_SITE", "https://swipe2news.com").rstrip("/")
STATE = os.path.join(ROOT, ".manual-publish.json")      # hand-over between "fetch" and "mark" (not committed)
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

REGION = {  # region -> st, sec, Telugu / English / Hindi category name (same values the newsroom uses)
    "telangana": ("TG", ["telangana"], "తెలంగాణ", "Telangana", "तेलंगाना"),
    "ap": ("AP", ["telangana"], "ఏపీ", "AP", "आंध्र प्रदेश"),
    "india": ("IN", ["india"], "భారత్", "India", "भारत"),
    "world": ("WORLD", ["world"], "ప్రపంచం", "World", "दुनिया"),
}
TOPICS = {"business", "education", "jobs", "agri", "weather", "culture", "sports", "innovation"}
COLOUR = {"business": "--c-money", "agri": "--c-water", "weather": "--c-water", "election": "--c-election"}
LABELS = {"fact", "claim", "opinion", "forecast"}


def sid(s):
    """Same id as sid() in index.html: djb2 over UTF-16 units of url|h, unsigned, base 36."""
    if s.get("_sid"):
        return s["_sid"]
    t = (s.get("url") or "") + "|" + (s.get("h") or "")
    b = t.encode("utf-16-le")
    h = 5381
    for i in range(0, len(b), 2):
        h = ((h << 5) + h + (b[i] | (b[i + 1] << 8))) & 0xFFFFFFFF
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while True:
        h, r = divmod(h, 36)
        out = digits[r] + out
        if not h:
            return out


def newsroom(action, **kw):
    url, key = os.environ.get("NEWSROOM_URL", ""), os.environ.get("NEWSROOM_BOT_KEY", "")
    if not url or not key:
        sys.exit("NEWSROOM_URL / NEWSROOM_BOT_KEY are not set (add them as GitHub Actions secrets)")
    body = json.dumps(dict(kw, action=action, key=key)).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "text/plain;charset=utf-8"})
    ca = "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else None
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def load(p, default):
    try:
        return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
    except Exception:
        return default


def save(p, d):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    json.load(open(os.path.join(ROOT, p), encoding="utf-8"))  # validate


def clean(x, n):
    return re.sub(r"[<>]", "", str(x or "")).strip()[:n]


def build(draft_id, d, now):
    """Draft from the editor form -> a story in the same shape as the newsroom's stories."""
    region = d.get("region") if d.get("region") in REGION else "telangana"
    st, sec, cte, cen, chi = REGION[region]
    topic = d.get("topic") or ""
    sec = list(sec) + ([topic] if topic in TOPICS else [])
    loc = clean(d.get("loc"), 40)
    s = {
        "cat": cte + (" · " + loc if loc else ""),
        "col": COLOUR.get(topic, "--c-gov"),
        "pic": clean(d.get("pic"), 60),
        "stat": clean(d.get("stat"), 30),
        "statl": clean(d.get("statl"), 40),
        "h": clean(d.get("h"), 120),
        "p": clean(d.get("p"), 1200),
        "src": clean(d.get("src"), 80),
        "url": clean(d.get("url"), 500),
        "sec": sec,
        "st": st,
        "loc": loc,
        "pub": now.strftime("%Y-%m-%dT%H:%M+05:30"),
        "lbl": d.get("lbl") if d.get("lbl") in LABELS else "fact",
        "d": now.strftime("%d.%m.%Y"),
        "t": now.strftime("%H:%M"),
        "mid": draft_id,          # manual draft id – makes re-runs safe (never published twice)
        "manual": True,
    }
    pts = [clean(x, 160) for x in (d.get("pts") or []) if clean(x, 160)][:4]
    if pts:
        s["pts"] = pts
    if clean(d.get("why"), 200):
        s["why"] = clean(d.get("why"), 200)
    for L, cname in (("en", cen), ("hi", chi)):
        t = d.get(L) or {}
        if clean(t.get("h"), 120) and clean(t.get("p"), 1200):
            tl = clean(t.get("loc"), 40)
            s[L] = {"cat": cname + (" · " + tl if tl else ""), "h": clean(t.get("h"), 120), "p": clean(t.get("p"), 1200)}
            for k in ("stat", "statl"):
                if clean(t.get(k), 40):
                    s[L][k] = clean(t.get(k), 40)
            if tl:
                s[L]["loc"] = tl
    return s


def published_index():
    """mid -> (sid, day) and the set of source links of everything already published (news.json + archive)."""
    mids, urls = {}, set()
    files = [os.path.join(ROOT, "news.json")] + sorted(glob.glob(os.path.join(ROOT, "archive", "20*.json")))
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for s in (d.get("stories", []) if isinstance(d, dict) else d):
            if s.get("mid"):
                mids[s["mid"]] = sid(s)
            if s.get("url"):
                urls.add(s["url"].strip())
    return mids, urls


def fetch():
    j = newsroom("drafts")
    if not j.get("ok"):
        sys.exit("newsroom refused the request: %s (is the newsroom script updated and the BOT key right?)" % j.get("error"))
    items = j.get("items") or []
    now = datetime.datetime.now(IST)
    mids, urls = published_index()
    new, done, report = [], [], []
    for it in items:
        did = str(it.get("id") or "")
        if not re.match(r"^d[0-9a-z-]{8,40}$", did):
            continue
        if did in mids:  # published before (e.g. a run that pushed but could not mark it) – only mark it again
            done.append({"id": did, "status": "published", "link": f"{SITE}/s/{mids[did]}", "note": "already published"})
            report.append(f"- already live: {did} → {SITE}/s/{mids[did]}")
            continue
        s = build(did, it.get("story") or {}, now)
        errs, warns, _ = check_news.check({"stories": [s]})
        if s["url"] in urls or any(x["url"] == s["url"] for x in new):
            errs.append("the same source link is already published")
        if errs:
            done.append({"id": did, "status": "rejected", "note": "; ".join(errs)[:480]})
            report.append(f"- REJECTED {did} \"{s['h'][:50]}\": " + "; ".join(errs))
            continue
        new.append(s)
        done.append({"id": did, "status": "published", "link": f"{SITE}/s/{sid(s)}"})
        report.append(f"- PUBLISHED {did} \"{s['h'][:50]}\" → {SITE}/s/{sid(s)}" + (" (to look at: " + "; ".join(warns) + ")" if warns else ""))

    if new:
        news = load("news.json", {"stories": []})
        news["stories"] = new[::-1] + news.get("stories", [])  # newest draft first
        news["date"] = now.strftime("%d.%m.%Y")
        news["updated"] = now.strftime("%Y-%m-%dT%H:%M:00+05:30")
        news["version"] = 2
        save("news.json", news)
        iso = now.strftime("%Y-%m-%d")
        ap = os.path.join("archive", iso + ".json")
        arch = load(ap, {"date": now.strftime("%d.%m.%Y"), "iso": iso, "count": 0, "stories": []})
        have = {x.get("mid") for x in arch.get("stories", []) if x.get("mid")}
        arch["stories"] = [x for x in new[::-1] if x["mid"] not in have] + arch.get("stories", [])
        arch["count"] = len(arch["stories"])
        save(ap, arch)
        idx = load(os.path.join("archive", "index.json"), {"dates": []})
        dates = [x for x in idx.get("dates", []) if x.get("iso") != iso]
        idx["dates"] = sorted(dates + [{"iso": iso, "date": arch["date"], "count": arch["count"]}], key=lambda x: x["iso"], reverse=True)
        save(os.path.join("archive", "index.json"), idx)

    json.dump({"done": done, "published": len(new)}, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
    summary = [f"Queued drafts: {len(items)} · published now: {len(new)} · rejected: {sum(1 for x in done if x['status'] == 'rejected')}"] + report
    print("\n".join(summary))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("## Manual stories\n\n" + "\n".join(summary) + "\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"published={len(new)}\nhandled={len(done)}\n")


def mark():
    st = load(STATE, {"done": []})
    bad = 0
    for x in st.get("done", []):
        try:
            r = newsroom("draftdone", **x)
            ok = r.get("ok")
        except Exception as e:  # the story is live; the next run sees its mid and marks it again
            ok, r = False, {"error": str(e)}
        print(("marked " if ok else "could not mark ") + x["id"] + " " + x["status"] + ("" if ok else f" ({r.get('error')})"))
        bad += 0 if ok else 1
    if bad:
        print("::warning::Some drafts could not be marked in the Sheet – running the workflow again fixes this without duplicates.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        fetch()
    elif cmd == "mark":
        mark()
    else:
        sys.exit(__doc__)
