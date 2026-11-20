#!/usr/bin/env python3
"""Build the Swipe2News STAGING copy (a separate repo + GitHub Pages site, e.g. https://staging.swipe2news.com).

  python3 tools/staging/make_staging.py --out ../swipe2news-staging --host staging.swipe2news.com [--newsroom URL] [--days 3]

What the copy changes (the live repo is never touched):
  * CNAME = the staging host; robots.txt blocks all search engines; a red "STAGING" ribbon on the app, website and editor
  * reporter/config.js points to the STAGING newsroom (a separate Google Sheet + Apps Script), never the live one
  * only the "Publish manual stories" workflow is kept – no phone alerts, IndexNow, feeds, story-check or Android builds
  * smaller: only the last --days of archive (+ their article pages and share pictures); no e-paper, videos, app files
  * tools/staging/newsroom_staging.gs = the newsroom script with its own photo folder, ready to paste into the staging Sheet
Phone alerts stay off on staging anyway: index.html only turns OneSignal on for swipe2news.com.
"""
import argparse, glob, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from manual_publish import sid  # noqa: E402

SKIP_TOP = {".git", "cards", "s", "epaper", "videos", "app", "android", "screenshots", "archive", ".github", "__pycache__"}
RIBBON = ('<div id="s2n-staging" style="position:fixed;z-index:2147483647;top:0;left:50%;transform:translateX(-50%);'
          'background:#B3261E;color:#fff;font:800 12px/1 system-ui,sans-serif;padding:5px 12px;border-radius:0 0 10px 10px;'
          'letter-spacing:.06em;pointer-events:none">STAGING · పరీక్ష సైట్ · not live</div>')
NOINDEX = '<meta name="robots" content="noindex,nofollow">'


def mark_page(path):
    if not os.path.exists(path):
        return
    t = open(path, encoding="utf-8").read()
    if "s2n-staging" in t:
        return
    t = re.sub(r"(<head[^>]*>)", r"\1" + NOINDEX, t, count=1)
    t = re.sub(r"(<body[^>]*>)", r"\1" + RIBBON, t, count=1)
    open(path, "w", encoding="utf-8").write(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--host", default="staging.swipe2news.com")
    ap.add_argument("--newsroom", default="", help="STAGING newsroom web app URL (never the live one)")
    ap.add_argument("--days", type=int, default=3)
    a = ap.parse_args()
    live = open(os.path.join(ROOT, "reporter", "config.js"), encoding="utf-8").read()
    if a.newsroom and a.newsroom in live:
        sys.exit("refusing: that is the LIVE newsroom URL – staging needs its own Sheet + Apps Script")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):  # keep the staging repo's .git, replace everything else
        if name == ".git":
            continue
        p = os.path.join(out, name)
        shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)

    for name in os.listdir(ROOT):
        if name in SKIP_TOP or name.startswith(".manual-publish"):
            continue
        src, dst = os.path.join(ROOT, name), os.path.join(out, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, dst)

    # archive: last N days only
    os.makedirs(os.path.join(out, "archive"), exist_ok=True)
    idx = json.load(open(os.path.join(ROOT, "archive", "index.json"), encoding="utf-8"))
    keep = idx["dates"][: a.days]
    json.dump({"dates": keep}, open(os.path.join(out, "archive", "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    stories = json.load(open(os.path.join(ROOT, "news.json"), encoding="utf-8")).get("stories", [])
    for d in keep:
        f = os.path.join(ROOT, "archive", d["iso"] + ".json")
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(out, "archive", d["iso"] + ".json"))
            stories += json.load(open(f, encoding="utf-8")).get("stories", [])
    # article pages + share pictures that already exist for those stories (the rest are built by the workflow)
    for sub, ext in (("s", ".html"), ("cards", ".jpg")):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
        for s in stories:
            f = os.path.join(ROOT, sub, sid(s) + ext)
            if os.path.exists(f):
                shutil.copy2(f, os.path.join(out, sub, sid(s) + ext))

    # only the manual publishing workflow
    os.makedirs(os.path.join(out, ".github", "workflows"), exist_ok=True)
    wf = open(os.path.join(ROOT, ".github", "workflows", "publish-manual.yml"), encoding="utf-8").read()
    wf = wf.replace("${{ vars.S2N_ENV || 'staging' }}", "staging").replace("${{ vars.S2N_SITE || 'https://swipe2news.com' }}", "https://" + a.host)
    wf = wf.replace("${{ vars.S2N_NOINDEX }}", "'1'").replace("name: Publish manual stories", "name: Publish manual stories (STAGING)", 1)
    if "S2N_ENV: staging" not in wf or "S2N_NOINDEX: '1'" not in wf:
        sys.exit("could not pin the staging settings in the workflow")
    open(os.path.join(out, ".github", "workflows", "publish-manual.yml"), "w", encoding="utf-8").write(wf)

    open(os.path.join(out, "CNAME"), "w").write(a.host + "\n")
    open(os.path.join(out, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(out, "reporter", "config.js"), "w", encoding="utf-8").write(
        "/* Swipe2News STAGING newsroom (separate Google Sheet + Apps Script – NOT the live one). */\n"
        f"window.W2S_NEWSROOM = '{a.newsroom}';\n")
    for p in ("index.html", "editor/index.html", "reporter/index.html", "tools/web_template.html", "te/index.html", "en/index.html", "hi/index.html", "web/index.html"):
        mark_page(os.path.join(out, p))

    gs = open(os.path.join(ROOT, "tools", "reporter_apps_script.gs"), encoding="utf-8").read()
    gs = gs.replace("const FOLDER     = 'Swipe2News reporter photos';", "const FOLDER     = 'Swipe2News STAGING photos';  // staging: never the live photo folder")
    gs = gs.replace(" * Swipe2News newsroom inbox", " * STAGING COPY – paste into the \"Swipe2News STAGING newsroom\" Sheet only, never the live one.\n * Swipe2News newsroom inbox", 1)
    if "STAGING photos" not in gs:
        sys.exit("could not switch the photo folder for staging")
    os.makedirs(os.path.join(out, "tools", "staging"), exist_ok=True)
    open(os.path.join(out, "tools", "staging", "newsroom_staging.gs"), "w", encoding="utf-8").write(gs)
    open(os.path.join(out, "README.md"), "w", encoding="utf-8").write(
        f"# Swipe2News STAGING\n\nTest copy of swipe2news.com at https://{a.host} – not live, not indexed, no phone alerts.\n"
        "Built from branch `manual-publish` of WAY2SEC/swipe2news with tools/staging/make_staging.py.\n"
        "Publish queued test stories: Actions → **Publish manual stories** → Run workflow.\n")
    print(f"staging copy ready in {out}: {len(keep)} archive days, newsroom {'set' if a.newsroom else 'NOT set yet'}")


if __name__ == "__main__":
    main()
