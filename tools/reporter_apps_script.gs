/**
 * Swipe2News newsroom inbox (Google Apps Script, bound to the "Swipe2News Reporters" Google Sheet).
 * Reporters send news from https://swipe2news.com/reporter/ ; the editor approves at https://swipe2news.com/editor/ ;
 * the Swipe2News publishing task collects approved stories and puts them live.
 *
 * Applications from https://swipe2news.com/reporter/join.html land in the "Applications" sheet; to accept someone, give them a PIN in "Reporters".
 * SETUP: Extensions → Apps Script → paste this file → set the two keys below → Run "setup" once → Deploy → New deployment
 *        → type "Web app" → Execute as: Me → Who has access: Anyone → Deploy → copy the Web app URL.
 * Keep EDITOR_KEY and BOT_KEY secret (do not put them on the website).
 */
const EDITOR_KEY = 'PUT-EDITOR-KEY-HERE';   // typed once on the editor page
const BOT_KEY    = 'PUT-BOT-KEY-HERE';      // used only by the Swipe2News publishing task
const FOLDER     = 'Swipe2News reporter photos';
// AUTO_APPROVE (user, 10 Nov 2026): reporter stories from active PINs go live automatically at the next :20 run –
// no editor click needed. The publishing task still screens each story; a risky one (crime allegation naming someone,
// death, communal tension, child, graphic photo…) stays "pending" with a 🤖 note for the editor. The editor can still
// ❌ reject a pending story before the next run. Set to false to go back to editor-only approval.
const AUTO_APPROVE = true;
const COLS = ['id','time','pin','reporter','district','place','lat','lng','headline','text','photo','status','note','link'];
// "Review": web news that the news tasks HOLD for the editor (crime allegations, deaths, communal, elections, emergencies,
// conflicting reports). The editor approves at /editor/ (tab "వెబ్ వార్తలు"); the reporter-stories task publishes approved ones.
const RCOLS = ['id','time','risk','headline','source','url','story','status','note','link','key','canon','approved','hash','by','approvedat'];
// RSS candidates (21 Nov 2026, no AI): tools/collect_feeds.py --candidates --post adds rows with risk "rss", status "candidate".
// The editor writes the Telugu card in /editor/ (tab 📡 RSS), opens the source, and approves ONE exact version:
// "approved" = that version as JSON, "hash" = its SHA-256. Only tools/publish_approved.py publishes these rows, and only
// the exact approved text. Editing after approval withdraws the approval. The newsroom (Claude) tasks never see rss rows.
// "Photos" (15 Nov 2026): OFFICIAL photos the editor attaches to a published story – government press releases (PIB, CMO, I&PR)
// or a party's/leader's official handle, for ANY party. Each row keeps the credit and the source link the photo came from.
const OCOLS = ['id','time','sid','headline','credit','person','party','srcurl','photo','status','note','link'];
function photos_() { let r = sheet_('Photos'); if (!r) { r = book_().insertSheet('Photos'); r.appendRow(OCOLS); r.setFrozenRows(1); } return r; }
function prows_() { const v = photos_().getDataRange().getValues(); return v.slice(1).map((r, i) => { const o = { _row: i + 2 }; OCOLS.forEach((c, j) => o[c] = String(r[j])); return o; }); }
function review_() {
  let r = sheet_('Review'); if (!r) { r = book_().insertSheet('Review'); r.appendRow(RCOLS); r.setFrozenRows(1); return r; }
  const h = r.getRange(1, 1, 1, Math.max(r.getLastColumn(), 1)).getValues()[0].map(String);   // older sheets: add the new columns at the end
  RCOLS.forEach(c => { if (h.indexOf(c) < 0) { h.push(c); r.getRange(1, h.length).setValue(c); } });
  return r;
}
function rset_(s, row, col, v) { const h = s.getRange(1, 1, 1, s.getLastColumn()).getValues()[0].map(String); s.getRange(row, h.indexOf(col) + 1).setValue(v); }
function sha256_(s) { return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, s, Utilities.Charset.UTF_8).map(b => ((b + 256) % 256).toString(16).padStart(2, '0')).join(''); }
const RSS_FIELDS = ['h','p','stat','statl','pic','lbl','region','topic','loc','src','url'];
// one fixed field order, so the same card always gives the same text and hash
function rssCard_(s, row) {
  const o = {}; RSS_FIELDS.forEach(k => o[k] = clean_(s && s[k], k === 'p' ? 1200 : k === 'url' ? 500 : 160).trim());
  if (!o.src) o.src = clean_(row.source, 80); if (!o.url) o.url = String(row.url || '');
  return o;
}
function rssProblem_(o) {
  if (!o.h) return 'headline'; if (!o.p) return 'summary'; if (!o.stat || !o.statl) return 'picture line';
  if (!/^(c|o|i|n|s|cv|w|d)\/[a-z0-9-]+$/.test(o.pic)) return 'picture';
  if (['fact','claim','opinion','forecast'].indexOf(o.lbl) < 0) return 'label';
  if (['telangana','ap','india','world'].indexOf(o.region) < 0) return 'region';
  if (!/^https:\/\//.test(o.url) || !o.src) return 'source';
  return '';
}
function rrows_() {
  const v = review_().getDataRange().getValues(), h = v[0];
  return v.slice(1).map((r, i) => { const o = { _row: i + 2 }; h.forEach((k, j) => o[k] = r[j]); return o; });
}

// Works both inside a Google Sheet (Extensions → Apps Script) and as a separate script:
// if there is no sheet, setup() creates "Swipe2News Reporters" in your Google Drive and remembers it.
function book_() {
  const a = SpreadsheetApp.getActiveSpreadsheet(); if (a) return a;
  const p = PropertiesService.getScriptProperties(), id = p.getProperty('SHEET_ID');
  if (id) return SpreadsheetApp.openById(id);
  const s = SpreadsheetApp.create('Swipe2News Reporters'); p.setProperty('SHEET_ID', s.getId()); return s;
}

function setup() {
  const ss = book_();
  let r = ss.getSheetByName('Reporters');
  if (!r) { r = ss.insertSheet('Reporters'); r.appendRow(['pin','name','phone','district','place','active']); r.appendRow(['1001','Sample Reporter','','yadadri','ఆలేరు','yes']); }
  let s = ss.getSheetByName('Submissions');
  if (!s) { s = ss.insertSheet('Submissions'); s.appendRow(COLS); s.setFrozenRows(1); }
  let a = ss.getSheetByName('Applications');
  if (!a) { a = ss.insertSheet('Applications'); a.appendRow(['time','name','phone','age','district','mandal','village','about','status','pin']); a.setFrozenRows(1); }
  folder_();
  Logger.log('Swipe2News Reporters sheet: ' + ss.getUrl());
}

function folder_() {
  const it = DriveApp.getFoldersByName(FOLDER);
  return it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER);
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function sheet_(n) { return book_().getSheetByName(n); }
function rows_() {
  const s = sheet_('Submissions'), v = s.getDataRange().getValues(), h = v[0];
  return v.slice(1).map((r, i) => { const o = { _row: i + 2 }; h.forEach((k, j) => o[k] = r[j]); return o; });
}
function reporter_(pin) {
  const v = sheet_('Reporters').getDataRange().getValues();
  for (let i = 1; i < v.length; i++) if (String(v[i][0]).trim() === String(pin).trim() && String(v[i][5]).toLowerCase() !== 'no') return { name: v[i][1], district: v[i][3], place: v[i][4] };
  return null;
}
function clean_(t, n) { return String(t || '').replace(/[<>]/g, '').slice(0, n); }

function doPost(e) {
  let b = {}; try { b = JSON.parse(e.postData.contents); } catch (x) { return out_({ ok: false, error: 'bad request' }); }
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    if (b.action === 'join') {   // new reporter application from https://swipe2news.com/reporter/join.html
      const phone = String(b.phone || '').replace(/\D/g, '');
      if (clean_(b.name, 60).length < 3 || !/^[6-9]\d{9}$/.test(phone) || Number(b.age) < 18) return out_({ ok: false, error: 'details' });
      let a = sheet_('Applications');
      if (!a) { a = book_().insertSheet('Applications'); a.appendRow(['time','name','phone','age','district','mandal','village','about','status','pin']); }
      const dup = a.getDataRange().getValues().some(r => String(r[2]) === phone);
      if (!dup) a.appendRow([Utilities.formatDate(new Date(), 'Asia/Kolkata', 'dd.MM.yyyy HH:mm'), clean_(b.name, 60), "'" + phone, Number(b.age) || '',
        clean_(b.district, 40), clean_(b.mandal, 40), clean_(b.village, 60), clean_(b.about, 400), 'new', '']);
      return out_({ ok: true });
    }
    if (b.action === 'submit') {
      const rep = reporter_(b.pin); if (!rep) return out_({ ok: false, error: 'pin' });
      const text = clean_(b.text, 3000); if (text.length < 30) return out_({ ok: false, error: 'short' });
      const id = Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyMMddHHmmss') + '-' + Math.floor(Math.random() * 900 + 100);
      let photo = '';
      if (b.photo && /^data:image\/jpeg;base64,/.test(b.photo) && b.photo.length < 2800000) {
        const blob = Utilities.newBlob(Utilities.base64Decode(b.photo.split(',')[1]), 'image/jpeg', id + '.jpg');
        photo = folder_().createFile(blob).getId();
      }
      sheet_('Submissions').appendRow([id, Utilities.formatDate(new Date(), 'Asia/Kolkata', 'dd.MM.yyyy HH:mm'), String(b.pin), rep.name,
        clean_(b.district, 40) || rep.district, clean_(b.place, 80) || rep.place, Number(b.lat) || '', Number(b.lng) || '',
        clean_(b.headline, 160), text, photo, 'pending', '', '']);
      return out_({ ok: true, id: id, name: rep.name });
    }
    if (b.action === 'list' && b.key === EDITOR_KEY) {
      return out_({ ok: true, items: rows_().slice(-60).reverse() });  // newest first; photos load one by one with "photo"
    }
    if (b.action === 'photo' && b.key === EDITOR_KEY) {
      const r = rows_().find(x => x.id === b.id); if (!r || !r.photo) return out_({ ok: false });
      return out_({ ok: true, data: 'data:image/jpeg;base64,' + Utilities.base64Encode(DriveApp.getFileById(r.photo).getBlob().getBytes()) });
    }
    if (b.action === 'decide' && b.key === EDITOR_KEY) {
      const r = rows_().find(x => x.id === b.id); if (!r) return out_({ ok: false, error: 'missing' });
      const st = b.decision === 'approve' ? 'approved' : 'rejected';
      const s = sheet_('Submissions'); s.getRange(r._row, COLS.indexOf('status') + 1).setValue(st); s.getRange(r._row, COLS.indexOf('note') + 1).setValue(clean_(b.note, 300));
      return out_({ ok: true, status: st });
    }
    if (b.action === 'approved' && b.key === BOT_KEY) {
      const items = rows_().filter(r => r.status === 'approved' ||
          (AUTO_APPROVE && r.status === 'pending' && String(r.note || '').indexOf('🤖') !== 0)).map(r => Object.assign({}, r,
        { auto: r.status === 'pending', photo_data: r.photo ? Utilities.base64Encode(DriveApp.getFileById(r.photo).getBlob().getBytes()) : '' }));
      return out_({ ok: true, items: items });
    }
    if (b.action === 'published' && b.key === BOT_KEY) {
      const r = rows_().find(x => x.id === b.id); if (!r) return out_({ ok: false });
      const s = sheet_('Submissions'); s.getRange(r._row, COLS.indexOf('status') + 1).setValue('published'); s.getRange(r._row, COLS.indexOf('link') + 1).setValue(clean_(b.link, 200));
      return out_({ ok: true });
    }
    if (b.action === 'needseditor' && b.key === BOT_KEY) {   // auto-approve screen said "editor must check" – keep pending, stop re-sending it
      const r = rows_().find(x => x.id === b.id); if (!r || r.status !== 'pending') return out_({ ok: false });
      sheet_('Submissions').getRange(r._row, COLS.indexOf('note') + 1).setValue('🤖 ఎడిటర్ పరిశీలన అవసరం: ' + clean_(b.reason, 200));
      return out_({ ok: true });
    }
    if (b.action === 'hold' && b.key === BOT_KEY) {   // news task: [{risk, story}] – story = the full Swipe2News story object
      const s = review_(), have = new Set(rrows_().map(r => String(r.url)));
      let added = 0;
      (Array.isArray(b.items) ? b.items : []).slice(0, 40).forEach(it => {
        const st = it && it.story; if (!st || !st.h) return;
        const url = String(st.url || ''); if (url && have.has(url)) return; have.add(url);
        const id = 'r' + Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyMMddHHmmss') + '-' + Math.floor(Math.random() * 900 + 100);
        s.appendRow([id, Utilities.formatDate(new Date(), 'Asia/Kolkata', 'dd.MM.yyyy HH:mm'), clean_(it.risk, 200), clean_(st.h, 200),
          clean_(st.src, 80), url.slice(0, 500), JSON.stringify(st).slice(0, 45000), 'pending', '', '']);
        added++;
      });
      return out_({ ok: true, added: added });
    }
    if (b.action === 'reviewlist' && b.key === EDITOR_KEY) {
      return out_({ ok: true, items: rrows_().filter(r => r.risk !== 'rss').slice(-60).reverse().map(r => { let st = {}; try { st = JSON.parse(r.story); } catch (x) {} return Object.assign({}, r, { story: st }); }) });
    }
    if (b.action === 'reviewdecide' && b.key === EDITOR_KEY) {
      const r = rrows_().find(x => x.id === b.id); if (!r) return out_({ ok: false, error: 'missing' });
      if (r.risk === 'rss' && b.decision === 'approve') return out_({ ok: false, error: 'use rssapprove' });   // rss: only an exact version can be approved
      const st = b.decision === 'approve' ? 'approved' : 'rejected', s = review_();
      s.getRange(r._row, RCOLS.indexOf('status') + 1).setValue(st); s.getRange(r._row, RCOLS.indexOf('note') + 1).setValue(clean_(b.note, 300));
      return out_({ ok: true, status: st });
    }
    if (b.action === 'reviewapproved' && b.key === BOT_KEY) {
      return out_({ ok: true, items: rrows_().filter(r => r.status === 'approved' && r.risk !== 'rss').map(r => { let st = {}; try { st = JSON.parse(r.story); } catch (x) {} return { id: r.id, risk: r.risk, note: r.note, story: st }; }) });
    }
    if (b.action === 'reviewpublished' && b.key === BOT_KEY) {
      const r = rrows_().find(x => x.id === b.id); if (!r) return out_({ ok: false });
      const s = review_(); s.getRange(r._row, RCOLS.indexOf('status') + 1).setValue('published'); s.getRange(r._row, RCOLS.indexOf('link') + 1).setValue(clean_(b.link, 200));
      return out_({ ok: true });
    }
    if (b.action === 'offphoto' && b.key === EDITOR_KEY) {   // editor attaches an official photo to a published story
      const src = String(b.srcurl || ''); if (!/^https:\/\//.test(src)) return out_({ ok: false, error: 'source link (https) required' });
      if (!b.sid || !b.data || !b.credit) return out_({ ok: false, error: 'missing' });
      const id = 'o' + Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyMMddHHmmss') + '-' + Math.floor(Math.random() * 900 + 100);
      const bytes = Utilities.base64Decode(String(b.data).replace(/^data:image\/\w+;base64,/, ''));
      if (bytes.length > 4 * 1024 * 1024) return out_({ ok: false, error: 'photo too big' });
      const f = folder_().createFile(Utilities.newBlob(bytes, 'image/jpeg', id + '.jpg'));
      photos_().appendRow([id, Utilities.formatDate(new Date(), 'Asia/Kolkata', 'dd.MM.yyyy HH:mm'), clean_(b.sid, 40), clean_(b.headline, 200),
        clean_(b.credit, 80), clean_(b.person, 80), clean_(b.party, 60), src.slice(0, 500), f.getId(), 'approved', '', '']);
      return out_({ ok: true, id: id });
    }
    if (b.action === 'offphotolist' && b.key === EDITOR_KEY) {
      return out_({ ok: true, items: prows_().slice(-40).reverse().map(r => Object.assign({}, r, { photo: '' })) });
    }
    if (b.action === 'offphotos' && b.key === BOT_KEY) {
      return out_({ ok: true, items: prows_().filter(r => r.status === 'approved').map(r => Object.assign({}, r,
        { photo_data: r.photo ? Utilities.base64Encode(DriveApp.getFileById(r.photo).getBlob().getBytes()) : '' })) });
    }
    if (b.action === 'offphotodone' && b.key === BOT_KEY) {   // status: published | rejected (note says why)
      const r = prows_().find(x => x.id === b.id); if (!r) return out_({ ok: false });
      const s = photos_(); s.getRange(r._row, OCOLS.indexOf('status') + 1).setValue(b.status === 'published' ? 'published' : 'rejected');
      s.getRange(r._row, OCOLS.indexOf('note') + 1).setValue(clean_(b.note, 200)); s.getRange(r._row, OCOLS.indexOf('link') + 1).setValue(clean_(b.link, 200));
      return out_({ ok: true });
    }
    if (b.action === 'candidates' && b.key === BOT_KEY) {   // RSS candidates from tools/collect_feeds.py --candidates --post
      const s = review_(), rows = rrows_();
      const keys = new Set(rows.map(r => String(r.key)).filter(Boolean)), canons = new Set(rows.map(r => String(r.canon)).filter(Boolean)), urls = new Set(rows.map(r => String(r.url)));
      let added = 0, dups = 0;
      (Array.isArray(b.items) ? b.items : []).slice(0, 60).forEach((it, i) => {
        const key = clean_(it && it.key, 40), canon = clean_(it && it.canon, 500), url = clean_(it && it.url, 500);
        if (!key || !/^https?:\/\//.test(url)) return;
        if (keys.has(key) || (canon && canons.has(canon)) || urls.has(url)) { dups++; return; }
        keys.add(key); if (canon) canons.add(canon); urls.add(url);
        const id = 'q' + Utilities.formatDate(new Date(), 'Asia/Kolkata', 'yyMMddHHmmss') + '-' + ('0' + i).slice(-2) + Math.floor(Math.random() * 90 + 10);
        const story = { src: clean_(it.outlet, 80), url: canon || url, title_src: clean_(it.title, 300), pub_src: clean_(it.time, 40), feed: clean_(it.feed, 80) };
        s.appendRow([id, Utilities.formatDate(new Date(), 'Asia/Kolkata', 'dd.MM.yyyy HH:mm'), 'rss', clean_(it.title, 200), clean_(it.outlet, 80), url,
          JSON.stringify(story), 'candidate', '', '', key, canon, '', '', '', '']);
        added++;
      });
      return out_({ ok: true, added: added, duplicates: dups });
    }
    if (b.action === 'rsslist' && b.key === EDITOR_KEY) {
      return out_({ ok: true, items: rrows_().filter(r => r.risk === 'rss').slice(-80).reverse().map(r => { let st = {}; try { st = JSON.parse(r.story); } catch (x) {} return Object.assign({}, r, { story: st }); }) });
    }
    if (b.action === 'rssedit' && b.key === EDITOR_KEY) {   // save the editor's Telugu card; any approval is withdrawn
      const r = rrows_().find(x => x.id === b.id && x.risk === 'rss'); if (!r) return out_({ ok: false, error: 'missing' });
      if (r.status === 'published' || r.status === 'rejected') return out_({ ok: false, error: r.status });
      let old = {}; try { old = JSON.parse(r.story); } catch (x) {}
      const card = Object.assign({ title_src: old.title_src, pub_src: old.pub_src, feed: old.feed }, rssCard_(b.story, r)), s = review_();
      rset_(s, r._row, 'story', JSON.stringify(card)); rset_(s, r._row, 'status', 'draft');
      ['approved','hash','by','approvedat'].forEach(c => rset_(s, r._row, c, ''));
      return out_({ ok: true, status: 'draft', story: card });
    }
    if (b.action === 'rssapprove' && b.key === EDITOR_KEY) {   // approve THIS exact version (the text the editor sees)
      const r = rrows_().find(x => x.id === b.id && x.risk === 'rss'); if (!r) return out_({ ok: false, error: 'missing' });
      if (r.status === 'published' || r.status === 'rejected') return out_({ ok: false, error: r.status });
      if (b.verified !== true) return out_({ ok: false, error: 'open and check the source first' });
      const by = clean_(b.by, 40).trim(); if (by.length < 2) return out_({ ok: false, error: 'your name' });
      const card = rssCard_(b.story, r), bad = rssProblem_(card); if (bad) return out_({ ok: false, error: 'missing ' + bad });
      const text = JSON.stringify(card), hash = 'sha256:' + sha256_(text), s = review_();   // prefix: Sheets never turns it into a number
      let old = {}; try { old = JSON.parse(r.story); } catch (x) {}
      rset_(s, r._row, 'story', JSON.stringify(Object.assign({ title_src: old.title_src, pub_src: old.pub_src, feed: old.feed }, card)));
      rset_(s, r._row, 'approved', text); rset_(s, r._row, 'hash', hash); rset_(s, r._row, 'by', by);
      rset_(s, r._row, 'approvedat', Utilities.formatDate(new Date(), 'Asia/Kolkata', "yyyy-MM-dd'T'HH:mm:ss'+05:30'")); rset_(s, r._row, 'status', 'approved');
      return out_({ ok: true, status: 'approved', hash: hash, approved: card });
    }
    if (b.action === 'rssapproved' && b.key === BOT_KEY) {   // for tools/publish_approved.py only: the exact approved text + its hash
      return out_({ ok: true, items: rrows_().filter(r => r.risk === 'rss' && r.status === 'approved' && r.approved && r.hash)
        .map(r => ({ id: r.id, approved: String(r.approved), hash: String(r.hash), by: String(r.by), approvedat: String(r.approvedat) })) });
    }
    return out_({ ok: false, error: 'not allowed' });
  } finally { lock.releaseLock(); }
}

function doGet() { return out_({ ok: true, service: 'Swipe2News newsroom' }); }
