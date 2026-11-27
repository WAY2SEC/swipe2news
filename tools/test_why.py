#!/usr/bin/env python3
"""Tests for the "why this matters" approval checks.  Run: python3 tools/test_why.py"""
import copy, datetime as dt, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import why_check as W

NOW = dt.datetime(2026, 11, 27, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30)))
BASE = {
    'h': 'శబరిమలకు 14 ప్రత్యేక రైళ్లు', 'url': 'https://telugu.newsmeter.in/x', 'pub': '2026-11-27T11:51+05:30',
    'p': 'దక్షిణ మధ్య రైల్వే 14 ప్రత్యేక రైళ్లను ప్రకటించింది. డిసెంబర్ 4 నుంచి నడుస్తాయి.', 'pts': [],
    'why': 'శబరిమల వెళ్లే తెలంగాణ అయ్యప్ప భక్తులకు ప్రయాణం సులువవుతుంది.',
    'en': {'h': '14 special trains', 'p': 'SCR announced 14 special trains from December 4.', 'why': 'It eases travel for Ayyappa devotees from Telangana.'},
    'hi': {'h': '14 ट्रेनें', 'p': 'दक्षिण मध्य रेलवे ने 14 ट्रेनें घोषित कीं।', 'why': 'तेलंगाना के अयप्पा भक्तों की यात्रा आसान होगी।'},
}


def ok_story(**over):
    s = copy.deepcopy(BASE)
    s['whyr'] = {'ok': True, 'at': '2026-11-27T11:58+05:30', 'src': ['https://scr.indianrailways.gov.in/view'], 'by': 'ED1'}
    for k, v in over.items():
        s[k] = v
    s['whyr']['hash'] = W.why_hash(s)
    return s


def bad(s):
    return W.problems(s, now=NOW)


CASES = []
def case(name, s, expect_ok):
    CASES.append((name, s, expect_ok))

case('valid approval', ok_story(), True)
case('no whyr at all (old story)', copy.deepcopy(BASE), True)
case('old story without why or en', {'h': 'x', 'p': 'y'}, True)
s = ok_story(); s['whyr']['ok'] = False; case('ok false', s, False)
s = ok_story(); s['whyr'] = 'yes'; case('whyr wrong type', s, False)
s = ok_story(); s['whyr']['at'] = 'tomorrow'; case('bad date', s, False)
s = ok_story(); s['whyr']['at'] = '2026-11-28T10:00+05:30'; case('future date', s, False)
s = ok_story(); s['whyr']['at'] = '2026-11-26T10:00+05:30'; case('approved before publish', s, False)
s = ok_story(); s['why'] = s['why'].replace('సులువవుతుంది', 'సులభం అవుతుంది'); case('text edited after approval', s, False)
s = ok_story(); s['whyr']['src'] = []; case('no sources', s, False)
s = ok_story(); s['whyr']['src'] = ['javascript:alert(1)']; s['whyr']['hash'] = W.why_hash(s); case('javascript source', s, False)
s = ok_story(); s['whyr']['src'] = ['http://scr.indianrailways.gov.in/x']; case('http source', s, False)
s = ok_story(); s['whyr']['src'] = ['https://bit.ly/abc']; case('short link source', s, False)
s = ok_story(); s['whyr']['src'] = ['https://10.0.0.1/a']; case('IP source', s, False)
s = ok_story(); s['whyr']['src'] = ['https://randomblog.example.com/a']; case('untrusted only source', s, False)
s = ok_story(); s['whyr']['src'] = ['https://telugu.newsmeter.in/x']; case("story's own source", s, True)
s = ok_story(); s['whyr']['by'] = 'Ravi Kumar 9876543210'; case('editor name instead of code', s, False)
case('three sentences', ok_story(why='ఒకటి. రెండు. మూడు.'), False)
case('two sentences', ok_story(why='ప్రయాణం సులువు. భక్తులకు మేలు.'), True)
case('too long Telugu', ok_story(why='భక్తులకు ' * 30), False)
case('number not in story', ok_story(why='500 మంది భక్తులకు ప్రయాణం సులువవుతుంది.'), False)
case('number in story', ok_story(why='14 రైళ్లతో భక్తులకు ప్రయాణం సులువవుతుంది.'), True)
case('deadline claim not in story', ok_story(why='దరఖాస్తుకు గడువు దగ్గర పడింది.'), False)
case('rupee claim', ok_story(why='ప్రతి కుటుంబానికి ₹ లాభం.'), False)
case('markup in text', ok_story(why='<b>ముఖ్యం</b>'), False)
e = copy.deepcopy(BASE['en']); e['why'] = 'You are eligible for free tickets.'
case('eligibility claim in English', ok_story(en=e), False)
e = copy.deepcopy(BASE['en']); del e['why']
case('English line missing', ok_story(en=e), False)
h = copy.deepcopy(BASE['hi']); del h['why']
case('Hindi line missing is allowed (hidden for Hindi readers)', ok_story(hi=h), True)

fails = 0
for name, s, want in CASES:
    got = not bad(s)
    if got != want:
        fails += 1
        print(f'FAIL {name}: expected {"valid" if want else "invalid"}, problems={bad(s)}')
print(f'{len(CASES) - fails}/{len(CASES)} approval cases pass')

# djb2 must give exactly what the app computes in the browser (same code as sid() in index.html)
JS = ("const t=process.argv[1];let h=5381;for(let i=0;i<t.length;i++)h=((h<<5)+h+t.charCodeAt(i))|0;"
      "process.stdout.write((h>>>0).toString(36))")
for t in ('abc', W.texts(BASE)['te'] + '\n' + W.texts(BASE)['en'] + '\n' + W.texts(BASE)['hi'], '😀 emoji'):
    try:
        js = subprocess.run(['node', '-e', JS, t], capture_output=True, text=True, timeout=20).stdout
    except FileNotFoundError:
        print('node not installed – skipped the app hash cross-check'); break
    if js != W.djb2(t):
        fails += 1; print(f'FAIL hash differs from the app for {t[:20]!r}: py {W.djb2(t)} js {js}')
else:
    print('hash matches the app (Telugu, Hindi, emoji)')
# check_news.py --fix strips a bad approval and keeps a good one, without blocking
with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, 'feed.json')
    good, broken = ok_story(), ok_story(); broken['whyr']['ok'] = False
    good['url'] = 'https://telugu.newsmeter.in/good'; good['whyr']['src'] = ['https://scr.indianrailways.gov.in/v']; good['whyr']['hash'] = W.why_hash(good)
    json.dump({'date': 'x', 'stories': [good, broken], 'flags': {'why2': False}}, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'check_news.py'), f, '--fix'], capture_output=True, text=True)
    out = json.load(open(f, encoding='utf-8'))
    if 'whyr' not in out['stories'][0] or 'whyr' in out['stories'][1] or out['flags'] != {'why2': False}:
        fails += 1; print('FAIL check_news --fix did not keep the good approval / strip the bad one')
    else:
        print('check_news --fix: good approval kept, bad one removed, flags kept')
sys.exit(1 if fails else 0)
