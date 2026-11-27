#!/usr/bin/env python3
"""Proposed checker for knowledge.json (Learn Today). Read-only: prints problems, exits 1 if any.
Usage: python3 tools/check_knowledge.py knowledge.json [--today YYYY-MM-DD]"""
import json, re, sys, datetime, difflib

CATS = {"finance", "science_tech", "ai", "health", "agriculture", "constitution", "schemes", "career",
        "english", "history_geo", "cyber", "banking_insurance", "business", "environment", "life_skills",
        "parenting_education", "tg_ap", "global"}
STATUS = {"draft", "review", "approved", "retired"}
EX_KIND = {"hypothetical", "real", "everyday"}
ITYPES = {"inflation", "interest", "savings", "percent", "electricity", "unit", "diagram", "map", "compare"}
ADVICE = {None, "finance", "health", "legal"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^lt-[a-z0-9-]{3,60}$")
LANG_FIELDS = ("h", "p", "ex_kind", "ex", "key", "do", "alt")

def words(s):
    return len(re.findall(r"\S+", s))

def check(doc, today):
    errs, warns = [], []
    L = doc.get("lessons")
    if doc.get("version") != 1 or not isinstance(L, list):
        return ["top level: need version 1 and a lessons list"], warns
    ids, topics, heads = set(), {}, []
    for i, x in enumerate(L):
        w = f"lessons[{i}] {x.get('id', '?')}"
        def need(c, msg):
            if not c: errs.append(f"{w}: {msg}")
        need(ID.match(str(x.get("id", ""))), "id must look like lt-some-slug")
        need(x.get("id") not in ids, "duplicate id"); ids.add(x.get("id"))
        t = x.get("topic")
        need(bool(t), "topic missing")
        if t in topics and topics[t] != "retired" and x.get("status") != "retired":
            errs.append(f"{w}: duplicate topic '{t}' (pick a new angle or retire the old lesson)")
        topics[t] = x.get("status")
        need(x.get("cat") in CATS, f"cat must be one of the 18 categories, got {x.get('cat')!r}")
        need(x.get("status") in STATUS, "bad status")
        for k in ("pub", "verified", "review_by"):
            need(DATE.match(str(x.get(k, ""))), f"{k} must be YYYY-MM-DD")
        if DATE.match(str(x.get("verified", ""))) and DATE.match(str(x.get("review_by", ""))):
            need(x["verified"] <= today, "verified date is in the future")
            need(x["review_by"] > x["verified"], "review_by must be after verified")
            if x["review_by"] < today and x.get("status") == "approved":
                warns.append(f"{w}: review overdue since {x['review_by']} – hide until re-checked")
        if x.get("status") == "approved":
            need(x.get("approved_by") and x.get("approved_at"), "approved lessons need approved_by + approved_at")
        need(isinstance(x.get("read_sec"), int) and 20 <= x["read_sec"] <= 90, "read_sec 20–90")
        need(x.get("advice") in ADVICE, "advice must be null, finance, health or legal")
        img = x.get("img") or {}
        need(img.get("type") in {"library", "photo", "ai", "diagram"}, "img.type")
        need(bool(img.get("pic") or img.get("url")), "img.pic or img.url")
        if img.get("type") == "ai": need(img.get("ai") is True, "AI pictures must set ai: true (shows the label)")
        for lang in ("te", "en"):
            b = x.get(lang) or {}
            for f in LANG_FIELDS:
                need(bool(b.get(f)), f"{lang}.{f} missing")
            need(b.get("ex_kind") in EX_KIND, f"{lang}.ex_kind must be hypothetical / real / everyday")
            n = words(b.get("p", ""))
            lo, hi = (40, 60) if lang == "en" else (28, 60)  # Telugu packs more meaning per word
            if not lo <= n <= hi: errs.append(f"{w}: {lang}.p has {n} words (want {lo}–{hi})")
            if len(b.get("h", "")) > 70: warns.append(f"{w}: {lang}.h longer than 70 characters")
            if lang == "en" and not b.get("h", "").endswith("?"): warns.append(f"{w}: headline is not a question")
        if lang_te := x.get("te"):
            need(not re.search(r"[A-Za-z]{12,}", lang_te.get("p", "")) or "gov.in" in lang_te.get("p", ""), "te.p has a long English word – check translation")
        need((x.get("te") or {}).get("ex_kind") == (x.get("en") or {}).get("ex_kind"), "te/en ex_kind differ")
        src = x.get("sources") or []
        need(len(src) >= 1, "at least one source")
        need(any(s.get("primary") for s in src), "at least one primary (official) source")
        for s in src:
            need(str(s.get("url", "")).startswith("https://"), f"source url must be https: {s.get('url')}")
            need(DATE.match(str(s.get("checked", ""))), "source.checked date")
            need(bool(s.get("name")), "source.name")
        q = x.get("quiz")
        if q:
            te, en = q.get("te") or {}, q.get("en") or {}
            need(len(te.get("opts", [])) == len(en.get("opts", [])) >= 2, "quiz te/en need the same number of options (2+)")
            need(isinstance(q.get("answer"), int) and 0 <= q["answer"] < len(en.get("opts", [])), "quiz.answer index out of range")
            need(te.get("q") and en.get("q") and te.get("why") and en.get("why"), "quiz needs q and why in te + en")
        it = x.get("interactive")
        if it:
            need(it.get("type") in ITYPES, "interactive.type")
            need(isinstance(it.get("hypothetical"), bool), "interactive.hypothetical must be true/false")
        for r in x.get("related", []):
            pass  # checked below
        heads.append((x.get("id"), (x.get("en") or {}).get("h", "").lower()))
    for x in L:
        for r in x.get("related", []):
            if r not in ids: errs.append(f"{x.get('id')}: related id {r} not found")
    for a in range(len(heads)):
        for b in range(a + 1, len(heads)):
            r = difflib.SequenceMatcher(None, heads[a][1], heads[b][1]).ratio()
            if r > 0.8: errs.append(f"near-duplicate headlines: {heads[a][0]} / {heads[b][0]} ({r:.2f})")
    return errs, warns

if __name__ == "__main__":
    path = sys.argv[1]
    today = sys.argv[sys.argv.index("--today") + 1] if "--today" in sys.argv else datetime.date.today().isoformat()
    doc = json.load(open(path, encoding="utf-8"))
    errs, warns = check(doc, today)
    for m in warns: print("WARN ", m)
    for m in errs: print("ERROR", m)
    shown = [x["id"] for x in doc["lessons"] if x.get("status") == "approved" and x.get("pub", "9") <= today and x.get("review_by", "0") >= today]
    print(f"{len(doc['lessons'])} lessons · {len(errs)} errors · {len(warns)} warnings · public today: {len(shown)}")
    sys.exit(1 if errs else 0)
