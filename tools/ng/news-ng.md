# Nigeria newsroom task (Swipe2News Nigeria edition) – instructions

Status: prepared 24 Nov 2026, NOT scheduled. The owner decides the schedule.

1. Clone WAY2SEC/swipe2news (main). Read `latest.json` from the `feeds-ng` branch (`git fetch --depth 1 origin feeds-ng`).
2. Pick 8–15 new stories that matter to people in Nigeria: official news first (State House, INEC, CBN, NiMet, NCDC,
   ministries, police), then stories carried by several outlets (`n` ≥ 2). Mix: politics/government, business and the
   naira, Lagos and other states, security, sports, a few world stories. Skip gossip, rumours and single-source claims.
3. Write each card in **English, in our own words** (never copy sentences), 40–60 words, from the facts in the
   sources' text. Name who said a claim. One-line headline that names the event (≤ 60 characters).
4. Fields (same format as `/news.json`): `cat` ("Nigeria · Lagos", "World · Africa", "Sports"), `col` "--c-gov",
   `pic` "logo" (no Nigerian picture library yet – never Indian pictures), `stat` + `statl` (short number/topic +
   what happened), `h`, `p`, `src` (outlet name), `url` (the outlet's own article link, not news.google.com),
   `sec` from politics · business · lagos · security · sports · world, `st` "NG", `loc`, `pub` (WAT, +01:00),
   `d` (dd.mm.yyyy), `t` (HH:MM WAT), `lbl` fact | claim | opinion | forecast, `lang` "en".
5. Put new cards at the top of `editions/ng/news.json`, keep at most 60 stories and only the last 2 days, update `date`
   and `updated` (WAT). Never add the same story twice (same link or same event).
6. Commit ONLY `editions/ng/news.json` ("Nigeria news HH:MM WAT") and push to main. Never touch `news.json`,
   `archive/`, the India tasks or alerts. (Changes to editions/ng/ start no alert, check or IndexNow workflow.)
7. Sensitive news (death, crime, accidents, violence): facts from police or official sources only, no names of
   victims or minors, no graphic detail, no pictures.
