/**
 * Next Chapter — Application Tracker (Google Apps Script)
 *
 * Lives INSIDE the candidate's Google account, bound to the tracker spreadsheet.
 * Three jobs, zero manual entry:
 *   1. doPost      — webhook for the newsletter's Save buttons and the VM's
 *                    LinkedIn feed (applied list + recruiter replies).
 *   2. scanGmail   — daily: application confirmations -> Applied; replies
 *                    from tracked companies -> Heard back; rejection
 *                    phrasing -> Rejected.
 *   3. scanCalendar— daily: events matching a tracked company -> Interview
 *                    with the meeting date.
 * Setup steps: see SHEET-SETUP.md in the repo. Run dailyScan on a daily
 * time trigger; deploy doPost as a Web app (execute as me / anyone).
 *
 * Status ladder (writes only ever move UP; Rejected is terminal):
 *   Saved -> Applied -> Heard back -> Interview -> Offer   |  Rejected
 *
 * RAV edition: three extra columns (Employer address, Workload %, How
 * applied) carry the fields the monthly "Nachweis persoenlicher
 * Arbeitsbemuehungen" form asks for. Job-Room ads arrive with all three
 * pre-filled via the Save button; a "RAV YYYY-MM" tab is rebuilt on every
 * write with the month's APPLIED rows in the official form's column
 * order, ready to copy row-by-row into the RAV system. Past months'
 * tabs are never touched — they are the permanent audit trail.
 */

var SHEET_NAME = 'Tracker';
var TOKEN = 'CHANGE-ME-any-random-words';   // must match the repo's SHEET_TOKEN variable

var HEADERS = ['First seen', 'Applied on', 'Last contact on', 'Contact via',
               'Meeting on', 'Status', 'Title', 'Company', 'Location',
               'Employer address', 'Workload %', 'How applied',
               'Salary', 'Score', 'Source', 'Job URL', 'Detected via',
               'Last update', 'Notes'];
// RAV monthly-tab columns, in the order the official form asks for them.
var RAV_HEADERS = ['Date of application', 'Company', 'Address',
                   'Contact / via', 'Position', 'Workload %',
                   'How applied', 'Outcome'];
var COL = {};  // name -> 1-based column index, filled by sheet_()
var LADDER = {'': 0, 'Saved': 1, 'Applied': 2, 'Heard back': 3,
              'Interview': 4, 'Offer': 5, 'Rejected': 9, 'Withdrawn': 9};

var REJECTION_PHRASES = ['unfortunately', 'other candidates', 'not selected',
                         'not moving forward', 'decided to pursue',
                         'will not be moving', 'position has been filled'];
var CONFIRMATION_SUBJECTS = ['your application was sent to',
                             'thank you for applying',
                             'application received',
                             'we received your application',
                             'your application to'];
// Senders that are confirmations/notifications, never a human reply.
var NOREPLY = /no-?reply|donotreply|notifications?@|jobs-noreply|talent@linkedin/i;

// ---------------------------------------------------------------------------
// Identity — mirrors history.py normalize_url / job_fingerprint in the repo
// ---------------------------------------------------------------------------
function normalizeUrl(url) {
  var u = (url || '').trim();
  var m = u.match(/linkedin\.com\/jobs\/view\/(?:[^\/?#]*?-)?(\d{6,})/i);
  if (m) return 'linkedin:' + m[1];
  u = u.split('#')[0].split('?')[0].replace(/\/+$/, '').toLowerCase();
  return u.replace(/^https?:\/\/(www\.)?/, '');
}

function normalizeText(t) {
  t = (t || '').toLowerCase().trim();
  ['inc', 'inc.', 'ltd', 'ltd.', 'limited', 'llc', 'corp', 'corp.',
   'co.', 'co', 'group', 'canada'].forEach(function (s) {
    if (t.slice(-(s.length + 1)) === ' ' + s) t = t.slice(0, -(s.length + 1)).trim();
  });
  return t.replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function fingerprint(company, title) {
  return normalizeText(company) + '|' + normalizeText(title);
}

// A short token for matching a company in email senders / event text.
// "Acme Widgets Inc" -> "acme"; skip tokens under 4 chars.
function companyToken(company) {
  var words = normalizeText(company).split(' ').filter(function (w) {
    return w.length >= 4;
  });
  return words.length ? words[0] : '';
}

// ---------------------------------------------------------------------------
// Sheet access + upsert
// ---------------------------------------------------------------------------
function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
  }
  HEADERS.forEach(function (h, i) { COL[h] = i + 1; });
  return sh;
}

function findRow_(sh, url, company, title) {
  var data = sh.getDataRange().getValues();
  var nurl = normalizeUrl(url);
  var fp = fingerprint(company, title);
  for (var r = 1; r < data.length; r++) {
    var rowUrl = data[r][COL['Job URL'] - 1];
    if (nurl && rowUrl && normalizeUrl(rowUrl) === nurl) return r + 1;
    if (company && title &&
        fingerprint(data[r][COL['Company'] - 1],
                    data[r][COL['Title'] - 1]) === fp) return r + 1;
  }
  return 0;
}

function today_() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone(),
                              'yyyy-MM-dd');
}

