"""Rythu Swipe feed (farm.json) for farmers.html – owner, 27 Nov 2026.
Only verified, dated items: farm stories already published in Swipe2News (with their source and link) from the last 7 days.
District rule: a story is shown for a district only when its place is that district, or the whole state that district is in
(TS = all Telangana, AP = all Andhra Pradesh). India-wide and other-state stories are never shown as district updates.
Weather cards are made in the page from weather.json (IMD). Nothing is invented here: no sample text, prices or weather."""
import json, glob, os, re, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FARM = re.compile(r'రైతు|పంట|వరి|ధాన్య|పత్తి|మొక్కజొన్న|కంది|పసుపు|మిరప|కొనుగోలు\s?కేంద్ర|ఎరువు|యూరియా|విత్తన|వ్యవసాయ|మద్దతు\s?ధర|సోయా|శనగ|వేరుశనగ|మార్కెట్\s?యార్డ్|ఐకేపీ|పీఏసీఎస్|రైతు\s?భరోసా|ఉద్యాన|పశువుల|పాడి|ఆక్వా|\bCCI\b|\bMSP\b')
# headline words that only appear in farm news (Telugu has no word breaks: 'వరి' is inside 'జనవరి', 'ధర' inside 'ధర్నా', so those are not used)
STRONG = re.compile(r'రైతు|ధాన్యం|వడ్ల\s?(?:కొనుగోలు|బస్తా|వేలం)|వడ్లు|కొనుగోలు\s?కేంద్ర|యాసంగి|ఖరీఫ్|పత్తి|మిరప|పసుపు|మొక్కజొన్న|ఎరువు|యూరియా|విత్తనాలు|పంట\s?(?:నష్ట|బీమా|రుణ|కొనుగోలు|సర్వే)|మద్దతు\s?ధర|వ్యవసాయ\s?శాఖ|\bMSP\b|\bCCI\b')
NOT = re.compile(r'హత్య|ఆత్మహత్య|మృతి|మరణ|అరెస్ట్|విమర్శ|ఆరోపణ|ఆగ్రహం|దొంగ|నిప్పు|దాడి|ధర్నా|నిరసన|వినతి|డిమాండ్|కరపత్రం|రిలయన్స్|విద్యుత్|రైల్వే|murder|suicide|arrest')  # also no political blame stories   # no sad stories in the farm swipe
CAT = [('procure', r'కొనుగోలు|ఐకేపీ|పీఏసీఎస్|\bCCI\b|ధాన్యం|procure'), ('price', r'ధర|మద్దతు|\bMSP\b|మార్కెట్|price'),
       ('input', r'ఎరువు|యూరియా|విత్తన|fertili|seed'), ('scheme', r'రైతు\s?భరోసా|బీమా|రుణ|పథకం|సబ్సిడీ|scheme|loan|insurance'),
       ('alert', r'హెచ్చరిక|తుఫాను|వర్ష|పురుగు|తెగులు|alert|pest|cyclone'), ('crop', r'.')]
CAT[1] = ('price', r'ధరలు|ధర\s|మద్దతు\s?ధర|\bMSP\b|క్వింటా|price')
CROP = [('paddy', r'(?:^|\s)వరి|ధాన్య|వడ్ల\s|వడ్లు|paddy'), ('cotton', r'పత్తి|cotton'), ('maize', r'మొక్కజొన్న|maize'), ('turmeric', r'పసుపు|turmeric'),
        ('chilli', r'మిరప|chilli'), ('redgram', r'(?:^|\s)కంది(?!కొండ)|red\s?gram'), ('groundnut', r'వేరుశనగ|groundnut'), ('soybean', r'సోయా|soy')]
def sid(s):
    h = 5381
    for ch in (s.get('url') or '') + '|' + (s.get('h') or ''): h = ((h << 5) + h + ord(ch)) & 0xFFFFFFFF
    n, o = h, ''
    while True:
        n, r = divmod(n, 36); o = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + o
        if not n: break
    return o
def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    files = [os.path.join(R, 'news.json')] + [os.path.join(R, 'archive', (now - datetime.timedelta(days=k)).strftime('%Y-%m-%d') + '.json') for k in range(7)]
    seen, out = set(), []
    for f in files:
        try: L = json.load(open(f, encoding='utf-8')); L = L.get('stories', L) if isinstance(L, dict) else L
        except Exception: continue
        for s in L:
            if s.get('kind') or not s.get('url') or not s.get('src'): continue
            t = ' '.join([s.get('h', ''), s.get('statl', '')])
            sec = (s.get('cat') or '').split('·')[-1].strip()
            farmy = (sec in ('వ్యవసాయం', 'రైతులు') or s.get('art') == 'farm') and STRONG.search(t + ' ' + s.get('p', '')[:160]) or STRONG.search(s.get('h', ''))
            if not farmy or NOT.search(t + ' ' + s.get('p', '')): continue
            place = s.get('place') or ''
            if place in ('', 'IN') or (s.get('st') not in (None, '', 'TG', 'AP')): continue
            k = sid(s)
            if k in seen: continue
            seen.add(k); full = t + ' ' + s.get('p', '')
            cat = next(c for c, rx in CAT if re.search(rx, full, re.I)); crop = next((c for c, rx in CROP if re.search(rx, full, re.I)), '')
            e = s.get('en') or {}
            out.append({'id': k, 'place': place, 'st': 'AP' if place == 'AP' or place.startswith('ap-') else 'TG', 'cat': cat, 'crop': crop,
                        'te': {'h': s.get('h', ''), 'p': s.get('p', ''), 'why': s.get('why', '')}, 'en': {'h': e.get('h', ''), 'p': e.get('p', ''), 'why': e.get('why', '')},
                        'pub': s.get('pub') or '', 'd': s.get('d', ''), 'src': s.get('src', ''), 'url': s.get('url', ''), 'img': s.get('img', ''), 'link': f'/s/{k}.html'})
    out.sort(key=lambda x: x['pub'], reverse=True)
    json.dump({'updated': now.isoformat(timespec='minutes'), 'about': 'Farm stories published in Swipe2News in the last 7 days, by district. Built by tools/farm_feed.py.', 'items': out[:300]},
              open(os.path.join(R, 'farm.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(len(out), 'farm items')
if __name__ == '__main__': main()
