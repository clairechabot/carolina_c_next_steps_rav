# Step 12 — Running several clients from one template (operators)

*For an operator who sets this up for more than one job seeker. Skip it
if you are building your own.*

## One repo per client, this template as upstream

Every client gets **their own repository created from this template**.
Not a branch: GitHub only fires `schedule:` workflows on a repo's default
branch, and secrets, variables and Pages are per repository. A branch
per client would never send an evening email.

What makes this cheap is that a client repo differs from the template in
a handful of files only:

| Path | What |
|---|---|
| `client/config.py` | the search definition: tiers, title gate, Job-Room keywords, LinkedIn and Adzuna searches, recruiter watch, news feeds, interview-brief persona |
| `profile/candidate.md` | the public scoring profile |
| `claude-project/instructions.md` and `claude-project/knowledge/` | the coach |

Everything else, the code and workflows, is identical in every client
repo. So a template improvement flows to each client with one merge.

## Setting up a client

1. Prepare their bundle in the template repo under `clients/<name>/`
   (mirror the three paths above; a README with the secrets checklist).
   The CUSTOMIZE.md interview produces exactly these files; keep the
   private profile and private knowledge copies out of git.
2. On the template repo, tick **Settings → General → Template
   repository** once. From then on **Use this template → Create a new
   repository** appears on the repo page.
3. In the new client repo:

   ```
   python tools/apply_client.py <name>
   git add -A && git commit -m "Client setup: <name>" && git push
   git remote add upstream https://github.com/<you>/next-chapter-rav-template.git
   ```

   The script copies the bundle into place and deletes `clients/` so no
   client repo carries another client's data.
4. Steps 3, 4, 5, 7, 8 and 11 as usual: secrets, Pages, first run, the
   Claude Project, the tracker sheet, the RAV variable.

## Pushing a template update to every client

In each client repo:

```
git fetch upstream
git merge upstream/main
git push
```

Conflicts only arise in the three client-owned paths, which the template
should not be changing, or in the state files the nightly run commits
(`history.json`, `pending_jobs.json`, `editions/`, `docs/`). For those,
keep the client's side (`git checkout --ours -- history.json
pending_jobs.json editions docs`) and commit. A small sync workflow in
each client repo can automate the merge; run it after quiet hours so it
does not race the evening edition's own commit.

## Where the private material lives

Per client, the operator keeps outside git: the private profile
(`CANDIDATE_PROFILE` secret text), `target-private.md` and
`master-cv-private.md` for the Claude Project. A private client repo is
recommended; the Evening Edition workflow can publish the rendered pages
to a separate small public repo (`EDITION_REPO`, `EDITION_DEPLOY_TOKEN`)
when Pages on a private repo is not available.
