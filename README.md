# The Next Chapter: RAV edition — a Swiss job-search machine that files its own paperwork

> **What it costs: ~$10–35/month**, depending on choices.
>
> | | |
> |---|---|
> | Claude API — nightly job scoring + Vern's notes | **~$10–20/mo** on the default model (Opus); **~$2–4/mo** if you set it to Sonnet |
> | GitHub — code, automation, the web edition | **$0** (public repo) or $4/mo (GitHub Pro, if you want the repo private) |
> | Email sending (Gmail), job-board scraping, the tracker sheet | **$0** |
> | Optional: always-on VM for authenticated LinkedIn scanning | **+$12/mo** (skippable — everything else works without it) |
> | Claude Pro for the career-coach Project | whatever plan the job seeker already has (from $20/mo) |
>
> Typical setups: **~$12/month** (Sonnet scoring, public repo, no VM) to
> **~$32/month** (Opus scoring + the LinkedIn VM). No subscriptions to this
> template itself — everything runs in your own accounts, on your own keys.

A template for building a Swiss job seeker their own automated job
search — with the monthly RAV proof-of-efforts chore automated away.
Built for anyone registered with an RAV who must document 10–12 real
applications a month or lose benefit days:

- **A nightly email** ("The Next Chapter") that scans job boards, LinkedIn,
  and recruiter sites, has Claude score every posting against a personal
  profile (location, level, salary floors, dealbreakers), and delivers the
  short verdict at the evening hour you choose — with a note from **Vern**,
  the search's fictional scout, who writes with measured, literate warmth.
- **A full web edition** on GitHub Pages: every scored job with a
  "why" / "watch out", a copy-paste **Claude Project prompt** per good job,
  a searchable archive (**The Grove**), a recruiter watch, an AI-for-your-
  field reading list, and one dad joke a day.
- **A Claude Project career coach** (also Vern): blunt fit checks, CV
  tailoring, cover letters in the candidate's own voice, interview prep,
  outreach drafting — grounded in their real career facts, never invented.
- **A zero-typing application tracker** (Google Sheet): Save buttons on the
  edition, and automatic detection of applications, replies, rejections and
  interviews from Gmail, Calendar, and LinkedIn.
- **The RAV compliance layer**: the official Job-Room (arbeit.swiss) board
  as source #1 (its ads carry the employer address, workload % and apply
  channel — the exact form fields); an auto-maintained "RAV month" sheet
  tab in the official form's column order; an "N of 12 this month — on
  pace" meter in every email; and a filled, print-ready proof-of-efforts
  form emailed on the 2nd of each month. See
  [onboarding/11-rav-compliance.md](onboarding/11-rav-compliance.md).
- **Optional extras**: an always-on VM for authenticated LinkedIn scanning
  with hiring-team contact extraction, and an on-demand interview brief.

The built-in **working example** is a finance professional in the Zurich
region; every part of it — titles, cantons, keywords, recruiters — is
replaced with the real candidate's search via a guided Claude
conversation ([CUSTOMIZE.md](CUSTOMIZE.md)).

## Start here — the onboarding path

Work through **[onboarding/](onboarding/README.md)** in order. Steps 1–5
get a real email flowing the same day (using the built-in example search);
6–7 make it the job seeker's own; 8 and 11 are the RAV compliance heart
of this edition; 9 is an optional power-up.

| | Step | Time |
|---|---|---|
| 1 | [Accounts you need](onboarding/01-accounts.md) | 15 min |
| 2 | [Copy the template](onboarding/02-copy-the-template.md) | 10 min |
| 3 | [Secrets and variables](onboarding/03-secrets-and-variables.md) | 20 min |
| 4 | [Turn on the web edition](onboarding/04-web-edition.md) | 10 min |
| 5 | [First run + delivery time](onboarding/05-first-run.md) | 15 min |
| 6 | [Personalize it with Claude](onboarding/06-personalize-with-claude.md) — uses [CUSTOMIZE.md](CUSTOMIZE.md) | 45 min |
| 7 | [The Claude Project coach](onboarding/07-claude-project-coach.md) | 20 min |
| 8 | [Application tracker](onboarding/08-application-tracker.md) — required for the RAV layer; deep dive: [SHEET-SETUP.md](SHEET-SETUP.md) | 30 min |
| 9 | [Optional: LinkedIn VM](onboarding/09-linkedin-vm.md) — deep dive: [VM-SETUP.md](VM-SETUP.md) | 1–2 h |
| 10 | [Privacy rules + troubleshooting](onboarding/10-privacy-and-troubleshooting.md) | read once |
| 11 | [The RAV compliance layer](onboarding/11-rav-compliance.md) | 20 min |
| 12 | [Operators: several clients from one template](onboarding/12-multi-client.md) | 15 min |

Written for someone who has barely used Claude or GitHub — and the
standing advice throughout: keep Claude open in another tab and paste
anything confusing into it.

## Honest notes before you begin

- **Privacy**: the simplest free setup uses a public repo. This template is
  built for that: real salary floors, phone numbers, and CV details live in
  GitHub *secrets* and the private Claude Project, never in committed
  files. [onboarding/10-privacy-and-troubleshooting.md](onboarding/10-privacy-and-troubleshooting.md)
  walks the line — read it before committing anything personal.
- **LinkedIn**: the authenticated scanning layer is against LinkedIn's
  terms of service. It is gentle (a handful of searches nightly, human
  pacing, reads only your own data for the tracker), but the account used
  carries a small restriction risk. The guide explains the trade-offs; the
  whole system works without it.
- **Real records only — the non-negotiable rule of the RAV edition**:
  every application the system logs is one the candidate actually sent.
  The automation makes real applications nearly effortless (scored leads,
  drafted materials, one-click tracking, the filled form) — it never
  invents effort. Fabricated entries are benefit fraud and, worse for the
  candidate, self-documenting evidence: RAV advisors spot-check with
  employers. There is no auto-apply and no fake-log mode, by design.
- **This is a template, not a service**: it runs in YOUR accounts, on YOUR
  keys, and nothing phones home to anyone.
