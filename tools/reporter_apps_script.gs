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
const RCOLS = ['id','time','risk','headline','source','url','story','status','note','link'];
function review_() { let r = sheet_('Review'); if (!r) { r = book_().insertSheet('Review'); r.appendRow(RCOLS); r.setFrozenRows(1); } return r; }
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
      return out_({ ok: true, items: rrows_().slice(-60).reverse().map(r => { let st = {}; try { st = JSON.parse(r.story); } catch (x) {} return Object.assign({}, r, { story: st }); }) });
    }
    if (b.action === 'reviewdecide' && b.key === EDITOR_KEY) {
      const r = rrows_().find(x => x.id === b.id); if (!r) return out_({ ok: false, error: 'missing' });
      const st = b.decision === 'approve' ? 'approved' : 'rejected', s = review_();
      s.getRange(r._row, RCOLS.indexOf('status') + 1).setValue(st); s.getRange(r._row, RCOLS.indexOf('note') + 1).setValue(clean_(b.note, 300));
      return out_({ ok: true, status: st });
    }
    if (b.action === 'reviewapproved' && b.key === BOT_KEY) {
      return out_({ ok: true, items: rrows_().filter(r => r.status === 'approved').map(r => { let st = {}; try { st = JSON.parse(r.story); } catch (x) {} return { id: r.id, risk: r.risk, note: r.note, story: st }; }) });
    }
    if (b.action === 'reviewpublished' && b.key === BOT_KEY) {
      const r = rrows_().find(x => x.id === b.id); if (!r) return out_({ ok: false });
      const s = review_(); s.getRange(r._row, RCOLS.indexOf('status') + 1).setValue('published'); s.getRange(r._row, RCOLS.indexOf('link') + 1).setValue(clean_(b.link, 200));
      return out_({ ok: true });
    }
    return out_({ ok: false, error: 'not allowed' });
  } finally { lock.releaseLock(); }
}

function doGet() { return out_({ ok: true, service: 'Swipe2News newsroom' }); }
