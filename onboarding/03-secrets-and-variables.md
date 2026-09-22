# Step 3 — Secrets and variables (20 min)

Your repo → **Settings → Secrets and variables → Actions**. Two tabs
matter: **Secrets** (passwords — encrypted, never visible again) and
**Variables** (plain settings).

## Secrets tab → "New repository secret", one at a time

| Secret | Value |
|---|---|
| `CLAUDE_API_KEY` | the key from console.anthropic.com (Step 1) |
| `SMTP_USER` | the Gmail address the newsletter sends FROM |
| `SMTP_PASS` | a 16-character **Gmail app password** — see below |
| `EMAIL_TO` | where the newsletter goes; comma-separate to add the operator as a shadow copy |
| `CANDIDATE_PROFILE` | leave for Step 6 — the private scoring profile with real salary numbers |
| `RECIPIENT_NAME` | the job seeker's first name (a secret so the public repo never names them) |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | optional extra job source — free keys at developer.adzuna.com |

**Getting the Gmail app password**: google.com → your account (top-right
avatar) → **Security** → turn on **2-Step Verification** if it isn't →
search the settings for **"App passwords"** → create one named "Mail".
Google shows a 16-character code once — that's `SMTP_PASS` (spaces don't
matter).

## Variables tab → "New repository variable"

| Variable | Value |
|---|---|
| `EDITION_URL` | the web edition's address — you get it in Step 4 |
| `CLAUDE_MODEL` | optional. Default is `claude-opus-5` (best quality); set `claude-sonnet-5` to cut scoring cost ~80% |
| `RAV_MONTHLY_TARGET` | the monthly application quota the RAV advisor set (typically 10–12). Powers the RAV meter, the behind-pace nudge, and the "N of T" line on the exported form. Unset = meter off |

(Four more `SHEET_*` variables belong to the tracker — [Step 8](08-application-tracker.md);
the RAV form workflow reuses them plus `RAV_MONTHLY_TARGET` —
[Step 11](11-rav-compliance.md).)

Next: [Step 4 — Turn on the web edition](04-web-edition.md)
