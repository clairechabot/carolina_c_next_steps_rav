# Step 6 — Personalize it with Claude (45 min, the fun part)

Open **[CUSTOMIZE.md](../CUSTOMIZE.md)** — the whole step lives there. In
short: you paste one big prompt into Claude, attach the job seeker's
resume, answer an interview (target titles, location tiers, salary
floors, dealbreakers, recruiters, timezone), and Claude produces
replacement contents for every personal file — the search definition in
`client/config.py`, the scoring profile, the coach knowledge. No other
code file changes, so later template updates merge cleanly.

Two ways to apply what Claude produces:

- **Easiest (no tools)**: edit files on github.com — open a file, pencil
  icon, paste, **Commit changes**.
- **Best**: install **Claude Code** (claude.com/claude-code), open it in a
  clone of your repo, paste the CUSTOMIZE.md prompt — it edits every file
  itself and you just review.

Don't forget the **private half**: the interview produces a private
profile with real salary floors — that text goes into the
`CANDIDATE_PROFILE` **secret** (Step 3 table), never into a committed
file.

After personalizing, fire another manual run (Step 5) and check the
edition now hunts YOUR jobs.

Next: [Step 7 — The Claude Project coach](07-claude-project-coach.md)
