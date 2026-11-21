#!/usr/bin/env python3
"""Swipe2News story checker: catches small mistakes before readers see them.

Usage:
  python3 tools/check_news.py [news.json] [--fix] [--report FILE]

--fix      repairs what is safe to repair automatically (and says what it changed)
--report   also writes a short Markdown report
Exit code 1 when a story still has a blocking problem (ERROR), so the newsroom fixes it before publishing.
"""
import json, re, sys, os
HARD_WORDS = {'పట్టివేత': 'పట్టుకున్నారు', 'స్వాధీనం': 'పట్టుకున్నారు', 'లభ్యం': 'దొరికింది', 'నిలిపివేత': 'ఆపేశారు', 'పునరుద్ధరణ': 'మళ్లీ మొదలు', 'ఉల్లంఘన': 'నిబంధనలు పాటించలేదు', 'తొలగింపునకు': 'తీసేయాలని', 'జననం': 'పుట్టారు', 'ఆచూకీ': 'దొరికింది / కనిపించలేదు', 'నిమిత్తం': 'కోసం', 'పరిశీలన': 'చూశారు / తనిఖీ', 'ప్రారంభోత్సవం': 'ప్రారంభం', 'శంకుస్థాపన': 'పనులకు పునాది', 'వేర్పాటు': 'విడిగా ఉన్న', 'ఉపసంహరణ': 'వెనక్కి తీసుకున్నారు', 'దుర్మరణం': 'మృతి', 'అస్వస్థత': 'అనారోగ్యం', 'ఆకస్మిక': 'హఠాత్తుగా', 'సమీక్షా సమావేశం': 'సమీక్ష'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIC_RX = re.compile(r'^(c|o|i|n|s|cv|w|d)/([a-z0-9-]+)$')
def pic_ok(pc):
    m = PIC_RX.match(pc or '')
    return bool(m) and any(os.path.exists(os.path.join(ROOT, 'art', m.group(1), m.group(2) + e)) for e in ('.webp', '.jpg'))

LATIN_OK = re.compile(r'^(AI|IMD|ISRO|NASA|BJP|BRS|TDP|YSRCP|ANI|PTI|UNI|IANS|ED|CBI|NIA|IPL|ICC|BCCI|UN|US|UK|UAE|GST|EMI|UPI|ATM|SIM|OTP|KYC|PAN|NEET|JEE|EAMCET|TSPSC|APPSC|UPSC|SSC|RTC|TGSRTC|APSRTC|HICC|IT|AP|TG|TS|MLA|MP|CM|PM|SP|DSP|SI|CI|DGP|IAS|IPS|DRDO|ITI|IIT|NIT|AIIMS|COVID|WHO|GDP|RBI|SBI|LIC|TTD|GHMC|HMDA|HMWSSB|SEC|EC|T20|ODI|U19|km|kg|cm)$')
VAGUE_START = re.compile(r'^(సమ్మిట్|సదస్సు|సమావేశం|పథకం|ప్రాజెక్టు|కార్యక్రమం|ఉత్సవం|ఎన్నిక|కేసు|ఘటన|ప్రమాదం)(\s|$|లో|కు|పై|వద్ద)')
DAMAGE = re.compile(r'నష్టం|నష్ట|దెబ్బతిన|ధ్వంసం|కూలిన|మృతి|మృతుల|చనిపో|loss|damage|died|killed')
FORECAST_WORDS = re.compile(r'సూచన|హెచ్చరిక|అవకాశం|అంచనా|forecast|warning|likely|alert')
POLICE_SAID = re.compile(r'పోలీసులు (తెలిపారు|వెల్లడించారు|చెప్పారు)|police said')
ONE_NOUN = re.compile(r'^\s*1\s')

def stories(d):
    return d['stories'] if isinstance(d, dict) else d

def check(d, fix=False):
    errs, warns, fixed = [], [], []
    seen = {}
    for i, s in enumerate(stories(d)):
        if s.get('kind'):
            continue
        h = (s.get('h') or '').strip(); p = (s.get('p') or '').strip()
        tag = f'#{i+1} "{h[:40]}"'
        stat, statl = (s.get('stat') or '').strip(), (s.get('statl') or '').strip()
        # 1) picture heading line
        if not stat and not statl:
            errs.append(f'{tag}: picture heading line is empty – give stat (number or 1–3 word topic) + statl (what happened)')
        elif stat and not statl and re.search(r'\d', stat):
            errs.append(f'{tag}: number "{stat}" has no meaning – add statl')
        if ONE_NOUN.match(stat + ' ' + statl) and re.search(r'మృతి|గాయ', statl):
            warns.append(f'{tag}: "1 …" reads badly – write "ఒకరు మృతి" style Telugu')
        # 1b) picture (owner 18 Nov 2026): every new story names its picture from tools/pictures.md
        pc = s.get('pic')
        if pc and not pic_ok(pc):
            errs.append(f'{tag}: pic "{pc}" is not in tools/pictures.md – pick a real key')
        elif pc and str(s.get('pub') or '') >= '2026-11-21T21' and not re.match(r'^(e|d|w|m)/|^c/devotional$|^n/(africa|asia|europe|mideast|namerica|friendship|pod)$|^i/', pc):
            errs.append(f'{tag}: pic "{pc}" is a generic old key – pick the exact e/ scene for this event (tools/pictures.md, "Exact picture for common stories")')
        elif not pc and str(s.get('pub') or '') >= '2026-11-18T18':
            errs.append(f'{tag}: no "pic" – read the story and choose its picture from tools/pictures.md')
        # 2) headline
        if not h:
            errs.append(f'#{i+1}: headline missing')
        if len(h) > 40:
            warns.append(f'{tag}: headline is {len(h)} characters – may not fit one line (keep ≤ 38)')
        if re.search(r'[:]|అని సంస్థ|అని పోలీసులు|ప్రకారం$', str(s.get('statl') or '')):
            warns.append(f'{tag}: picture line has a tail ("{s.get("statl")}") – write one natural phrase')
        hard = [f'{w} → {e}' for w, e in HARD_WORDS.items() if w in h or w in str(s.get('statl') or '')]
        if hard:
            warns.append(f'{tag}: hard words for readers – say it simply: ' + '; '.join(hard))
        if VAGUE_START.match(h):
            errs.append(f'{tag}: headline does not say WHICH event – name it (e.g. "భారత్ సమ్మిట్ వద్ద…")')
        lat = [w for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]{2,}', h) if not LATIN_OK.match(w)]
        if lat:
            warns.append(f'{tag}: English letters in the Telugu headline: {", ".join(lat)}')
        pl = len((s.get('stat') or '') + (s.get('statl') or ''))
        if pl > 34:
            warns.append(f'{tag}: picture line is long ({pl} letters) – keep stat + statl short so it fits one line')
        # 3) summary
        n = len(p.split())
        if not p:
            errs.append(f'{tag}: summary missing')
        elif n < 32 or n > 48:
            errs.append(f'{tag}: summary is {n} words – the card summary must be about 40 words (36–44) so it fits under the half-size picture; rewrite it, never pad')
        # 4) source
        if not (s.get('src') or '').strip():
            errs.append(f'{tag}: source name missing')
        url = (s.get('url') or '').strip()
        if not re.match(r'^https?://', url) and 'రిపోర్టర్' not in (s.get('src') or '') and 'Swipe2News' not in (s.get('src') or ''):
            errs.append(f'{tag}: source link missing')
        if url:
            if url in seen:
                errs.append(f'{tag}: same story link as #{seen[url]} (duplicate)')
            seen[url] = i + 1
        # 5) labels
        lbl = s.get('lbl')
        text = h + ' ' + statl + ' ' + p[:200]
        if lbl == 'forecast' and DAMAGE.search(h + ' ' + statl) and not FORECAST_WORDS.search(h + ' ' + statl):
            if fix:
                s['lbl'] = 'fact'; fixed.append(f'{tag}: "forecast" label removed – it reports damage that already happened')
            else:
                errs.append(f'{tag}: "forecast" label on a report of damage that already happened')
        if lbl in ('claim', 'allegation') and POLICE_SAID.search(text) and not re.search(r'ఆరోప|allege', h):
            if fix:
                s['lbl'] = 'fact'; fixed.append(f'{tag}: label changed {lbl} → fact (the police reported it)')
            else:
                warns.append(f'{tag}: labelled {lbl}, but the police reported it – police-reported events are facts')
        # 6) translations
        for L in ('en', 'hi'):
            t = s.get(L)
            if not (isinstance(t, dict) and (t.get('h') or '').strip()):
                warns.append(f'{tag}: {L} translation missing'); continue
            for k in ('stat', 'loc'):
                if re.search(r'[\u0C00-\u0C7F]', s.get(k) or '') and not (t.get(k) or '').strip():
                    warns.append(f'{tag}: {L} version has no "{k}" – English/Hindi readers would see Telugu ("{s.get(k)}")')
    return errs, warns, fixed

def pictures_needed(d):
    """Stories whose topic still has no proper picture (tools/art_needed.json) – owner creates them."""
    import os
    try: need = json.load(open('tools/art_needed.json', encoding='utf-8'))
    except Exception: return []
    out = []
    for k, v in need.items():
        if k.startswith('_') or os.path.exists(f'art/n/{k}.jpg'): continue
        hits = [s.get('h','') for s in stories(d) if not s.get('kind') and re.search(v['rx'], (s.get('h') or '') + ' ' + (s.get('p') or ''), re.I)]
        if hits: out.append((k, v, hits))
    return out

KEEP_NEWEST = 60
def trim_feed(d, root):
    """news.json is the file every phone downloads first: keep it small (owner 19 Nov 2026 – it had grown to 582
    stories / 2.5 MB, so on 4G the app timed out and showed yesterday's saved news). Older stories stay in
    archive/<date>.json, which the app loads for today and the date list. A story is removed only if its day's
    archive already has it."""
    L = d['stories'] if isinstance(d, dict) else d
    if len(L) <= KEEP_NEWEST:
        return []
    arch = {}
    def in_archive(s):
        day = str(s.get('pub') or '')[:10]
        if not re.match(r'\d{4}-\d\d-\d\d$', day):
            return False
        if day not in arch:
            try:
                a = json.load(open(os.path.join(root, 'archive', day + '.json'), encoding='utf-8'))
                arch[day] = {x.get('h') for x in (a['stories'] if isinstance(a, dict) else a)}
            except Exception:
                arch[day] = set()
        return s.get('h') in arch[day]
    keep, n = [], 0
    for s in L:
        if s.get('kind'):
            keep.append(s); continue
        n += 1
        if n <= KEEP_NEWEST or not in_archive(s):
            keep.append(s)
    gone = len(L) - len(keep)
    if not gone:
        return []
    if isinstance(d, dict):
        d['stories'] = keep
    else:
        L[:] = keep
    return [f'news.json trimmed to the newest {KEEP_NEWEST} stories ({gone} older ones stay in archive/) so phones load it fast']

def main():
    args = sys.argv[1:]
    fix = '--fix' in args
    rep = args[args.index('--report') + 1] if '--report' in args else None
    files = [a for a in args if a.endswith('.json')] or ['news.json']
    rc = 0
    lines = []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        errs, warns, fixed = check(d, fix)
        if fix and os.path.basename(f) == 'news.json':
            fixed += trim_feed(d, os.path.dirname(os.path.abspath(f)))
        if fix and fixed:
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        n = len([s for s in stories(d) if not s.get('kind')])
        lines.append(f'## {f}: {n} stories · {len(errs)} to fix · {len(warns)} to look at · {len(fixed)} fixed automatically')
        for t, xs in (('FIXED', fixed), ('ERROR', errs), ('CHECK', warns)):
            lines += [f'- {t}: {x}' for x in xs]
        if errs:
            rc = 1
        pn = pictures_needed(d)
        if pn:
            lines.append('\n### Pictures needed (create in your image tool, send to Claude)')
            for k, v, hits in pn:
                lines.append(f'- **{v["title"]}** – {len(hits)} story(ies), e.g. "{hits[0][:50]}". Prompt: {v["prompt"]}')
    out = '\n'.join(lines)
    print(out)
    if rep:
        open(rep, 'w', encoding='utf-8').write('# Swipe2News story check\n\n' + out + '\n')
    sys.exit(rc)

if __name__ == '__main__':
    main()
