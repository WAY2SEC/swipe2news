#!/usr/bin/env node
/* Swipe2News newsroom emulator – runs the REAL tools/reporter_apps_script.gs on this machine for staging tests.
 *
 *   EDITOR_KEY=… BOT_KEY=… node tools/staging/newsroom_emulator.js --port 8787 --state /tmp/newsroom-state.json
 *
 * The script's own doPost() handles every request, exactly as Google Apps Script would, against an in-memory Google
 * Sheet that is saved to --state after each request. It never talks to Google: the live reporter Sheet can't be
 * touched from here. Keys come from the environment and are only substituted in memory (never written to disk).
 * Not emulated: Drive uploads (reporter photos) and Sheets' automatic number/date conversion of typed values.
 */
'use strict';
const fs = require('fs'), path = require('path'), http = require('http'), vm = require('vm'), crypto = require('crypto');

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const PORT = Number(arg('--port', 8787)), STATE = arg('--state', '/tmp/newsroom-state.json');
const GS = arg('--script', path.join(__dirname, '..', 'reporter_apps_script.gs'));
const EK = process.env.EDITOR_KEY || '', BK = process.env.BOT_KEY || '';
if (EK.length < 6 || BK.length < 12) { console.error('set EDITOR_KEY (≥6) and BOT_KEY (≥12) in the environment'); process.exit(1); }

// ---- fake Google Sheet -------------------------------------------------------------------------------
let BOOK = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : { sheets: {} };
const save = () => fs.writeFileSync(STATE, JSON.stringify(BOOK, null, 1));
function Sheet(name) {
  const rows = () => BOOK.sheets[name];
  const width = () => rows().reduce((m, r) => Math.max(m, r.length), 0);
  const cell = (r, c) => { const x = rows()[r - 1]; return x && x[c - 1] !== undefined ? x[c - 1] : ''; };
  const range = (r, c, nr = 1, nc = 1) => ({
    getValues: () => Array.from({ length: nr }, (_, i) => Array.from({ length: nc }, (_, j) => cell(r + i, c + j))),
    getValue: () => cell(r, c),
    setValue: v => { while (rows().length < r) rows().push([]); const x = rows()[r - 1]; while (x.length < c) x.push(''); x[c - 1] = v instanceof Date ? v.toISOString() : v; return this; },
  });
  return {
    getName: () => name,
    appendRow: a => { rows().push(a.map(v => (v instanceof Date ? v.toISOString() : v))); },
    getDataRange: () => range(1, 1, Math.max(rows().length, 1), Math.max(width(), 1)),
    getRange: range,
    getLastRow: () => rows().length,
    getLastColumn: () => width(),
    setFrozenRows: () => {},
  };
}
const SPREADSHEET = {
  getSheetByName: n => (BOOK.sheets[n] ? Sheet(n) : null),
  insertSheet: n => { BOOK.sheets[n] = BOOK.sheets[n] || []; return Sheet(n); },
  getId: () => 'emulated-staging-sheet', getUrl: () => 'about:emulated-staging-sheet',
};

// ---- the Apps Script services the newsroom script uses ------------------------------------------------
const pad = (n, w = 2) => String(n).padStart(w, '0');
function formatDate(d, tz, fmt) {   // supports the patterns in reporter_apps_script.gs; tz: Asia/Kolkata (+05:30)
  const off = tz === 'Asia/Kolkata' ? 330 : 0, t = new Date(d.getTime() + off * 60000);
  const map = { yyyy: t.getUTCFullYear(), yy: pad(t.getUTCFullYear() % 100), MM: pad(t.getUTCMonth() + 1), dd: pad(t.getUTCDate()),
    HH: pad(t.getUTCHours()), mm: pad(t.getUTCMinutes()), ss: pad(t.getUTCSeconds()) };
  return fmt.split(/('[^']*')/).map(p => (p.startsWith("'") ? p.slice(1, -1) : p.replace(/yyyy|yy|MM|dd|HH|mm|ss/g, k => map[k]))).join('');
}
const ctx = {
  console,
  SpreadsheetApp: { getActiveSpreadsheet: () => SPREADSHEET, openById: () => SPREADSHEET, create: () => SPREADSHEET },
  PropertiesService: { getScriptProperties: () => ({ getProperty: () => null, setProperty: () => {} }) },
  LockService: { getScriptLock: () => ({ waitLock: () => {}, releaseLock: () => {} }) },
  ContentService: { MimeType: { JSON: 'json' }, createTextOutput: s => ({ s, setMimeType() { return this; } }) },
  Utilities: {
    formatDate,
    DigestAlgorithm: { SHA_256: 'sha256' }, Charset: { UTF_8: 'utf8' },
    computeDigest: (alg, s) => Array.from(crypto.createHash(alg).update(String(s), 'utf8').digest()).map(b => (b > 127 ? b - 256 : b)),
    base64Decode: () => { throw new Error('photo uploads are not emulated'); },
    newBlob: () => { throw new Error('photo uploads are not emulated'); },
  },
  DriveApp: new Proxy({}, { get: () => () => { throw new Error('Drive is not emulated'); } }),
};
let src = fs.readFileSync(GS, 'utf8');
if (!src.includes("'PUT-EDITOR-KEY-HERE'") || !src.includes("'PUT-BOT-KEY-HERE'")) { console.error('script must contain the placeholder keys'); process.exit(1); }
src = src.replace("'PUT-EDITOR-KEY-HERE'", JSON.stringify(EK)).replace("'PUT-BOT-KEY-HERE'", JSON.stringify(BK));
vm.createContext(ctx);
vm.runInContext(src + '\n;this.__doPost = doPost; this.__doGet = doGet;', ctx, { filename: 'reporter_apps_script.gs' });

// ---- HTTP, like the web app URL -----------------------------------------------------------------------
const LOG = arg('--log', '');
http.createServer((req, res) => {
  const send = (code, body) => { res.writeHead(code, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Content-Type': 'application/json; charset=utf-8' }); res.end(body); };
  if (req.method === 'OPTIONS') return send(204, '');
  if (req.method === 'GET') return send(200, ctx.__doGet().s);
  let body = '';
  req.on('data', c => (body += c));
  req.on('end', () => {
    let out;
    try { out = ctx.__doPost({ postData: { contents: body } }).s; } catch (e) { out = JSON.stringify({ ok: false, error: 'script error: ' + e.message }); }
    save();
    if (LOG) { let a = ''; try { a = JSON.parse(body).action; } catch (e) {} fs.appendFileSync(LOG, `${new Date().toISOString()} ${a} -> ${out.slice(0, 120)}\n`); }
    send(200, out);
  });
}).listen(PORT, '127.0.0.1', () => console.log(`newsroom emulator on http://127.0.0.1:${PORT}  state=${STATE}`));
