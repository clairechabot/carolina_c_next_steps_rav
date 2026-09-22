# Step 11 — The RAV compliance layer

*Time: ~20 minutes (assuming the tracker from step 8 is already running).
This is the step that makes this the **RAV edition**.*

Anyone registered with a Swiss RAV (regional employment office) must prove
their job-search efforts every month: the "Nachweis der persönlichen
Arbeitsbemühungen", due at the start of the following month, listing every
application with date, employer and address, position, workload, how they
applied, and the outcome. Miss the quota or the deadline and benefit days
get docked.

This template turns that chore into a copy-paste (or less):

| Piece | What it does |
|---|---|
| Job-Room source (`sources/jobroom.py`) | Scans the official job board (job-room.ch, run by SECO — it also syndicates jobs.ch/jobup.ch ads). Each ad arrives WITH the employer's full postal address, the workload %, and the apply channel — exactly the form's fields. |
| Tracker columns | `Employer address`, `Workload %`, `How applied` — pre-filled by the Save button for Job-Room jobs, fill-if-empty for the rest. |
| "RAV YYYY-MM" tab | Auto-maintained by the sheet's script: the month's applications in the official form's column order. The monthly chore = open the tab, copy rows top-to-bottom into Job-Room or the cantonal form. Past months stay forever as the audit trail. |
| RAV meter | In the nightly email and the edition masthead: "7 of 12 applications this month — on pace". Behind pace, Vern's "One action" points at closing the gap. |
| Gap flags | The edition's In-play section flags any application whose tracker row is missing an address/workload/method, so the tab is complete before the deadline, not the night of. |
| `rav_export.py` + the RAV Form workflow | On the 2nd of each month (and on demand), emails a filled, print-ready A4 form for the previous month. If the RAV accepts the paper form, that's the whole chore. |

## The one rule that is not optional

**Every logged effort is a real application the candidate actually sent.**
The system makes real applications nearly effortless — it never invents
them. This is for the candidate's own protection: RAV advisors spot-check
with employers, and fabricated efforts are treated as benefit fraud
(sanctions, clawbacks). An automated log of *real* activity is
unimpeachable; an automated log of fake activity is evidence. There is no
mode in this template that logs an application that didn't happen — do
not add one.

For the same reason there is no auto-apply: drafts and tailored CVs come
from the Claude Project (step 7), and the human clicks send.

## Setup

1. Do step 8 (the tracker) first if you haven't. The header row in
   [SHEET-SETUP.md](../SHEET-SETUP.md) already includes the three RAV
   columns, and `tracker.gs` already maintains the monthly tab — nothing
   extra to install.
2. Add one repo variable (Settings → Secrets and variables → Actions →
   Variables): `RAV_MONTHLY_TARGET` = the monthly quota the RAV advisor
   set (typically 10–12). Unset = the meter and pace nudges stay off.
3. That's it for the meter and the tab. The monthly form email
   (`.github/workflows/rav_form.yml`) uses the same secrets as the
   newsletter; it starts working as soon as the tracker sheet has rows.

## The monthly ritual (what the candidate actually does)

1. **~2nd of the month:** the "RAV proof of efforts" email arrives with
   the filled form for last month attached.
2. Open it, check every row (the edition has been flagging gaps all
   month, so usually there are none).
3. Submit the way your RAV expects:
   - **Cantons accepting the paper form:** print the attachment to PDF
     (Ctrl+P → Save as PDF, A4), sign, submit. Done.
   - **Job-Room / canton portal:** open the sheet's "RAV <month>" tab and
     copy the rows top-to-bottom — the columns are already in the form's
     order.
4. If a row was wrong, fix it **in the Tracker tab** (the RAV tab is
   rebuilt from it), then Actions → RAV Form → Run workflow for a fresh
   copy.

## Customizing the search

`client/config.py` ships with an example (finance keywords, cantons
ZH/ZG/AG/SG, 60%+ workload). The [CUSTOMIZE.md](../CUSTOMIZE.md)
interview rewrites `JOBROOM_KEYWORDS`, `JOBROOM_CANTONS`, and
`JOBROOM_WORKLOAD_MIN` for the real candidate — and asks the RAV-specific questions (canton, quota, accepted
proof format, deadline day) so the whole layer comes out configured.

## What this deliberately does NOT do (v1)

- **No automatic entry into Job-Room.** If the canton insists on online
  entry, the copy-ready tab keeps it to minutes. Scripted entry into the
  candidate's Job-Room account is a separate, consent-heavy project —
  scope it explicitly if ever needed.
- **No auto-sent applications** — see the rule above.
