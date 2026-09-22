"""Monthly RAV proof-of-efforts export.

Reads the tracker sheet's published CSV, keeps the rows APPLIED in the
target month (previous month by default - the form is due early the
following month), and renders them as a print-ready A4 HTML page laid out
like the official "Nachweis der persoenlichen Arbeitsbemuehungen" table
(SECO form: date, employer + address, contact / via, position, workload,
how applied, outcome). Then emails it with a reminder of the deadline.

This is a COPY AID, not a forgery: every row is a real application the
tracker detected or the candidate saved-then-sent. The candidate signs
and submits it themselves (paper-form cantons), or uses it as the
copy-from list while typing into Job-Room / the canton portal. Print to
PDF straight from the attachment (Ctrl+P, save as PDF, A4).

Env:
    SHEET_CSV_URL       the sheet's published-CSV endpoint (required)
    RAV_MONTHLY_TARGET  quota for the "N of T" line (optional)
    RECIPIENT_NAME      printed in the form header (optional)
    SMTP_USER/SMTP_PASS/SMTP_HOST/SMTP_PORT/EMAIL_TO  as render.py
    ALLOW_NO_EMAIL=1    build the file, skip the send (testing)

Usage:
    python rav_export.py                # previous Zurich month
    python rav_export.py --month 2026-08
    python rav_export.py --no-email
"""
from __future__ import annotations

import argparse
import csv
import datetime
import html
import io
import os
import smtplib
from email.message import EmailMessage
from email.utils import getaddresses
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

HERE = Path(__file__).parent
ZURICH = ZoneInfo("Europe/Zurich")
FORMS_DIR = HERE / "rav_forms"

OUTCOME = {"Applied": "Pending", "Heard back": "In discussion",
           "Interview": "Interview", "Offer": "Offer",
           "Rejected": "Rejected"}


def esc(t) -> str:
    return html.escape(str(t if t is not None else ""), quote=True)


def previous_month(now: datetime.datetime) -> str:
    first = now.date().replace(day=1)
    prev = first - datetime.timedelta(days=1)
    return prev.strftime("%Y-%m")


def month_rows(month: str) -> list[dict]:
    csv_url = os.environ.get("SHEET_CSV_URL") or ""
    if not csv_url:
        raise SystemExit("ERROR: SHEET_CSV_URL not set - the export reads "
                         "the tracker sheet's published CSV.")
    resp = requests.get(csv_url, timeout=30)
    resp.raise_for_status()
    rows = []
    for r in csv.DictReader(io.StringIO(resp.text)):
        applied = (r.get("Applied on") or "").strip()
        if applied[:7] != month:
            continue
        rows.append({
            "date": applied[:10],
            "company": r.get("Company", ""),
            "address": r.get("Employer address", ""),
            "contact": r.get("Contact via", ""),
            "position": r.get("Title", ""),
            "workload": r.get("Workload %", ""),
            "method": r.get("How applied", ""),
            "outcome": OUTCOME.get(r.get("Status", ""),
                                   r.get("Status", "")),
        })
    rows.sort(key=lambda r: r["date"])
    return rows