/**
 * evt: {action, title, company, location, salary, score, source, url,
 *       via, date, address, workload, method}
 * action: save | unsave | applied | contact | meeting | rejected
 * address/workload/method are the RAV form fields — Job-Room jobs carry
 * them on the Save button; they backfill empty cells on existing rows too
 * (a Gmail-detected Applied row gains its address when the job is Saved).
 */
function upsert(evt) {
  var sh = sheet_();
  var row = findRow_(sh, evt.url || '', evt.company || '', evt.title || '');
  var isNew = !row;
  if (isNew) {
    row = sh.getLastRow() + 1;
    sh.getRange(row, COL['First seen']).setValue(today_());
    ['Title', 'Company', 'Location', 'Salary', 'Score', 'Source']
      .forEach(function (f) {
        var v = evt[f.toLowerCase()];
        if (v !== undefined && v !== null && v !== '')
          sh.getRange(row, COL[f]).setValue(v);
      });
    if (evt.url) sh.getRange(row, COL['Job URL']).setValue(evt.url);
    if (evt.via) sh.getRange(row, COL['Detected via']).setValue(evt.via);
  }
  // RAV fields: fill-if-empty on new AND existing rows, never overwrite
  // a hand-corrected cell.
  [['Employer address', evt.address], ['Workload %', evt.workload],
   ['How applied', evt.method]].forEach(function (pair) {
    if (pair[1] && !sh.getRange(row, COL[pair[0]]).getValue())
      sh.getRange(row, COL[pair[0]]).setValue(pair[1]);
  });
  var current = String(sh.getRange(row, COL['Status']).getValue() || '');
  var when = evt.date || today_();

  var target = '';
  if (evt.action === 'save') target = 'Saved';
  if (evt.action === 'applied') {
    target = 'Applied';
    if (!sh.getRange(row, COL['Applied on']).getValue())
      sh.getRange(row, COL['Applied on']).setValue(when);
  }
  if (evt.action === 'contact') {
    target = 'Heard back';
    sh.getRange(row, COL['Last contact on']).setValue(when);
    if (evt.via) sh.getRange(row, COL['Contact via']).setValue(evt.via);
  }
  if (evt.action === 'meeting') {
    target = 'Interview';
    sh.getRange(row, COL['Meeting on']).setValue(when);
  }
  if (evt.action === 'rejected') target = 'Rejected';
  if (evt.action === 'unsave') {
    // Only clears a plain bookmark; never touches an application in flight.
    if (current === 'Saved') sh.getRange(row, COL['Status']).setValue('');
    sh.getRange(row, COL['Last update']).setValue(today_());
    return {row: row, status: ''};
  }

  // Ladder: never move DOWN (a Saved click after Applied changes nothing).
  if (target && LADDER[target] > (LADDER[current] || 0)) {
    sh.getRange(row, COL['Status']).setValue(target);
    current = target;
  }
  sh.getRange(row, COL['Last update']).setValue(today_());
  return {row: row, status: current, isNew: isNew};
}

// ---------------------------------------------------------------------------
// 1. Webhook (Save buttons + VM LinkedIn feed)
// ---------------------------------------------------------------------------
function doPost(e) {
  var out = {ok: false};
  try {
    var evt = JSON.parse(e.postData.contents);
    if (evt.token !== TOKEN) {
      out.error = 'bad token';
    } else {
      var res = upsert(evt);
      updateRavTab_();
      out = {ok: true, row: res.row, status: res.status};
    }
  } catch (err) {
    out.error = String(err);
  }
  return ContentService.createTextOutput(JSON.stringify(out))
    .setMimeType(ContentService.MimeType.JSON);
}

// ---------------------------------------------------------------------------
// RAV monthly tab — "RAV YYYY-MM", rebuilt from the CURRENT month's
// Applied rows on every write. One row per real application, columns in
// the official form's order, so the monthly chore is copy top-to-bottom.
// Past months' tabs are left alone (permanent audit trail).
// ---------------------------------------------------------------------------
function ravOutcome_(status) {
  return {'Applied': 'Pending', 'Heard back': 'In discussion',
          'Interview': 'Interview', 'Offer': 'Offer',
          'Rejected': 'Rejected'}[status] || status;
}

