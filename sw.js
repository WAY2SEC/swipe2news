// Swipe2News service worker: keeps the app working offline (villages, weak signal).
// Pages and news: network first, but fall back to the saved copy after 4 s. Fonts and pictures: saved copy first.
const CACHE = 's2n-v47';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'logo.png', 'logo-light.png', 'qr.png', 'icon-192.png', 'icon-512.png',
  'news.json', 'mandi.json', 'mandi.js?v=2', 'mandi/', 'morning/', 'archive/index.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => 0))))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
const FONT = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;
function fresh(req, ms) {
  return new Promise(resolve => {
    let done = false;
    const fallback = () => caches.match(req, {ignoreSearch: true}).then(c => c || null);
    const t = setTimeout(() => fallback().then(c => { if (c && !done) { done = true; resolve(c); } }), ms);
    fetch(req).then(r => { if (r && r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      clearTimeout(t); if (!done) { done = true; resolve(r); } })
      .catch(() => { clearTimeout(t); fallback().then(c => { if (!done) { done = true; resolve(c || Response.error()); } }); });
  });
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (FONT.test(req.url)) {
    e.respondWith(caches.match(req).then(c => c || fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(x => x.put(req, copy)); return r; })));
    return;
  }
  if (u.origin !== location.origin) return;
  if (/\.(jpg|jpeg|png|webp|svg|woff2?)$/i.test(u.pathname) && !/^\/cards\//.test(u.pathname)) {
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(c => c || fetch(req).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(x => x.put(req, copy)); } return r; })));
    return;
  }
  e.respondWith(fresh(req, req.mode === 'navigate' || /\.json$/.test(u.pathname) ? 4000 : 6000));
});
// the app asks us to save today's pictures and pages for offline reading
self.addEventListener('message', e => {
  const d = e.data || {}; if (d.type !== 'warm' || !Array.isArray(d.urls)) return;
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(d.urls.slice(0, 40).map(u => c.match(u).then(h => h || c.add(u).catch(() => 0))))));
});
