#!/usr/bin/env python3
"""Newsreader voice for Telugu stories (owner 21 Nov 2026: "best voices, very fluent").

After every news update (GitHub Action news-voice.yml) this turns each new Telugu story in news.json into an MP3
with Google Cloud Text-to-Speech (Chirp 3 HD voice) and lists it in audio/index.json ({story id: file}).
The app plays that file when the reader taps Listen; stories without a file use the phone's own voice.

Needs the GitHub secret GOOGLE_TTS_KEY (Google Cloud API key restricted to the Text-to-Speech API).
Files older than KEEP_DAYS are deleted so the website stays small.
Usage: python3 tools/tts.py [--dry] [--max N]
"""
import base64, datetime, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, 'audio')
INDEX = os.path.join(AUD, 'index.json')
VOICE = os.environ.get('S2N_TTS_VOICE', 'te-IN-Chirp3-HD-Charon')  # calm male newsreader; female: te-IN-Chirp3-HD-Kore
KEEP_DAYS = 3
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def sid(s):  # same id as the app's sid()
    h = 5381
    for ch in (s.get('url') or '') + '|' + (s.get('h') or ''):
        c = ord(ch)
        for u in ([c] if c < 0x10000 else [0xD800 + ((c - 0x10000) >> 10), 0xDC00 + ((c - 0x10000) & 0x3FF)]):
            h = ((h << 5) + h + u) & 0xFFFFFFFF
    out, d = '', '0123456789abcdefghijklmnopqrstuvwxyz'
    while True:
        out = d[h % 36] + out; h //= 36
        if not h: return out

def speakable(t):  # same clean-up as the app's speakable() for Telugu
    t = re.sub('[\U0001F300-\U0001FAFF☀-➿️]', ' ', t)
    t = re.sub('[“”"‘’\'«»]', '', t)
    t = re.sub(r'\s*[–—]\s*', ', ', t); t = re.sub(r'\s*:\s*', ', ', t); t = re.sub('[|·•]', ', ', t)
    t = re.sub(r'(\d),(?=\d)', r'\1', t)
    t = re.sub(r'₹\s?([\d.]+)\s?(వేల|వేలు)', r'\1 వేల రూపాయల', t)
    t = re.sub(r'₹\s?([\d.]+)\s?(కోట్ల|కోట్లు)', r'\1 కోట్ల రూపాయల', t)
    t = re.sub(r'₹\s?([\d.]+)\s?(లక్షల|లక్షలు)', r'\1 లక్షల రూపాయల', t)
    t = re.sub(r'₹\s?([\d.]+)', r'\1 రూపాయల', t)
    for a, b in (('కి.మీ.', 'కిలోమీటర్లు'), ('కి.మీ', 'కిలోమీటర్లు'), ('సెం.మీ.', 'సెంటీమీటర్లు'), ('మి.మీ.', 'మిల్లీమీటర్లు')):
        t = t.replace(a, b)
    t = re.sub(r'(\d)\s?%', r'\1 శాతం', t); t = re.sub(r'(\d)°', r'\1 డిగ్రీలు', t)
    return re.sub(r'(\.\s*){2,}', '. ', re.sub(r'\s{2,}', ' ', t)).strip()

def text_of(s):
    parts = [s.get('h'), s.get('p')] + (s.get('pts') if isinstance(s.get('pts'), list) else [])
    return speakable('. '.join(x.strip().rstrip('.') for x in parts if x))

def synth(text, key):
    body = {'input': {'text': text}, 'voice': {'languageCode': 'te-IN', 'name': VOICE},
            'audioConfig': {'audioEncoding': 'MP3', 'speakingRate': 1.0, 'sampleRateHertz': 24000}}
    req = urllib.request.Request('https://texttospeech.googleapis.com/v1/text:synthesize?key=' + key,
                                 data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return base64.b64decode(json.loads(r.read().decode())['audioContent'])

def main():
    dry = '--dry' in sys.argv
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 40
    key = os.environ.get('GOOGLE_TTS_KEY', '').strip()
    os.makedirs(AUD, exist_ok=True)
    try: idx = json.load(open(INDEX, encoding='utf-8'))
    except Exception: idx = {}
    now = datetime.datetime.now(IST)
    stories = [s for s in json.load(open(os.path.join(ROOT, 'news.json'), encoding='utf-8'))['stories'] if not s.get('kind') and s.get('h') and s.get('p')]
    made = chars = 0
    for s in stories[:60]:
        k = sid(s)
        if k in idx and os.path.exists(os.path.join(AUD, idx[k]['f'])):
            continue
        if made >= mx: break
        t = text_of(s)
        if dry or not key:
            print(f'  [{"dry" if dry else "no key"}] {k}: {len(t)} chars – {s["h"]}'); chars += len(t); continue
        try:
            mp3 = synth(t, key)
        except Exception as e:
            print('  FAILED', k, s['h'], e); continue
        f = f'{now.strftime("%Y%m%d")}-{k}.mp3'
        open(os.path.join(AUD, f), 'wb').write(mp3)
        idx[k] = {'f': f, 't': now.isoformat(timespec='minutes')}
        made += 1; chars += len(t)
        print(f'  made {f} ({len(mp3)//1024} KB, {len(t)} chars) – {s["h"]}')
    # keep the website small: drop files older than KEEP_DAYS
    cut = (now - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    for k in [k for k, v in idx.items() if v.get('t', '') < cut]:
        try: os.remove(os.path.join(AUD, idx[k]['f']))
        except Exception: pass
        idx.pop(k)
    if not dry and key:
        json.dump(idx, open(INDEX, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{made} new voice files, {chars} characters' + ('' if key else ' – GOOGLE_TTS_KEY not set, nothing made'))

if __name__ == '__main__':
    main()
