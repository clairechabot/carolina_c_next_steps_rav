# Step 8 — The application tracker (30 min)

*Optional in the general template - REQUIRED here: the RAV compliance
layer (Step 11) is built on this sheet.*

A Google Sheet that fills itself. The job seeker never types a row:

- **☆ Save** buttons on the edition/Grove shortlist jobs into it.
- A small script inside their own Google account scans **Gmail** daily
  (application confirmations → Applied; company replies → Heard back;
  rejection wording → Rejected) and **Calendar** (matching meetings →
  Interview).
- With the VM (Step 9), their **LinkedIn** Applied list and recruiter
  replies feed in too.
- The newsletter reads it back: an "In play" section, Applied badges, and
  a nudge when an application has gone quiet 10+ days.
- **RAV edition**: the sheet carries the proof-of-efforts fields
  (employer address, workload %, how applied - pre-filled for Job-Room
  jobs) and auto-maintains a "RAV month" tab in the official form's
  column order. That tab is the heart of [Step 11](11-rav-compliance.md).

Full walkthrough: **[SHEET-SETUP.md](../SHEET-SETUP.md)** — sheet
creation, pasting the Apps Script, the two authorizations, publishing the
CSV, and the four `SHEET_*` repo variables. Everything runs inside the
job seeker's Google account; no passwords leave it.

Next: [Step 9 — the LinkedIn VM](09-linkedin-vm.md) (optional),
or jump to [Step 11 — the RAV compliance layer](11-rav-compliance.md).
