#!/usr/bin/env python3
"""Bump the app version after changing index.html, scenes.js, pictures, etc.
Changes the cache name in sw.js AND the same name in OneSignalSDKWorker.js.
Safari (iPhone) only installs a new service worker when OneSignalSDKWorker.js itself changes,
so both files must change together, or iPhones keep old pictures and old code."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
sw = (root / 'sw.js').read_text()
m = re.search(r"s2n-v(\d+)", sw); new = f"s2n-v{int(m.group(1)) + 1}"
(root / 'sw.js').write_text(sw.replace(m.group(0), new, 1))
w = (root / 'OneSignalSDKWorker.js').read_text()
w2 = re.sub(r'importScripts\("sw\.js(\?v=[^"]*)?"\)', f'importScripts("sw.js?v={new}")', w, count=1)
(root / 'OneSignalSDKWorker.js').write_text(w2)
print(new)
