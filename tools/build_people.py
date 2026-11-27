"""Who's who for Swipe2News: MLAs, MLCs, MPs, ministers (TG/AP) and Union ministers.
Source: owner's research list tools/people-src/ (16 Nov 2026, names/roles only – NOT cleared photos).
Writes tools/people.json and tools/photos-needed.md (people in recent news who have no photo yet, most mentioned first).
Run: python3 tools/build_people.py"""
import csv, json, glob, os, re, collections
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
rd = lambda f: list(csv.DictReader(open(os.path.join(H, 'people-src', f), encoding='utf-8-sig')))
roster, roles = rd('roster.csv'), rd('roles.csv')
P = {}
for r in roster:
    if 'TERM EXPIRED' in (r.get('rosterStatus') or '') or not r['name'].strip(): continue
    k = r['name'].strip()
    P.setdefault(k, {'name': k, 'state': r['state'], 'roles': [], 'party': r['party'], 'seat': r['constituency']})
    P[k]['roles'].append((r['house'] + ' ' + (r['office'] or '')).strip())
for r in roles:
    k = r['name'].strip(); P.setdefault(k, {'name': k, 'state': r['state'], 'roles': [], 'party': r['party'], 'seat': r['constituency']})
    P[k]['roles'].insert(0, r['office'] + (': ' + r['portfolio'] if r['portfolio'] else ''))
PHOTO = {'revanth-reddy': r'Revanth', 'bhatti-vikramarka': r'Bhatti', 'uttam-kumar-reddy': r'Uttam Kumar', 'komatireddy-venkat': r'Komati ?Reddy Venkat', 'sridhar-babu': r'Sridhar Babu',
 'ponguleti': r'Ponguleti', 'ponnam-prabhakar': r'Ponnam', 'seethakka': r'Seethakka', 'konda-surekha': r'Konda Surekha', 'kcr': r'Chandrashekar Rao', 'ktr': r'Taraka Rama Rao', 'harish-rao': r'Harish Rao',
 'kavitha': r'Kalvakuntla Kavitha', 'etela-rajender': r'(Eatala|Etela) Rajender', 'owaisi': r'Asaduddin', 'bandi-sanjay': r'Bandi Sanjay', 'kishan-reddy': r'^G\.? Kishan Reddy', 'dharmapuri-arvind': r'Dharmapuri Arvind',
 'chandrababu-naidu': r'Chandrababu', 'pawan-kalyan': r'Pawan Kalyan', 'nara-lokesh': r'Nara Lokesh', 'ys-jagan': r'Jagan Mohan', 'balakrishna': r'Balakrishna', 'modi': r'Narendra Modi',
 'amit-shah': r'Amit Shah', 'jaishankar': r'Jaishankar', 'rahul-gandhi': r'^Rahul Gandhi'}
# photos we already have (art/e/photo-*.jpg) – matched by surname/name words
have = [os.path.basename(f)[6:-4] for f in glob.glob(os.path.join(R, 'art/e/photo-*.jpg'))]
COMMON = set('reddy rao naidu kumar yadav singh raju prasad krishna rama srinivas gandhi mohan murali bharat ram swamy babu devi sri venkat venkata ramesh prabhakar sanjay dr ch srinivasa nageswara sambasiva mahesh goud kiran mahender prakash narayan'.split())
def alias(n):
    t = [x for x in re.split(r'[\s.]+', n) if x]
    a = {n} if len([x for x in t if len(x) > 1]) >= 2 else set()
    t = [x for x in t if len(x) > 1]
    for k in (3, 2):  # last words, only when they are not all common words ("Rama Krishna" would match many people)
        if len(t) > k and not all(w.lower() in COMMON for w in t[-k:]): a.add(' '.join(t[-k:]))
    return sorted(a, key=len, reverse=True)
norm = lambda n: re.sub(r'[^a-z]', '', n.lower().replace('konidala', 'konidela').replace('komati reddy', 'komatireddy'))
M = {}
for p in list(P.values()):
    k = norm(p['name'])
    if k in M: M[k]['roles'] = list(dict.fromkeys(M[k]['roles'] + p['roles']))
    else: M[k] = p
P = {p['name']: p for p in M.values()}
for p in P.values():
    p['aka'] = alias(p['name'])
    p['photo'] = next((h for h, rx in PHOTO.items() if re.search(rx, p['name'], re.I)), '')
json.dump(sorted(P.values(), key=lambda x: x['name']), open(os.path.join(H, 'people.json'), 'w'), ensure_ascii=False, indent=1)
# who appears in recent news (English text of the stories)
texts = []
for f in [os.path.join(R, 'news.json')] + sorted(glob.glob(os.path.join(R, 'archive/2026-*.json')))[-21:]:
    try: d = json.load(open(f))
    except Exception: continue
    for s in (d.get('stories', []) if isinstance(d, dict) else d):
        e = s.get('en') or {}; texts.append(' '.join([e.get('h', ''), e.get('p', '')]))
blob = '\n'.join(texts); cnt = collections.Counter()
for p in P.values():
    for a in p['aka']:
        if len(a) < 5: continue
        n = len(re.findall(r'\b' + re.escape(a) + r'\b', blob))
        if n: cnt[p['name']] = max(cnt[p['name']], n)
out = ['# Photos needed (from the last 3 weeks of news)', '', 'Most-mentioned people first. ✅ = photo already in the app.', '']
for n, c in cnt.most_common(80):
    p = P[n]; out.append(f"- {'✅' if p['photo'] else '⬜'} **{n}** – {p['roles'][0] if p['roles'] else ''} ({p['state']}, {p['party']}) · {c} stories")
open(os.path.join(H, 'photos-needed.md'), 'w').write('\n'.join(out) + '\n')
print(len(P), 'people ·', sum(1 for p in P.values() if p['photo']), 'with photo ·', len(cnt), 'in recent news')
