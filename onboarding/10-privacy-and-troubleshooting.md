# Step 10 — Privacy rules + troubleshooting

## Privacy (public-repo edition)

Never commit: real phone numbers, personal email addresses, exact salary
figures, or the full resume. Each has a private home by design:

| Data | Where it lives |
|---|---|
| Salary floors, private preferences | `CANDIDATE_PROFILE` secret (overrides the committed profile at scoring time) |
| Resume, contact details | Claude Project knowledge (private) |
| Passwords / API keys | GitHub Secrets |
| LinkedIn session files | the VM's disk only — never the repo |

The committed `profile/candidate.md` stays deliberately vague about
numbers. Keep it that way, and the public repo exposes nothing but job
preferences and a first name.

## When something breaks

- Every failure is visible: repo → **Actions** → the red run → the red
  step. Copy the last ~20 lines, paste into Claude, ask.
- The system degrades gracefully by design: one broken job board shows as
  "unavailable" in the run log while everything else keeps working. A
  missing optional setting just switches that feature off.
- Deep-dive troubleshooting sections live at the bottom of
  [SETUP.md](../SETUP.md), [SHEET-SETUP.md](../SHEET-SETUP.md) and
  [VM-SETUP.md](../VM-SETUP.md) (Gmail auth, LinkedIn session expiry, VM
  memory, cron timing).
- The **Interview Brief** bonus is already wired: Actions → Interview
  Brief → Run workflow → type a company name → a one-page prep brief
  lands in the inbox in ~2 minutes.
