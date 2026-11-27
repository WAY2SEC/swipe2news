#!/usr/bin/env python3
"""Swipe2News copy check: flags card text that copies the source's wording (editorial_policy.md §2).

  python3 tools/copycheck.py NEWS_JSON FEEDS_LATEST_JSON [--all]

Compares each story's English/Telugu headline and summary (h, p, en.h, en.p) with the headline and description the
collector saw for the same article link (url or srcs). A run of 6+ words in a row taken from the source is flagged,
unless it sits inside quotation marks in our text (a short attributed quote). By default only stories from the
last 6 hours are checked (use --all for every story). Exit code 1 when something is flagged.
"""
import datetime as dt, json, re, sys

N = 6
WORD = re.compile(r"[\wఀ-౿ऀ-ॿ']+", re.U)


def words(t):
    return [w.lower() for w in WORD.findall(t or "")]


def unquoted(t):
    return re.sub(r'["“”‘’][^"“”‘’]{0,120}["“”‘’]', " ¦ ", t or "")


def walk_events(feed):
    """url -> source text (titles + descriptions of the whole event)."""
    out = {}
    for ev in feed.get("events", []):
        texts, urls = [], []

        def go(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ("title", "desc", "summary", "description") and isinstance(v, str): texts.append(v)
                    elif k in ("url", "link") and isinstance(v, str): urls.append(v)
                    else: go(v)
            elif isinstance(x, list):
                for v in x: go(v)
        go(ev)
        blob = " \n ".join(texts)
        for u in urls: out[u.split("#")[0]] = out.get(u.split("#")[0], "") + " \n " + blob
    return out


def grams(ws):
    return {tuple(ws[i:i + N]) for i in range(len(ws) - N + 1)}


def recent(s, hours=6):
    p = s.get("pub") or ""
    try:
        t = dt.datetime.fromisoformat(p.replace("Z", "+00:00"))
        return (dt.datetime.now(dt.timezone.utc) - t).total_seconds() < hours * 3600
    except Exception:
        return True


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    news = json.load(open(sys.argv[1], encoding="utf-8"))
    src = walk_events(json.load(open(sys.argv[2], encoding="utf-8")))
    every = "--all" in sys.argv
    bad = 0
    for s in news.get("stories", []):
        if not s.get("h") or s.get("by") == "owner" or s.get("local"): continue
        if not every and not recent(s): continue
        urls = [s.get("url") or ""] + [x.get("u", "") for x in (s.get("srcs") or []) if isinstance(x, dict)]
        text = " \n ".join(src.get(u.split("#")[0], "") for u in urls if u)
        if not text.strip(): continue
        sg = grams(words(text))
        mine = [s.get("h"), s.get("p")] + ([s["en"].get("h"), s["en"].get("p")] if isinstance(s.get("en"), dict) else [])
        hits = []
        for m in mine:
            ws = words(unquoted(m))
            for i in range(len(ws) - N + 1):
                g = tuple(ws[i:i + N])
                if "¦" not in g and g in sg: hits.append(" ".join(g))
        if hits:
            bad += 1
            seen = []
            for h in hits:
                if not any(h in x or x in h for x in seen): seen.append(h)
            print(f"COPY  {s.get('h')[:70]!r}  ({s.get('src')})")
            for h in seen[:4]: print(f"      copied run: “{h}”")
    print(f"copycheck: {bad} story(ies) with copied wording" if bad else "copycheck: OK – no copied runs of 6+ words")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
