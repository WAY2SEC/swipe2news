// Swipe2News service worker: keeps the app working offline (villages, weak signal).
// Pages and news: network first, but fall back to the saved copy after 4 s. Fonts and pictures: saved copy first.
const CACHE = 's2n-v2276'; // when this changes, run tools/bump_app.py (or put the same name in OneSignalSDKWorker.js): Safari only updates the worker when OneSignalSDKWorker.js itself changes
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'logo.png', 'logo-light.png', 'qr.png', 'icon-192.png', 'icon-512.png',
  'news.json', 'mandi.json', 'mandi.js?v=2', 'mandi/', 'morning/', 'archive/index.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(new Request(u, {cache: 'reload'})).catch(() => 0))))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== FONTS && k !== ART).map(k => caches.delete(k))))); self.clients.claim(); });
const FONTS = 's2n-fonts', ART = 's2n-art'; // pictures re-check themselves in the background, so they can stay too // kept across app updates, so a new version never re-downloads the fonts
const FONT = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;
function fresh(req, ms) {
  return new Promise(resolve => {
    let done = false;
    const fallback = () => caches.match(req, {ignoreSearch: true}).then(c => c || null);
    const t = setTimeout(() => fallback().then(c => { if (c && !done) { done = true; resolve(c); } }), ms);
    // ask the server every time (cheap 304 if unchanged), never a stale copy from the phone's HTTP cache
    fetch(req.url, {cache: 'no-cache', credentials: 'same-origin'}).then(r => { if (r && r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      clearTimeout(t); if (!done) { done = true; resolve(r); } })
      .catch(() => { clearTimeout(t); fallback().then(c => { if (!done) { done = true; resolve(c || Response.error()); } }); });
  });
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (FONT.test(req.url)) {
    e.respondWith(caches.match(req).then(c => c || fetch(req).then(r => { const copy = r.clone(); caches.open(FONTS).then(x => x.put(req, copy)); return r; })));
    return;
  }
  if (u.origin !== location.origin) return;
  // library pictures (/art/): show the saved copy at once, and quietly check the server for a newer picture (a replaced picture appears from the next view; owner 23 Nov 2026: BRS logo picture stayed old on iPhone)
  if (/^\/art\//.test(u.pathname) && /\.(jpg|jpeg|png|webp|svg)$/i.test(u.pathname)) {
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(c => {
      const net = fetch(req.url, {cache: 'no-cache', credentials: 'same-origin'}).then(r => { if (r && r.ok) { const copy = r.clone(); caches.open(ART).then(x => x.put(req, copy)); } return r; });
      if (c) { e.waitUntil(net.catch(() => 0)); return c; }
      // no saved copy: if the first try fails (weak signal), try once more the normal way before giving up (owner 27 Nov 2026: Android showed no pictures)
      return net.then(r => (r && r.ok) ? r : fetch(req)).catch(() => fetch(req));
    }));
    return;
  }
  if (/\.(jpg|jpeg|png|webp|svg|woff2?)$/i.test(u.pathname) && !/^\/cards\//.test(u.pathname)) {
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(c => c || fetch(req).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(x => x.put(req, copy)); } return r; })));
    return;
  }
  // The app itself (home page + its scripts): open instantly from the saved copy and refresh it quietly.
  // New versions still arrive: every release changes this file, the new worker saves the new app and the page reloads once.
  if ((req.mode === 'navigate' && (u.pathname === '/' || u.pathname === '/index.html')) || /\.js$/.test(u.pathname)) {
    const key = req.mode === 'navigate' ? './' : req;
    e.respondWith(caches.match(key, {ignoreSearch: req.mode === 'navigate'}).then(c => {
      const net = fetch(req.mode === 'navigate' ? './' : req.url, {cache: 'no-cache', credentials: 'same-origin'})
        .then(r => { if (r && r.ok) { const copy = r.clone(); return caches.open(CACHE).then(x => x.put(key, copy)).then(() => r); } return r; });
      if (c) { e.waitUntil(net.catch(() => 0)); return c; }
      return net.catch(() => fresh(req, 4000));
    }));
    return;
  }
  e.respondWith(fresh(req, req.mode === 'navigate' || /\.json$/.test(u.pathname) ? 4000 : 6000));
});
// the app asks us to save today's pictures and pages for offline reading
self.addEventListener('message', e => {
  const d = e.data || {}; if (d.type !== 'warm' || !Array.isArray(d.urls)) return;
  const port = e.ports && e.ports[0];
  e.waitUntil(caches.open(CACHE).then(async c => { let saved = 0; const list = d.urls.slice(0, 45);
    for (let i = 0; i < list.length; i += 2) { // two at a time (owner 21 Nov 2026: the reader's own card pictures must always come first)
      await Promise.all(list.slice(i, i + 2).map(u => c.match(u, {ignoreSearch: true}).then(h => h ? saved++ : c.add(u).then(() => saved++).catch(() => 0)))); }
    if (port) port.postMessage({saved, total: list.length}); }));
});
