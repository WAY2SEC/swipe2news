#!/usr/bin/env python3
"""Swipe2News village reporter payouts for one month.

    python3 tools/payout.py 2026-11                      # stories only
    python3 tools/payout.py 2026-11 --ads ads.csv --views views.csv --out ~/payouts

Counts every published story in archive/<month>-*.json (and news.json) that carries
    "rep":  "<reporter PIN>"   and optionally  "repn": "<reporter name>"
and pays RATE_TEXT per text story, RATE_VIDEO per story with a "vid".

--ads   CSV with columns date,pin,client,amount   (ads a reporter brought in; they get AD_SHARE of amount)
--views CSV exported from Google Analytics with a page path column (/s/<id>) and a views column
        (used for the "top reporters" bonus list; optional)

Writes <out>/payout-<month>.csv (one row per reporter) and payout-<month>-stories.csv (every paid story).
Keep these files OUT of the website repo: they hold people's earnings.
"""
import argparse, csv, glob, json, os, sys

RATE_TEXT = 30      # ₹ per published text/photo story
RATE_VIDEO = 75     # ₹ per published story with a video
AD_SHARE = 0.20     # reporter's share of ad money they bring in
TOP_BONUS = [500, 300, 200]   # ₹ for the 3 most-read reporters of the month (set [] to switch off)
MIN_PAYOUT = 100             # ₹; a smaller total is marked "carry over" to next month
BONUS_MIN_STORIES = 10        # a reporter needs at least this many paid stories that month to win a bonus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sid(s):
    """Same story id as index.html / site_js.js (djb2 over url|h, JS 32-bit int, base36)."""
    t = (s.get("url") or s.get("apply") or "") + "|" + (s.get("h") or "")
    h = 5381
    units = t.encode("utf-16-le")
    for i in range(0, len(units), 2):
        c = units[i] | (units[i + 1] << 8)
        h = ((h << 5) + h + c) & 0xFFFFFFFF
    n, out = h, ""
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    while True:
        n, r = divmod(n, 36)
        out = digits[r] + out
        if not n:
            return out


def stories_for(month):
    files = sorted(glob.glob(os.path.join(ROOT, "archive", month + "-*.json")))
    files.append(os.path.join(ROOT, "news.json"))
    seen = {}
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for s in (d.get("stories") if isinstance(d, dict) else d) or []:
            if not s.get("rep"):
                continue
            dd = s.get("d", "")                       # "07.11.2026"
            iso = dd[6:10] + "-" + dd[3:5] if len(dd) == 10 else ""
            if iso and iso != month:
                continue
            seen.setdefault(sid(s), s)
    return seen


def read_csv(path):
    with open(os.path.expanduser(path), encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(str(x).replace(",", "").replace("₹", "").strip() or 0)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("month", help="YYYY-MM")
    ap.add_argument("--ads")
    ap.add_argument("--views")
    ap.add_argument("--out", default=os.path.expanduser("~/swipe2news-payouts"))
    a = ap.parse_args()
    if len(a.month) != 7 or a.month[4] != "-":
        sys.exit("month must look like 2026-11")

    stories = stories_for(a.month)
    views = {}
    if a.views:
        for r in read_csv(a.views):
            path = next((v for k, v in r.items() if k and "path" in k.lower()), "") or ""
            v = next((num(v) for k, v in r.items() if k and k.lower().strip() in ("views", "screenpageviews", "event count", "eventcount")), 0)
            if "/s/" in path:
                key = path.split("/s/")[1].split("?")[0].split(".")[0].strip("/")
                views[key] = views.get(key, 0) + v

    reps = {}
    def rep(pin):
        return reps.setdefault(str(pin).strip(), {"pin": str(pin).strip(), "name": "", "text": 0, "video": 0,
                                                  "story_pay": 0, "ads_total": 0.0, "ad_pay": 0.0, "views": 0, "bonus": 0})
    rows = []
    for k, s in stories.items():
        r = rep(s["rep"])
        r["name"] = r["name"] or s.get("repn", "")
        is_vid = bool(s.get("vid"))
        pay = RATE_VIDEO if is_vid else RATE_TEXT
        r["video" if is_vid else "text"] += 1
        r["story_pay"] += pay
        r["views"] += int(views.get(k, 0))
        rows.append({"date": s.get("d", ""), "pin": r["pin"], "name": r["name"], "id": k, "link": "https://swipe2news.com/s/" + k,
                     "type": "video" if is_vid else "text", "pay": pay, "views": int(views.get(k, 0)), "headline": s.get("h", "")})

    if a.ads:
        for ad in read_csv(a.ads):
            if not ad.get("pin") or not str(ad.get("date", "")).startswith(a.month):
                continue
            r = rep(ad["pin"])
            r["ads_total"] += num(ad.get("amount"))
    for r in reps.values():
        r["ad_pay"] = round(r["ads_total"] * AD_SHARE)

    if views and TOP_BONUS:
        ranked = sorted((r for r in reps.values() if r["views"] > 0 and r["text"] + r["video"] >= BONUS_MIN_STORIES), key=lambda r: -r["views"])
        for r, b in zip(ranked, TOP_BONUS):
            r["bonus"] = b

    os.makedirs(a.out, exist_ok=True)
    summary = os.path.join(a.out, f"payout-{a.month}.csv")
    detail = os.path.join(a.out, f"payout-{a.month}-stories.csv")
    cols = ["pin", "name", "text", "video", "story_pay", "ads_total", "ad_pay", "views", "bonus", "total", "pay_now"]
    with open(summary, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, cols); w.writeheader()
        for r in sorted(reps.values(), key=lambda r: r["pin"]):
            r["total"] = r["story_pay"] + r["ad_pay"] + r["bonus"]
            r["pay_now"] = "yes" if r["total"] >= MIN_PAYOUT else "carry over"
            w.writerow({c: r[c] for c in cols})
    with open(detail, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, ["date", "pin", "name", "type", "pay", "views", "id", "link", "headline"]); w.writeheader()
        for row in sorted(rows, key=lambda x: (x["pin"], x["date"][6:] + x["date"][3:5] + x["date"][:2])):
            w.writerow(row)

    print(f"Swipe2News reporter payouts {a.month}: {len(rows)} paid stories, {len(reps)} reporters")
    grand = 0
    for r in sorted(reps.values(), key=lambda r: -r["total"]):
        grand += r["total"] if r["pay_now"] == "yes" else 0
        print(f"  {r['pin']:>6}  {r['name'][:24]:<24} text {r['text']:>3}  video {r['video']:>3}  ads ₹{r['ad_pay']:>5}  bonus ₹{r['bonus']:>4}  = ₹{r['total']}  ({r['pay_now']})")
    print(f"  total to pay now: ₹{grand}\n  {summary}\n  {detail}")


if __name__ == "__main__":
    main()
