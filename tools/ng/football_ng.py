#!/usr/bin/env python3
"""Swipe2News Nigeria – football scores and fixtures (no AI), for the ⚽ football bar and football alerts.

  python3 tools/ng/football_ng.py            -> editions/ng/football.json

Reads ESPN's public scoreboard JSON for the competitions Nigerians follow most (Super Eagles/Falcons, AFCON and
qualifiers, NPFL, Premier League, Champions League and the big European leagues). Keeps yesterday → +4 days.
Only facts (teams, times, scores, status); no text, logos or pictures are copied.
"""
import concurrent.futures as cf, datetime as dt, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "editions/ng/football.json")
WAT = dt.timezone(dt.timedelta(hours=1))
UA = "Mozilla/5.0 (compatible; Swipe2NewsBot/1.0; +https://swipe2news.com)"
# (espn code, short name shown in the app, priority: lower = shown first)
LEAGUES = [
    ("fifa.world", "World Cup", 1), ("fifa.worldq.caf", "World Cup qualifiers (Africa)", 1),
    ("caf.nations", "AFCON", 1), ("caf.nations_qual", "AFCON qualifiers", 1), ("fifa.friendly", "Friendlies", 2),
    ("fifa.wwc", "Women's World Cup", 1), ("caf.w.nations", "Women's AFCON", 1),
    ("nga.1", "NPFL", 2), ("caf.champions", "CAF Champions League", 3), ("caf.confed", "CAF Confederation Cup", 4),
    ("eng.1", "Premier League", 2), ("uefa.champions", "Champions League", 2), ("uefa.europa", "Europa League", 3),
    ("esp.1", "La Liga", 3), ("ita.1", "Serie A", 3), ("ger.1", "Bundesliga", 4), ("fra.1", "Ligue 1", 4),
    ("tur.1", "Turkish Super Lig", 5), ("eng.fa", "FA Cup", 4), ("eng.league_cup", "EFL Cup", 5),
]
NIGERIA = re.compile(r"^Nigeria\b", re.I)
# clubs with Super Eagles players (shown with a 🇳🇬 tag; update as transfers happen)
NAIJA_CLUBS = {
    "Atalanta": "Lookman", "Galatasaray": "Osimhen", "Fulham": "Bassey, Iwobi", "Lille": "Bayo",
    "Brentford": "Onyeka", "Crystal Palace": "Uche", "Wolverhampton Wanderers": "Ajayi", "Nottingham Forest": "Aina",
    "Bayer Leverkusen": "Boniface, Tella", "Villarreal": "Chukwueze", "Leicester City": "Ndidi",
    "Southampton": "Onuachu", "Sevilla": "Ejuke", "Monaco": "Akliouche",
}
BIG = {"Arsenal", "Chelsea", "Liverpool", "Manchester United", "Manchester City", "Tottenham Hotspur",
       "Real Madrid", "Barcelona", "Bayern Munich", "Paris Saint-Germain", "Inter Milan", "Juventus", "AC Milan"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def league(code, name, prio, d1, d2):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={d1}-{d2}&limit=200"
    try:
        data = get(url)
    except Exception as e:
        return code, [], str(e)[:80]
    out = []
    for ev in data.get("events", []):
        try:
            comp = ev["competitions"][0]
            teams = sorted(comp["competitors"], key=lambda c: 0 if c.get("homeAway") == "home" else 1)
            h, a = teams[0], teams[1]
            st = comp.get("status") or ev.get("status") or {}
            ty = st.get("type", {})
            state = ty.get("state", "pre")  # pre | in | post
            hn, an = h["team"].get("displayName", ""), a["team"].get("displayName", "")
            tag = "ng" if (NIGERIA.match(hn) or NIGERIA.match(an)) else ""
            naija = [NAIJA_CLUBS[x] for x in (hn, an) if x in NAIJA_CLUBS]
            out.append({
                "id": ev.get("id"), "lg": name, "code": code, "p": prio if not tag else 0,
                "t": ev.get("date"), "state": state, "clock": st.get("displayClock", ""),
                "detail": ty.get("shortDetail", ""), "done": bool(ty.get("completed")),
                "h": hn, "a": an, "hs": h["team"].get("abbreviation", hn[:3].upper()), "as": a["team"].get("abbreviation", an[:3].upper()),
                "hg": h.get("score") if state != "pre" else None, "ag": a.get("score") if state != "pre" else None,
                "ng": tag, "naija": ", ".join(naija), "big": bool({hn, an} & BIG),
                "venue": (comp.get("venue") or {}).get("fullName", ""),
            })
        except Exception:
            continue
    return code, out, ""


def main():
    now = dt.datetime.now(WAT)
    d1 = (now - dt.timedelta(days=1)).strftime("%Y%m%d")
    d2 = (now + dt.timedelta(days=4)).strftime("%Y%m%d")
    matches, status = [], {}
    with cf.ThreadPoolExecutor(8) as ex:
        for code, ms, err in ex.map(lambda L: league(*L, d1, d2), LEAGUES):
            status[code] = err or len(ms)
            matches += ms
    seen, uniq = set(), []
    for m in sorted(matches, key=lambda m: (m["t"] or "", m["p"])):
        if m["id"] in seen: continue
        seen.add(m["id"]); uniq.append(m)
    if not uniq and os.path.exists(OUT):
        print("no matches fetched – keeping the old file", status); return
    json.dump({"updated": now.strftime("%Y-%m-%dT%H:%M+01:00"), "source": "ESPN scoreboard (scores and fixtures)",
               "status": status, "matches": uniq}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    live = sum(1 for m in uniq if m["state"] == "in")
    print(f"{len(uniq)} matches ({live} live)", status)


if __name__ == "__main__":
    main()
