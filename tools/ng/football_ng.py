#!/usr/bin/env python3
"""Swipe2News Nigeria – football scores and fixtures (no AI), for the ⚽ football bar and football alerts.

  FOOTBALL_DATA_KEY=... python3 tools/ng/football_ng.py      -> editions/ng/football.json

Source: football-data.org API (free plan; needs a free API key in the repo secret FOOTBALL_DATA_KEY).
Free plan covers: Premier League, Champions League, La Liga, Serie A, Bundesliga, Ligue 1, Eredivisie, Primeira Liga,
Championship, World Cup, Euros. (AFCON, NPFL and Super Eagles friendlies are not on the free plan – they can be
added by hand to editions/ng/football-extra.json: [{"t","lg","h","a","hg","ag","state"}].)
Only facts (teams, times, scores, status); no text, logos or pictures are copied. Keeps yesterday → +4 days.
(ESPN's public scoreboard was tried first on 27 Nov 2026 and refuses GitHub's servers with 403 – not used.)
"""
import datetime as dt, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "editions/ng/football.json")
EXTRA = os.path.join(ROOT, "editions/ng/football-extra.json")
WAT = dt.timezone(dt.timedelta(hours=1))
UA = "Swipe2NewsBot/1.0 (+https://swipe2news.com)"
NAMES = {"PL": ("Premier League", 2), "CL": ("Champions League", 2), "PD": ("La Liga", 3), "SA": ("Serie A", 3),
         "BL1": ("Bundesliga", 4), "FL1": ("Ligue 1", 4), "DED": ("Eredivisie", 5), "PPL": ("Primeira Liga", 5),
         "ELC": ("Championship", 5), "WC": ("World Cup", 1), "EC": ("Euros", 2), "BSA": ("Brasileirão", 6)}
NIGERIA = re.compile(r"^Nigeria\b", re.I)
# clubs with Super Eagles players (shown with a 🇳🇬 tag; update as transfers happen)
NAIJA_CLUBS = {
    "Atalanta": "Lookman", "Fulham": "Bassey, Iwobi", "Lille": "Bayo", "Brentford": "Onyeka", "Crystal Palace": "Uche",
    "Wolverhampton": "Ajayi", "Nottingham": "Aina", "Leverkusen": "Boniface, Tella", "Villarreal": "Chukwueze",
    "Leicester": "Ndidi", "Southampton": "Onuachu", "Sevilla": "Ejuke", "Galatasaray": "Osimhen", "Monaco": "Akliouche",
}
BIG = ("Arsenal", "Chelsea", "Liverpool", "Manchester United", "Manchester City", "Tottenham", "Real Madrid", "Barcelona",
       "Bayern", "Paris Saint-Germain", "Inter", "Juventus", "Milan")
STATE = {"SCHEDULED": "pre", "TIMED": "pre", "IN_PLAY": "in", "PAUSED": "in", "FINISHED": "post",
         "POSTPONED": "pre", "SUSPENDED": "in", "CANCELLED": "post", "AWARDED": "post"}


def naija(n): return ", ".join(v for k, v in NAIJA_CLUBS.items() if k in n)


def main():
    key = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
    now = dt.datetime.now(WAT)
    d1, d2 = (now - dt.timedelta(days=1)).date(), (now + dt.timedelta(days=4)).date()
    ms, err = [], ""
    if key:
        url = f"https://api.football-data.org/v4/matches?dateFrom={d1}&dateTo={d2}"
        try:
            req = urllib.request.Request(url, headers={"X-Auth-Token": key, "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            for m in data.get("matches", []):
                c = (m.get("competition") or {}).get("code", "")
                lg, prio = NAMES.get(c, ((m.get("competition") or {}).get("name", ""), 6))
                hn = (m.get("homeTeam") or {}).get("shortName") or (m.get("homeTeam") or {}).get("name") or "TBC"
                an = (m.get("awayTeam") or {}).get("shortName") or (m.get("awayTeam") or {}).get("name") or "TBC"
                ft = (m.get("score") or {}).get("fullTime") or {}
                state = STATE.get(m.get("status"), "pre")
                ng = "ng" if (NIGERIA.match(hn) or NIGERIA.match(an)) else ""
                ms.append({"id": str(m.get("id")), "lg": lg, "code": c, "p": 0 if ng else prio, "t": m.get("utcDate"),
                           "state": state, "clock": "", "detail": m.get("status", "").replace("_", " ").title(),
                           "done": m.get("status") == "FINISHED", "h": hn, "a": an,
                           "hs": (m.get("homeTeam") or {}).get("tla") or hn[:3].upper(), "as": (m.get("awayTeam") or {}).get("tla") or an[:3].upper(),
                           "hg": ft.get("home") if state != "pre" else None, "ag": ft.get("away") if state != "pre" else None,
                           "ng": ng, "naija": ", ".join(x for x in (naija(hn), naija(an)) if x),
                           "big": any(b in hn or b in an for b in BIG), "venue": m.get("venue") or ""})
        except Exception as e:
            err = str(e)[:120]
    else:
        err = "no FOOTBALL_DATA_KEY secret yet"
    try:  # hand-added Super Eagles / AFCON / NPFL fixtures
        for i, x in enumerate(json.load(open(EXTRA, encoding="utf-8"))):
            x = dict(x); x.setdefault("id", f"x{i}"); x.setdefault("code", "extra"); x.setdefault("p", 0)
            x.setdefault("ng", "ng" if (NIGERIA.match(x.get("h", "")) or NIGERIA.match(x.get("a", ""))) else "")
            x.setdefault("naija", ""); x.setdefault("big", False); x.setdefault("done", x.get("state") == "post")
            x.setdefault("hs", x.get("h", "")[:3].upper()); x.setdefault("as", x.get("a", "")[:3].upper()); x.setdefault("detail", "")
            ms.append(x)
    except FileNotFoundError:
        pass
    except Exception as e:
        err = (err + " · extra: " + str(e))[:200]
    ms.sort(key=lambda m: (m.get("t") or "", m.get("p", 6)))
    if not ms and os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
        if old.get("matches"):
            print("no matches fetched – keeping the old file:", err); return
    json.dump({"updated": now.strftime("%Y-%m-%dT%H:%M+01:00"), "source": "football-data.org", "error": err, "matches": ms},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(ms)} matches ({sum(1 for m in ms if m['state'] == 'in')} live)", err)


if __name__ == "__main__":
    main()
