# Client setup — Carolina

*The bundle has been applied to this repo (2026-09-22). This file keeps
the checklist; the sections below marked done need no action.*

Built 2026-09-22 from her intake form, CV, cover letter and writing
sample. RAV facts still generic (advisor appointment pending): quota 10,
German-language Job-Room form assumed, deadline the 5th assumed. Correct
the three after her appointment (only `RAV_MONTHLY_TARGET` is a setting;
the other two are conventions for the monthly ritual).

## What is in here

| Path | Goes to | Notes |
|---|---|---|
| `client/config.py` | `client/config.py` | tiers, title gate, Job-Room keywords, LinkedIn and Adzuna searches, recruiter watch, feeds |
| `profile/candidate.md` | `profile/candidate.md` | PUBLIC scoring profile, floors marked private |
| `claude-project/instructions.md` | Claude Project "Instructions" box | Vern, academic-to-industry playbook, English-only rule |
| `claude-project/knowledge/*.md` | Claude Project "Knowledge" | committed copies are floor-free and contact-free |

The PRIVATE files (real floors, contact line, insured salary) are not in
the repository. The operator holds them:
`CANDIDATE_PROFILE.md` (paste into the secret), `target-private.md` and
`master-cv-private.md` (upload to the Claude Project instead of the
committed copies).

## Create her repo (one repo per client) — DONE, steps 1-2

1. On this template repo: **Settings → General → tick "Template
   repository"** (that is why the green "Use this template" button was
   missing). Then **Use this template → Create a new repository**, e.g.
   `next-chapter-carolina`. Private is recommended for a client; the
   workflow already supports publishing the rendered edition to a small
   public site repo (`EDITION_REPO` + `EDITION_DEPLOY_TOKEN`), or use
   GitHub Pro for private Pages.
2. Clone it, then apply this bundle and commit:

   ```
   python tools/apply_client.py carolina
   git add -A && git commit -m "Client setup: Carolina" && git push
   ```

3. Settings → Actions → General: allow all actions; workflow permissions
   "Read and write".
4. Keep the template as upstream for later updates
   (onboarding/12-multi-client.md):

   ```
   git remote add upstream https://github.com/clairechabot/next-chapter-rav-template.git
   ```

## Secrets (Settings → Secrets and variables → Actions → Secrets)

| Secret | Value |
|---|---|
| `SMTP_USER` | the operator's sending Gmail |
| `SMTP_PASS` | its 16-character app password |
| `EMAIL_TO` | her new search Gmail (created on the call), comma-add the operator to shadow |
| `RECIPIENT_NAME` | `Carolina` |
| `CLAUDE_API_KEY` | console.anthropic.com key |
| `CANDIDATE_PROFILE` | the full text of the private `CANDIDATE_PROFILE.md` |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | optional; the config already carries CH, DE, NL, AT queries |

## Variables (Variables tab)

| Variable | Value |
|---|---|
| `RAV_MONTHLY_TARGET` | `10` (from the form; confirm with the advisor) |
| `EDITION_URL` | the Pages or edition-repo URL |
| `CLAUDE_MODEL` | leave unset for Opus, or `claude-sonnet-5` to cut cost |
| `SHEET_WEBHOOK_URL`, `SHEET_CSV_URL`, `SHEET_TOKEN`, `SHEET_LINK_URL` | from SHEET-SETUP.md, built on the call |

Delivery time is 18:30 Zurich, the template default: no workflow edit.
RAV form workflow runs on the 2nd; fine for a deadline on the 5th.

## Claude Project (her account, paid plan)

1. Projects → Create → "Next Chapter HQ".
2. Paste `claude-project/instructions.md` into Instructions.
3. Upload the five knowledge files, using the private `target-private.md`
   and `master-cv-private.md` in place of the committed copies, plus
   `achievements.md`, `voice-sample.md`, `home-market.md`.
4. Upload her CV .docx and the Lonza cover letter .docx.
5. Fill the `[NEEDS INPUT]` gaps in achievements.md with her on the call
   (numbers: donors, constructs, students trained, batches).

## Still open from the intake form

- RAV: advisor name, registration date, first benefit month, proof
  format, deadline, Job-Room account. Generic defaults until then.
- Dealbreakers, industries out, companies not to approach (all blank).
- LinkedIn Premium yes/no.
- Three or four achievements with numbers; one or two postings she would
  have applied to (calibration).
- Exact availability date after the defence.
- Confirm the calibration split: 3 wanted / 7 for compliance out of 10.
