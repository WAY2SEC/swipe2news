#!/usr/bin/env python3
"""Swipe2News story checker: catches small mistakes before readers see them.

Usage:
  python3 tools/check_news.py [news.json] [--fix] [--report FILE]

--fix      repairs what is safe to repair automatically (and says what it changed)
--report   also writes a short Markdown report
Exit code 1 when a story still has a blocking problem (ERROR), so the newsroom fixes it before publishing.
"""
import json, re, sys

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
        # 2) headline
        if not h:
            errs.append(f'#{i+1}: headline missing')
        if len(h) > 40:
            warns.append(f'{tag}: headline is {len(h)} characters – may not fit one line (keep ≤ 38)')
        if VAGUE_START.match(h):
            errs.append(f'{tag}: headline does not say WHICH event – name it (e.g. "భారత్ సమ్మిట్ వద్ద…")')
        lat = [w for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]{2,}', h) if not LATIN_OK.match(w)]
        if lat:
            warns.append(f'{tag}: English letters in the Telugu headline: {", ".join(lat)}')
        # 3) summary
        n = len(p.split())
        if not p:
            errs.append(f'{tag}: summary missing')
        elif n > 75:
            warns.append(f'{tag}: summary is {n} words – aim for about 60')
        elif n < 20:
            warns.append(f'{tag}: summary is only {n} words')
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
                warns.append(f'{tag}: {L} translation missing')
    return errs, warns, fixed

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
        if fix and fixed:
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        n = len([s for s in stories(d) if not s.get('kind')])
        lines.append(f'## {f}: {n} stories · {len(errs)} to fix · {len(warns)} to look at · {len(fixed)} fixed automatically')
        for t, xs in (('FIXED', fixed), ('ERROR', errs), ('CHECK', warns)):
            lines += [f'- {t}: {x}' for x in xs]
        if errs:
            rc = 1
    out = '\n'.join(lines)
    print(out)
    if rep:
        open(rep, 'w', encoding='utf-8').write('# Swipe2News story check\n\n' + out + '\n')
    sys.exit(rc)

if __name__ == '__main__':
    main()
