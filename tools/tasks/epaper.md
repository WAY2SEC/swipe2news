# Swipe2News — morning e-paper "జనధ్వని" (scheduled task, 05:06 IST, publish by 05:30)

Daily Telugu e-paper PDF + web viewer for https://swipe2news.com (repo WAY2SEC/swipe2news). ISSUE DATE = today (IST); NEWS DATE = yesterday (IST). Unattended run: don't ask questions.

1. GET THE REPO: mcp__claude-code-remote__add_repo owner "WAY2SEC", repo "swipe2news", access "push"; `git clone --depth 1 https://github.com/WAY2SEC/swipe2news /home/claude/swipe2news`. Read archive/<NEWS DATE>.json and jobs.json. If the archive file is missing or has fewer than 5 stories, stop with one line saying so.

2. PROOFREAD Telugu spelling only (h, p, pts, why, cat, statl of yesterday's stories): fix clear spelling/typing/ottulu/gunintam/spacing/punctuation mistakes — never facts, numbers, names or meaning. Same fixes in archive/<NEWS DATE>.json and, if still present, news.json (match by url + headline). Validate with json.load.

3. HIGHLIGHTS & UPCOMING → epaper/<ISSUE DATE>.extra.json = {"highlights":[8 exact "h" strings of yesterday's most important stories, a BREAKING one first], "upcoming":[5–8 {"when":"5 నవంబర్ (గురువారం)","what","where","src"} for today and the coming days, sorted, from the stories or pages retrieved in this run (IMD forecast, exam/notification dates, matches, government events, holidays); check weekdays; never invent]}. Validate.

4. BUILD: `python3 tools/epaper.py <NEWS DATE> <ISSUE DATE>` then `CHROME_PATH=$(which google-chrome || true) python3 tools/build_previews.py`. Look at epaper/<ISSUE DATE>/p1.jpg and p2.jpg with Read; report anything clearly broken (do not edit tools/).

5. SAVE: git config user.name "Swipe2News Bot"; git config user.email "news-bot@swipe2news.invalid"; git add epaper archive news.json s cards web; git commit -m "E-paper <ISSUE DATE>"; fetch + rebase if needed; git push origin HEAD:main; retry once.

6. SendUserMessage: "📰 ఈ-పేపర్ ready – DD.MM.YYYY", pages and stories, spelling fixes (up to 5 old → new), top 3 highlights, upcoming count, "Published: yes/no", and a WhatsApp caption: "📰 Swipe2News ఈ-పేపర్ – DD.MM.YYYY", "☀️ శుభోదయం! నిన్నటి ముఖ్య వార్తలు, ఈరోజు ముఖ్య ఘట్టాలు", 3 top headlines, "📖 చదవండి: https://swipe2news.com/epaper/?d=<ISSUE DATE>", "👉 https://whatsapp.com/channel/0029Vb9nNd8CBtxIYFryH138". Also send the PDF with SendUserFile (status "proactive").

Rules: facts only from the stories or pages retrieved in this run; own words; in the repo change only epaper/, archive/<NEWS DATE>.json, news.json and what build_previews.py generates. Do not post anywhere, do not send email, do not create or change scheduled tasks. Finish with one line: pages, stories, spelling fixes, published yes/no.
