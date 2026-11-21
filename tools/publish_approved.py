#!/usr/bin/env python3
"""Publish editor-approved RSS stories to a TEST feed (no AI anywhere in this path).

  python3 tools/publish_approved.py publish     # approved rows from the editor queue -> test feed, then mark them published
  python3 tools/publish_approved.py rollback    # put back the test feed exactly as it was before the last publish
  python3 tools/publish_approved.py status      # test feed hash, story count and saved versions

Environment (GitHub Actions secrets / variables, never files):
  NEWSROOM_URL, NEWSROOM_BOT_KEY   the newsroom (Apps Script) web app and its BOT key
  S2N_TEST_FEED                    the test feed to write (default staging/news.json)
  S2N_SITE                         address used for story links (default https://staging.swipe2news.com)

Safety:
  * Only rows the editor approved with "rssapprove" come back, as the exact approved text + its SHA-256.
    A row whose text no longer matches its hash is refused.
  * The card is published word for word as approved; only the date/time and the fixed category fields are added.
  * It refuses to write the live news.json or anything under archive/ (test feed only, for now).
  * Re-running is safe: each card carries "rv" (the queue row id); a row already in the feed is only marked again.
  * Before every change the current test feed is saved to <feed dir>/history/, so "rollback" restores it byte for byte.
"""
import datetime, glob, hashlib, json, os, shutil, ssl, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_news  # noqa: E402  (the newsroom's own story checks)

FEED = os.path.abspath(os.path.join(ROOT, os.environ.get("S2N_TEST_FEED", "staging/news.json")))
HIST = os.path.join(os.path.dirname(FEED), "history")
SITE = os.environ.get("S2N_SITE", "https://staging.swipe2news.com").rstrip("/")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
LIVE = {os.path.join(ROOT, "news.json"), os.path.join(ROOT, "jobs.json")}
REGION = {  # same values the newsroom uses for st / sec / Telugu category
    "telangana": ("TG", ["telangana"], "తెలంగాణ"), "ap": ("AP", ["telangana"], "ఏపీ"),
    "india": ("IN", ["india"], "భారత్"), "world": ("WORLD", ["world"], "ప్రపంచం"),
}
TOPICS = {"business", "education", "jobs", "agri", "weather", "culture", "sports", "innovation"}
COLOUR = {"business": "--c-money", "agri": "--c-water", "weather": "--c-water", "election": "--c-election"}


def guard():
    if FEED in LIVE or FEED.startswith(os.path.join(ROOT, "archive") + os.sep):
        sys.exit(f"refusing to write {os.path.relpath(FEED, ROOT)}: this tool only writes a TEST feed (S2N_TEST_FEED)")


def sid(s):  # same as sid() in index.html
    t = (s.get("url") or "") + "|" + (s.get("h") or "")
    b, h = t.encode("utf-16-le"), 5381
    for i in range(0, len(b), 2):
        h = ((h << 5) + h + (b[i] | (b[i + 1] << 8))) & 0xFFFFFFFF
    out = ""
    while True:
        h, r = divmod(h, 36)
        out = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + out
        if not h:
            return out