function updateRavTab_() {
  var sh = sheet_();
  var month = Utilities.formatDate(new Date(), Session.getScriptTimeZone(),
                                   'yyyy-MM');
  var tabName = 'RAV ' + month;
  var data = sh.getDataRange().getValues();
  var rows = [];
  for (var r = 1; r < data.length; r++) {
    var applied = data[r][COL['Applied on'] - 1];
    if (!applied) continue;
    var appliedStr = applied instanceof Date
      ? Utilities.formatDate(applied, Session.getScriptTimeZone(),
                             'yyyy-MM-dd')
      : String(applied);
    if (appliedStr.slice(0, 7) !== month) continue;
    rows.push([appliedStr,
               data[r][COL['Company'] - 1],
               data[r][COL['Employer address'] - 1],
               data[r][COL['Contact via'] - 1],
               data[r][COL['Title'] - 1],
               data[r][COL['Workload %'] - 1],
               data[r][COL['How applied'] - 1],
               ravOutcome_(String(data[r][COL['Status'] - 1] || ''))]);
  }
  rows.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tab = ss.getSheetByName(tabName);
  if (!tab) {
    tab = ss.insertSheet(tabName);
    tab.setFrozenRows(1);
  }
  tab.clearContents();
  tab.appendRow(RAV_HEADERS);
  if (rows.length)
    tab.getRange(2, 1, rows.length, RAV_HEADERS.length).setValues(rows);
}

// ---------------------------------------------------------------------------
// 2. Gmail scan (daily)
// ---------------------------------------------------------------------------
function scanGmail() {
  // A. New application confirmations (any company, last 3 days).
  var q = 'newer_than:3d (' + CONFIRMATION_SUBJECTS.map(function (s) {
    return 'subject:"' + s + '"';
  }).join(' OR ') + ')';
  GmailApp.search(q, 0, 30).forEach(function (thread) {
    var msg = thread.getMessages()[0];
    var subject = msg.getSubject() || '';
    var company = '';
    // "Your application was sent to Acme Widgets" / "Your application to X"
    var m = subject.match(/application (?:was sent|to|received)[^A-Za-z0-9]*(?:to\s+)?(.+)$/i);
    if (m) company = m[1].replace(/[.!]$/, '').trim();
    if (!company) {
      var from = msg.getFrom() || '';
      company = (from.split('<')[0] || '').replace(/["']/g, '').trim();
    }
    if (!company) return;
    upsert({action: 'applied', company: company, title: subjectTitle_(subject),
            via: 'gmail', date: Utilities.formatDate(msg.getDate(),
              Session.getScriptTimeZone(), 'yyyy-MM-dd')});
  });

  // B. Replies + rejections from tracked companies.
  trackedRows_().forEach(function (t) {
    var token = companyToken(t.company);
    if (!token) return;
    GmailApp.search('newer_than:3d from:(' + token + ')', 0, 10)
      .forEach(function (thread) {
        thread.getMessages().forEach(function (msg) {
          var from = msg.getFrom() || '';
          if (NOREPLY.test(from)) return;
          var when = Utilities.formatDate(msg.getDate(),
            Session.getScriptTimeZone(), 'yyyy-MM-dd');
          var body = (msg.getPlainBody() || '').slice(0, 2000).toLowerCase();
          var rejected = REJECTION_PHRASES.some(function (p) {
            return body.indexOf(p) !== -1;
          });
          upsert({action: rejected ? 'rejected' : 'contact',
                  company: t.company, title: t.title, url: t.url,
                  via: 'email', date: when});
        });
      });
  });
}

function subjectTitle_(subject) {
  // Best-effort role from "Your application to Acme for VP Finance" shapes.
  var m = subject.match(/for (?:the )?(?:position of |role of )?(.+)$/i);
  return m ? m[1].trim() : '';
}

function trackedRows_() {
  var sh = sheet_();
  var data = sh.getDataRange().getValues();
  var rows = [];
  for (var r = 1; r < data.length; r++) {
    var status = String(data[r][COL['Status'] - 1] || '');
    if (!status || status === 'Rejected' || status === 'Withdrawn') continue;
    rows.push({company: String(data[r][COL['Company'] - 1] || ''),
               title: String(data[r][COL['Title'] - 1] || ''),
               url: String(data[r][COL['Job URL'] - 1] || '')});
  }
  return rows;
}

// ---------------------------------------------------------------------------
// 3. Calendar scan (daily)
// ---------------------------------------------------------------------------
function scanCalendar() {
  var now = new Date();
  var start = new Date(now.getTime() - 2 * 24 * 3600 * 1000);
  var end = new Date(now.getTime() + 30 * 24 * 3600 * 1000);
  var events = CalendarApp.getDefaultCalendar().getEvents(start, end);
  var tracked = trackedRows_();
  events.forEach(function (ev) {
    var text = (ev.getTitle() + ' ' + (ev.getDescription() || '')).toLowerCase();
    var guests = ev.getGuestList().map(function (g) {
      return g.getEmail().toLowerCase();
    }).join(' ');
    tracked.forEach(function (t) {
      var token = companyToken(t.company);
      if (!token) return;
      if (text.indexOf(token) !== -1 || guests.indexOf(token) !== -1) {
        upsert({action: 'meeting', company: t.company, title: t.title,
                url: t.url, via: 'calendar',
                date: Utilities.formatDate(ev.getStartTime(),
                  Session.getScriptTimeZone(), 'yyyy-MM-dd')});
      }
    });
  });
}

// The function to put on the daily time trigger.
function dailyScan() {
  scanGmail();
  scanCalendar();
  updateRavTab_();
}
