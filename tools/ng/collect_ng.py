#!/usr/bin/env python3
"""Nigeria edition – collect headlines from Nigerian news sites + Google News Nigeria (no AI).

  python3 tools/ng/collect_ng.py OUT_DIR            # OUT_DIR/latest.json (story groups) + OUT_DIR/status.json (each feed)

Reads tools/ng/feeds.json. For every story it keeps the feed's own id (guid) and a cleaned-up article link, so the
same article is never listed twice; stories with almost the same headline from different outlets are grouped
into one event with all its sources. The writer (newsroom task or a human editor) uses latest.json to pick
stories and write the cards in its own words. This script never writes any news feed and never touches news.json.
"""
import concurrent.futures as cf, datetime as dt, email.utils, hashlib, html, json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "feeds.json"), encoding="utf-8"))
WAT = dt.timezone(dt.timedelta(hours=1))
NOW = dt.datetime.now(dt.timezone.utc)
KEEP_H = 36
UA = "Mozilla/5.0 (compatible; Swipe2NewsBot/1.0; +https://swipe2news.com)"
ATOM = "{http://www.w3.org/2005/Atom}"
STOP = set("the a an of to in on for and or at by with from as is are was were be has have had after over into amid says said new news nigeria nigerian".split())


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def ptime(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def plain(x, n):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(x or ""))).strip()[:n]


def parse(raw):
    root = ET.fromstring(raw)
    out = []
    for it in root.iter("item"):
        src = it.find("source")
        out.append({"t": plain(it.findtext("title"), 300), "u": (it.findtext("link") or "").strip(), "g": (it.findtext("guid") or "").strip(),
                    "p": it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date"),
                    "d": plain(it.findtext("description"), 400), "o": (src.text or "").strip() if src is not None else ""})
    for it in root.iter(ATOM + "entry"):
        ln = it.find(ATOM + "link")
        out.append({"t": plain(it.findtext(ATOM + "title"), 300), "u": ln.get("href") if ln is not None else "", "g": it.findtext(ATOM + "id") or "",
                    "p": it.findtext(ATOM + "published") or it.findtext(ATOM + "updated"), "d": plain(it.findtext(ATOM + "summary"), 400), "o": ""})
    return out


def canonical(u):
    p = urllib.parse.urlsplit((u or "").strip())
    if p.scheme not in ("http", "https") or not p.netloc:
        return (u or "").strip()
    host = p.netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    path = re.sub(r"/(?:amp/?|amp\.html)$", "/", p.path or "/")
    path = re.sub(r"/+$", "", path) or "/"
    drop = re.compile(r"^(utm_.*|fbclid|gclid|ref|ref_src|amp|outputtype|cmpid|from)$", re.I)
    q = urllib.parse.urlencode(sorted((k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True) if not drop.match(k)))
    return urllib.parse.urlunsplit(("https", host, path, q, ""))


def words(t):
    return {w for w in re.findall(r"[a-z0-9₦]+", t.lower()) if w not in STOP and len(w) > 2}


def one(f, kind):
    try:
        got = parse(fetch(f["url"]))
    except Exception as e:
        return f, kind, [], str(e)[:120]
    return f, kind, got, ""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "ng-out"
    jobs = [(f, "direct") for f in CFG["direct"]] + [(f, "gnews") for f in CFG["gnews"]]
    items, status, seen = [], [], set()
    with cf.ThreadPoolExecutor(12) as ex:
        for f, kind, got, err in ex.map(lambda j: one(*j), jobs):
            fresh = 0
            for g in got:
                d = ptime(g["p"])
                if not g["t"] or not d or NOW - d > dt.timedelta(hours=KEEP_H) or d - NOW > dt.timedelta(hours=2):
                    continue
                outlet = g["o"] or f["name"]
                title = re.sub(r"\s+-\s+[^-]{2,60}$", "", g["t"]) if kind == "gnews" else g["t"]   # Google adds " - Outlet"
                canon = canonical(g["u"])
                key = ("g:" + hashlib.sha1((urllib.parse.urlsplit(f["url"]).netloc + "|" + g["g"]).encode()).hexdigest()[:16]) if g["g"] and kind == "direct" else "u:" + hashlib.sha1(canon.encode()).hexdigest()[:16]
                if key in seen or canon in seen:
                    continue
                seen.update([key, canon])
                fresh += 1
                items.append({"title": title, "url": g["u"], "canon": canon, "key": key, "outlet": outlet, "kind": kind, "feed": f["name"],
                              "time": d.astimezone(WAT).isoformat(timespec="minutes"), "desc": g["d"] if kind == "direct" else ""})
            status.append({"name": f["name"], "kind": kind, "ok": not err and bool(got), "items": len(got), "fresh": fresh, "error": err})
    # group near-identical headlines from different outlets into one event
    items.sort(key=lambda x: x["time"], reverse=True)
    events = []
    for it in items:
        w = words(it["title"])
        best = None
        for e in events:
            inter = len(w & e["_w"])
            if w and inter / max(1, min(len(w), len(e["_w"]))) >= 0.6 and inter >= 3:
                best = e
                break
        if best:
            if it["outlet"] not in {s["outlet"] for s in best["sources"]}:
                best["sources"].append({k: it[k] for k in ("outlet", "url", "time", "kind", "desc")})
            best["_w"] |= w
        else:
            events.append({"title": it["title"], "first": it["time"], "key": it["key"], "_w": w,
                           "sources": [{k: it[k] for k in ("outlet", "url", "time", "kind", "desc")}]})
    for e in events:
        e.pop("_w")
        e["n"] = len(e["sources"])
    events.sort(key=lambda e: (e["n"] >= 3, e["first"]), reverse=True)
    os.makedirs(out, exist_ok=True)
    ok = sum(1 for s in status if s["ok"])
    json.dump({"updated": NOW.astimezone(WAT).isoformat(timespec="minutes"), "feeds_ok": ok, "feeds": len(status), "events": events[:250]},
              open(os.path.join(out, "latest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sorted(status, key=lambda s: (not s["ok"], s["name"])), open(os.path.join(out, "status.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{ok}/{len(status)} feeds OK · {len(items)} stories in the last {KEEP_H} h · {len(events)} events · {sum(1 for e in events if e['n'] >= 3)} carried by 3+ outlets")
    for s in sorted(status, key=lambda s: (not s["ok"], s["name"])):
        print(("  OK   " if s["ok"] else "  FAIL ") + f"{s['name']:<36} items {s['items']:>3}  fresh {s['fresh']:>3}  {s['error']}")


if __name__ == "__main__":
    main()