def newsroom(action, **kw):
    url, key = os.environ.get("NEWSROOM_URL", ""), os.environ.get("NEWSROOM_BOT_KEY", "")
    if not url or not key:
        sys.exit("NEWSROOM_URL / NEWSROOM_BOT_KEY are not set")
    req = urllib.request.Request(url, data=json.dumps(dict(kw, action=action, key=key)).encode(), headers={"Content-Type": "text/plain;charset=utf-8"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def fhash(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "-"


def card_to_story(rid, c, now):
    st, sec, cte = REGION[c["region"]]
    topic = c.get("topic") or ""
    s = {
        "cat": cte + (" · " + c["loc"] if c.get("loc") else ""), "col": COLOUR.get(topic, "--c-gov"), "pic": c["pic"],
        "stat": c["stat"], "statl": c["statl"], "h": c["h"], "p": c["p"], "src": c["src"], "url": c["url"],
        "sec": sec + ([topic] if topic in TOPICS else []), "st": st, "loc": c.get("loc", ""),
        "pub": now.strftime("%Y-%m-%dT%H:%M+05:30"), "lbl": c["lbl"], "d": now.strftime("%d.%m.%Y"), "t": now.strftime("%H:%M"),
        "rv": rid,   # queue row id: makes re-runs safe
    }
    return s


def publish():
    guard()
    j = newsroom("rssapproved")
    if not j.get("ok"):
        sys.exit("editor queue refused: %s" % j.get("error"))
    feed = json.load(open(FEED, encoding="utf-8")) if os.path.exists(FEED) else {"date": "", "updated": "", "version": 2, "stories": []}
    have = {s.get("rv"): s for s in feed.get("stories", []) if s.get("rv")}
    urls = {s.get("url") for s in feed.get("stories", [])}
    now = datetime.datetime.now(IST)
    new, marks = [], []
    for it in j.get("items", []):
        rid, text, h = it.get("id", ""), it.get("approved", ""), str(it.get("hash", ""))
        if rid in have:   # published before (e.g. the mark step failed) – mark again, never add twice
            marks.append({"id": rid, "link": f"{SITE}/s/{sid(have[rid])}"})
            print(f"already in the test feed: {rid}")
            continue
        if h.replace("sha256:", "") != hashlib.sha256(text.encode("utf-8")).hexdigest():
            print(f"REFUSED {rid}: approved text does not match its hash")
            continue
        c = json.loads(text)
        s = card_to_story(rid, c, now)
        errs, warns, _ = check_news.check({"stories": [s]})
        if c["url"] in urls:
            errs.append("this source link is already in the test feed")
        if errs:
            print(f"NOT PUBLISHED {rid}: " + "; ".join(errs))
            continue
        assert all(s[k] == c[k] for k in ("h", "p", "stat", "statl", "pic", "src", "url", "lbl")), "card changed after approval"
        new.append(s); urls.add(c["url"])
        marks.append({"id": rid, "link": f"{SITE}/s/{sid(s)}"})
        print(f"PUBLISHED {rid} \"{c['h']}\" (approved by {it.get('by')}, {h[:19]}…)" + (f" – to look at: {'; '.join(warns)}" if warns else ""))
    if new:
        os.makedirs(HIST, exist_ok=True)
        snap = os.path.join(HIST, now.strftime("%Y%m%dT%H%M%S") + "-" + fhash(FEED)[:12] + ".json")
        if os.path.exists(FEED):
            shutil.copy2(FEED, snap)
        else:
            open(snap, "w").write("null")   # "no feed yet" – rollback removes the file
        feed["stories"] = new[::-1] + feed.get("stories", [])
        feed.update(date=now.strftime("%d.%m.%Y"), updated=now.strftime("%Y-%m-%dT%H:%M:00+05:30"), version=2)
        tmp = FEED + ".tmp"
        os.makedirs(os.path.dirname(FEED), exist_ok=True)
        json.dump(feed, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.load(open(tmp, encoding="utf-8"))
        os.replace(tmp, FEED)
        print(f"test feed: {os.path.relpath(FEED, ROOT)} now {len(feed['stories'])} stories, sha256 {fhash(FEED)[:12]} (before: {os.path.basename(snap)})")
    else:
        print("nothing new to publish")
    json.dump(marks, open(os.path.join(os.path.dirname(FEED), ".to-mark.json"), "w"))
    if "--no-mark" not in sys.argv:
        mark()


def mark():
    p = os.path.join(os.path.dirname(FEED), ".to-mark.json")
    for m in (json.load(open(p)) if os.path.exists(p) else []):
        try:
            ok = newsroom("reviewpublished", id=m["id"], link=m["link"]).get("ok")
        except Exception as e:
            ok = False
            print(f"could not mark {m['id']}: {e}")
        print(("marked published " if ok else "NOT marked ") + m["id"])
    if os.path.exists(p):
        os.remove(p)


def rollback():
    guard()
    snaps = sorted(glob.glob(os.path.join(HIST, "*.json")))
    if not snaps:
        sys.exit("no saved version to roll back to")
    last, before = snaps[-1], fhash(FEED)
    undone = os.path.join(HIST, "undone")
    os.makedirs(undone, exist_ok=True)
    if os.path.exists(FEED):
        shutil.copy2(FEED, os.path.join(undone, os.path.basename(last).split("-")[0] + "-rolled-back-" + before[:12] + ".json"))
    if open(last).read().strip() == "null":
        os.remove(FEED)
    else:
        shutil.copy2(last, FEED)
    os.remove(last)
    print(f"rolled back: {before[:12]} -> {fhash(FEED)[:12]} (restored {os.path.basename(last)}; the undone version is kept in history/undone/)")


def status():
    n = len(json.load(open(FEED, encoding="utf-8")).get("stories", [])) if os.path.exists(FEED) else 0
    print(f"{os.path.relpath(FEED, ROOT)}: {n} stories, sha256 {fhash(FEED)[:12]}; saved versions: {len(glob.glob(os.path.join(HIST, '*.json')))}")


if __name__ == "__main__":
    {"publish": publish, "rollback": rollback, "status": status, "mark": mark}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
