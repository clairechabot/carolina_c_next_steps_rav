# Step 5 — First run + delivery time (15 min)

## Fire a run right now

1. Repo → **Actions** tab → **Evening Edition** (left sidebar) → **Run
   workflow** → green **Run workflow** button. Manual runs send
   immediately — no waiting for evening.
2. Watch it turn green (3–10 minutes), then check the `EMAIL_TO` inbox
   and click through to the web edition.
3. **Red instead of green?** Click the run → the failed step → copy the
   last ~20 lines → paste into Claude with "this is from my Next Chapter
   setup, what's wrong?". It's almost always a typo'd secret.

You're now looking at the EXAMPLE search (finance roles, Zurich-region
cantons, via Job-Room + LinkedIn). Step 6 replaces it with the real one.

## Set the delivery time

The schedule lives in `.github/workflows/digest_pm.yml`: two UTC cron
lines (one per daylight-saving season) with a guard, plus a hold step that
releases the email at the target local hour. The file's comments explain
the pattern. Easiest path: ask Claude —

> Here is my digest_pm.yml. I want the email delivered at 6:30pm in
> [your city]. Give me the exact cron lines, guard offsets, and hold time.

(Or let [Step 6](06-personalize-with-claude.md)'s interview handle it —
it asks for your timezone.)

A silent morning scan also runs daily (banks new postings; no email, no
cost) — `.github/workflows/digest_am.yml`, timing barely matters.

Next: [Step 6 — Personalize it with Claude](06-personalize-with-claude.md)
