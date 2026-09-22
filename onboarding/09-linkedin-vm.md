# Step 9 (optional) — The LinkedIn VM (~$12/month, 1–2 hours)

A small always-on server (DigitalOcean droplet) registered as a GitHub
Actions runner. It adds:

- **Authenticated LinkedIn job scans** (richer results than the free guest
  layer) with **"Meet the hiring team"** extraction — the edition shows
  who to contact.
- The **tracker's LinkedIn feed** (Step 8): the job seeker's Applied list
  and recruiter replies, read-only.
- Recovery of job boards that block GitHub's servers.

Full walkthrough with every terminal command (written for someone who has
never used a terminal): **[VM-SETUP.md](../VM-SETUP.md)**.

**Read first — honest trade-off**: automated LinkedIn access is against
LinkedIn's terms of service. The scripts are deliberately gentle (a few
searches nightly, human pacing, own-data reads only for the tracker), but
the logged-in account carries a small restriction risk. Decide whose
account logs in accordingly — everything else in this template works
without this step.

Next: [Step 10 — privacy + troubleshooting](10-privacy-and-troubleshooting.md)
