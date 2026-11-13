# Swipe2News — Jobs (జాబ్స్) update (scheduled task, 08:20 and 17:20 IST)

Keep jobs.json in https://swipe2news.com (repo WAY2SEC/swipe2news) current with government AND private openings Telugu readers can apply for now. Telugu text plus faithful English ("en") and Hindi ("hi") versions. Real current India time. Unattended run: don't ask questions.

1. GET THE REPO: mcp__claude-code-remote__add_repo owner "WAY2SEC", repo "swipe2news", access "push"; `git clone --depth 1 https://github.com/WAY2SEC/swipe2news /home/claude/swipe2news`. Read jobs.json {"updated","version":1,"jobs":[…]}.

2. CLEAN UP: remove jobs whose "last" (DD.MM.YYYY) is before today, and jobs with no "last" whose "d" is more than 21 days ago. Apply extensions/cancellations found on official pages.

3. RESEARCH (WebSearch several queries in one turn, WebFetch to read). Openings whose window is OPEN today:
 GOVERNMENT — Telangana ("tg": TGPSC, TGLPRB, DSC, TGSRTC, power utilities, SCCL, High Court, district/DMHO/NHM, MHSRB); Andhra Pradesh ("ap": APPSC, SLPRB, DSC, APSRTC, High Court, districts); central ("central"; PSUs "psu"); "bank" (IBPS, SBI, RBI, NABARD, PSBs; private banks from official careers pages); "railway" (RRB/RRC, South Central Railway); "police" (Agniveer, CAPF, state police); "teaching" (DSC, KVS/NVS, universities).
 PRIVATE (about half when good ones exist) — "it" (Hyderabad/TG/AP openings from companies' OWN careers pages or reputable news), "private" (pharma, hospitals, BFSI, BPO, retail, logistics, manufacturing, hotels, sales), "mela" (government job melas, NCS portal, apprenticeships, PM Internship, official walk-ins).
 Job portals (Naukri, TimesJobs, Freshersworld, Foundit, Indeed, Shine, LinkedIn, Apna, Sarkari Result, FreeJobAlert, Employment News…) are LEADS ONLY: add a job only after confirming it on the official page or reputable news, and set apply/url/src to that page, never the portal.
 Safety: never consultancies/agents, "placement guaranteed", any fee or deposit, or posts found only on social media or only on a portal. Every fact from an official or reputable-news page retrieved in this run; never invent numbers or dates. Up to 20 new jobs per run; never pad.

4. WRITE each new job in simple Telugu, own words:
 {"id","type","org","h","p","posts","statl":"పోస్టులు","qual","exp","loc","age","pay","last","walk","how","apply","url","src","place","d","en":{…},"hi":{…}} — same field meanings as existing jobs in jobs.json (last REQUIRED for government jobs; place = TS / AP / IN / a Telangana district key). en/hi: faithful translations of the non-empty text fields (h, p, statl, qual, exp, loc, age, how, walk, and posts only if it is a word). BACKFILL en/hi for up to 40 existing jobs missing them.

5. SAVE: new jobs first, then by last date (soonest first; no-last-date after); max 120. "updated" = now (ISO +05:30). Validate with json.load. Run `CHROME_PATH=$(which google-chrome || true) python3 tools/build_previews.py`. git config user.name "Swipe2News Bot"; git config user.email "news-bot@swipe2news.invalid"; git add jobs.json s cards web; git commit -m "Jobs update YYYY-MM-DD HH:MM IST"; fetch + rebase if needed (jobs.json conflict: take origin/main and re-apply); git push origin HEAD:main; retry once.
 FALLBACK: save jobs.json to /mnt/user-data/outputs/jobs.json and send it with SendUserFile (status "proactive", caption "GitHub save failed – upload this jobs.json to github.com/WAY2SEC/swipe2news").

6. SendUserMessage (short, English with Telugu titles): new jobs (gov / private / mela), portal leads used, expired removed, en/hi added, "App updated: yes/no", and a WhatsApp caption: "💼 Swipe2News జాబ్స్ – DD.MM.YYYY", numbered "<Telugu title> – <posts> పోస్టులు – చివరి తేదీ <last>" (private without last date: location), "⚠️ ఉద్యోగం కోసం ఎవరికీ డబ్బులు ఇవ్వకండి – అధికారిక వెబ్‌సైట్‌లోనే దరఖాస్తు చేయండి", "📲 https://swipe2news.com/?jobs=1", "👉 https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138".

Rules: facts only from retrieved official/reputable pages; portals only as leads; own words; no fee-based offers. In the repo change only jobs.json and what build_previews.py generates. Do not post to WhatsApp or anywhere else, do not send email, do not create or change scheduled tasks. Finish with one line: new jobs (gov/private/mela), expired removed, app updated yes/no.
