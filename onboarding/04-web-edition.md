# Step 4 — Turn on the web edition (10 min)

The email is deliberately short; the full edition (every scored job,
Claude prompts, the searchable Grove archive) is a website GitHub hosts
free.

1. Repo → **Settings → Pages** → under "Build and deployment":
   Source = **Deploy from a branch**, Branch = **main**, folder =
   **/docs** → Save.
2. Wait a minute, refresh: the page shows your URL, like
   `https://YOURNAME.github.io/next-chapter-mine/`.
3. Put that URL into the `EDITION_URL` **variable** (Step 3 table).
   Without it the email simply has no buttons; with it, "Read the full
   edition" works.
4. Know what this means: the pages ask search engines not to index them
   (`noindex`), but on a public repo **anyone with the URL can read the
   edition**. That's why it never contains more than a first name and job
   preferences.

The site will be empty until the first run builds it — next step.

Next: [Step 5 — First run](05-first-run.md)
