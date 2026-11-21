# RSS → editor queue → approved-only test feed (staging demo, 21 Nov 2026)

No AI in this path. Branch `rss-queue`; nothing here touches `main`, swipe2news.com, the `feeds` branch, the live Sheet or phone alerts.

| Step | Result |
|---|---|
| Live RSS (GitHub Actions, `rss-staging.yml`): The Hindu TG + AP, Telangana Today, read twice 90 s apart | 3/3 feeds OK both times; 20 newest candidates each; raw feeds saved in `staging/rss-live/` |
| Collector run 1 → queue | 20 new |
| Same run again | 0 new, 20 already queued |
| Second live fetch → queue | 0 new, 20 already queued |
| Same article, other link form (http, www, utm, trailing slash, `#comments`) and a different feed guid | 0 new, 1 duplicate (canonical URL match) |
| Editor approves without opening the source | refused (browser and server) |
| Old "✅ publish" button / BOT key on an RSS row | refused (`use rssapprove` / `not allowed`) |
| RSS rows in the AI tasks' list (`reviewapproved`) | none |
| Card with a picture the checker doesn't allow | not published (check_news.py error) |
| Edit after approval | approval withdrawn (status draft, hash cleared) |
| Publish: 1 approved (KRMB), 1 saved draft (Seethakka) | approved card in feed once; draft absent |
| Retry; retry after a lost "mark published" | no duplicate |
| Approved text changed in the Sheet after approval | refused (hash mismatch) |
| Publisher pointed at live `news.json` | refused, exit 1 |
| Rollback | test feed byte-identical to the pre-publish version (sha256 2f1c4a762eed) |
| Live app (`index.html`) reading the test feed | shows the approved card, not the draft |
| Network hosts used by the demo's Python | 127.0.0.1 only (the queue); the browser only tried Google Fonts and the source article |

The queue was the real `tools/reporter_apps_script.gs` running in `tools/staging/newsroom_emulator.js`, an in-memory Sheet. No staging Google Sheet exists yet.
The Telugu test cards were typed in the editor form, standing in for a human editor; nothing generated them.