def build_form(rows: list[dict], month: str) -> str:
    name = os.environ.get("RECIPIENT_NAME") or ""
    label = datetime.datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    target = int(os.environ.get("RAV_MONTHLY_TARGET") or 0)
    count_line = (f"{len(rows)} of {target} required efforts" if target
                  else f"{len(rows)} efforts")
    body_rows = "".join(
        f"""<tr>
        <td>{esc(r['date'])}</td>
        <td><b>{esc(r['company'])}</b><br>{esc(r['address'])}</td>
        <td>{esc(r['contact'])}</td>
        <td>{esc(r['position'])}</td>
        <td class="c">{esc(r['workload'])}</td>
        <td class="c">{esc(r['method'])}</td>
        <td>{esc(r['outcome'])}</td>
      </tr>""" for r in rows) or (
        '<tr><td colspan="7" class="c">No applications recorded for '
        'this month.</td></tr>')
    incomplete = [r for r in rows
                  if not (r["address"] and r["workload"] and r["method"])]
    warn = ("" if not incomplete else
            f'<p class="warn">{len(incomplete)} row(s) are missing an '
            'address, workload or application method - fill them in the '
            'tracker sheet, then re-run this export (Actions -&gt; '
            'RAV Form -&gt; Run workflow).</p>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Proof of personal job-search efforts - {esc(label)}</title>
<style>
  @page {{ size: A4; margin: 15mm; }}
  body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10.5px;
         color: #111; margin: 0; }}
  .sheet {{ max-width: 190mm; margin: 0 auto; padding: 8mm 0; }}
  h1 {{ font-size: 15px; margin: 0 0 2px; }}
  .sub {{ font-size: 10px; color: #444; margin-bottom: 10px; }}
  .head {{ display: flex; gap: 24px; margin: 10px 0 14px; }}
  .head div {{ border-bottom: 1px solid #999; min-width: 150px;
              padding: 2px 4px; }}
  .head span {{ display: block; font-size: 8px; color: #666;
               text-transform: uppercase; letter-spacing: .08em; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 1px solid #888; padding: 5px 6px; text-align: left;
           vertical-align: top; }}
  th {{ background: #efefef; font-size: 9px; text-transform: uppercase;
       letter-spacing: .05em; }}
  td.c, th.c {{ text-align: center; }}
  .count {{ margin: 10px 0; font-weight: bold; }}
  .warn {{ color: #8a2f0e; font-weight: bold; }}
  .sig {{ margin-top: 26px; display: flex; gap: 40px; }}
  .sig div {{ border-top: 1px solid #999; min-width: 200px;
             padding-top: 3px; font-size: 9px; color: #666; }}
  .note {{ margin-top: 16px; font-size: 8.5px; color: #666; }}
</style>
</head>
<body>
<div class="sheet">
  <h1>Proof of personal job-search efforts</h1>
  <div class="sub">Nachweis der persoenlichen Arbeitsbemuehungen -
    prepared from the application tracker for transcription into
    Job-Room / the cantonal form. Verify each row before submitting.</div>
  <div class="head">
    <div><span>Name</span>{esc(name) or "&nbsp;"}</div>
    <div><span>AHV no.</span>&nbsp;</div>
    <div><span>Month</span>{esc(label)}</div>
  </div>
  <div class="count">{esc(count_line)}</div>
  {warn}
  <table>
    <thead><tr>
      <th>Date</th><th>Employer (name, address)</th>
      <th>Contact / via</th><th>Position</th>
      <th class="c">Workload</th><th class="c">How applied</th>
      <th>Outcome</th>
    </tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
  <div class="sig">
    <div>Place, date</div>
    <div>Signature</div>
  </div>
  <div class="note">Every listed effort corresponds to a real application
    recorded by the tracker. Print to PDF: Ctrl+P, destination "Save as
    PDF", paper size A4.</div>
</div>
</body>
</html>
"""


def send_form(path: Path, month: str, n: int) -> None:
    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("EMAIL_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    smtp_host = (os.environ.get("SMTP_SERVER") or os.environ.get("SMTP_HOST")
                 or "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    recipients = [e for _, e in
                  getaddresses([os.environ.get("EMAIL_TO", "")]) if e]
    if not smtp_user or not smtp_pass:
        raise SystemExit("ERROR: SMTP_USER/SMTP_PASS not set.")
    if not recipients:
        raise SystemExit("ERROR: EMAIL_TO empty.")

    label = datetime.datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    sheet = os.environ.get("SHEET_LINK_URL") or ""
    msg = EmailMessage()
    msg["Subject"] = f"RAV proof of efforts - {label} ({n} applications)"
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)
    msg.set_content(
        f"Attached: the filled proof-of-efforts sheet for {label} "
        f"({n} applications), built from the tracker.\n\n"
        "1. Open the attachment, check every row.\n"
        "2. Fix anything wrong IN THE TRACKER SHEET"
        + (f" ({sheet})" if sheet else "")
        + ", then re-run the RAV Form workflow for a fresh copy.\n"
        "3. Submit the way your RAV expects: type the rows into Job-Room "
        "or the canton portal, or print the attachment to PDF/paper, "
        "sign, and hand it in.\n")
    msg.add_attachment(path.read_bytes(), maintype="text", subtype="html",
                       filename=path.name)
    print(f"[rav] Connecting to {smtp_host}:{smtp_port} ...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_bytes())
    print(f"[rav] Sent to {len(recipients)} recipient(s).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", help="YYYY-MM (default: previous month, "
                                        "Europe/Zurich)")
    parser.add_argument("--no-email", action="store_true")
    args = parser.parse_args()

    now = datetime.datetime.now(ZURICH)
    month = args.month or previous_month(now)
    if len(month) != 7 or month[4] != "-":
        raise SystemExit(f"ERROR: --month must be YYYY-MM, got {month!r}")

    rows = month_rows(month)
    print(f"[rav] {len(rows)} application(s) in {month}")
    FORMS_DIR.mkdir(exist_ok=True)
    out = FORMS_DIR / f"rav-{month}.html"
    out.write_text(build_form(rows, month), encoding="utf-8")
    print(f"[rav] wrote {out.relative_to(HERE)}")

    if args.no_email or os.environ.get("ALLOW_NO_EMAIL") == "1":
        print("[rav] email skipped")
    else:
        send_form(out, month, len(rows))


if __name__ == "__main__":
    main()
