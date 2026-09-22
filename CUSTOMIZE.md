# Customize it with Claude — the guided interview

You don't edit this template by hand. You paste the prompt below into
Claude, answer its questions, and it produces every personalized file.

**Where to paste it:**

- **Best: Claude Code** opened in your copy of this repo — it edits the
  files directly. (Install: claude.com/claude-code. In a terminal:
  `cd` into the repo folder, run `claude`, paste the prompt.)
- **Also fine: claude.ai** — attach the job seeker's resume, paste the
  prompt, and Claude outputs each file's full contents for you to
  copy-paste into GitHub's web editor (open file → pencil icon → paste →
  Commit changes).

---

Copy everything below the line into Claude, and attach the resume.

---

You are customizing "The Next Chapter: RAV edition" — a Swiss job-search
newsletter + Claude-Project career coach + RAV proof-of-efforts template —
for a specific job seeker registered with a Swiss RAV. The repository
you're working in (or that I'll paste files from) contains a fully working
EXAMPLE search for a finance professional in the Zurich region. Your job:
interview me, then replace every example-specific piece with this job
seeker's real search.

One rule overrides everything else: the system documents REAL applications
only. Never add, suggest, or configure anything that fabricates an effort
record, auto-sends an application, or logs an application that was not
actually sent. Preserve every guardrail that enforces this.

**Step 1 — Interview me.** Ask, in small batches, and wait for answers:

1. The job seeker's first name, and the name they'd like the newsletter
   persona to greet them by.
2. Their target roles: the exact titles they'd apply to, plus your own
   suggestions for same-level synonyms and one-notch-down titles worth
   surfacing (present your proposed full title universe for approval).
3. Location priorities as ordered tiers (e.g. "1: home city and region,
   2: rest of Switzerland, 3: remote, 4: neighboring countries"),
   including any explicit exclusions, and which CANTONS to search on
   Job-Room (two-letter codes; empty = all of Switzerland).
4. Salary floors by region, and whether they only apply when a posting
   states compensation. (These go ONLY in private copies.)
5. Industry preferences, dealbreakers (restricted-hiring situations,
   sectors they won't touch, travel limits), and any "wildcard" bets
   (specific companies expanding locally, fractional/interim work,
   internal transfers).
6. Their preferred email delivery hour (timezone is Europe/Zurich
   throughout unless they say otherwise).
6b. **The RAV specifics** (this edition's reason to exist): their canton
   and RAV office; the monthly application quota their advisor set
   (usually 10-12 — this becomes the `RAV_MONTHLY_TARGET` repo variable);
   the proof format their RAV accepts (the standard paper/PDF form,
   entry in the Job-Room portal, or a cantonal portal) and the monthly
   submission deadline day; the minimum workload percentage worth
   applying to (`WORKLOAD_MIN`); which languages they can apply in
   (affects Job-Room keywords — search in German AND English when they
   can apply in both).
7. Names of local/specialist recruiters they'd want watched (offer to
   research the region's executive-search firms if they don't know).
8. Career facts for the coach: paste or attach the resume; ask for their
   2–4 proudest quantified achievements, and for a paragraph or an old
   cover letter written in their own voice.

**Step 2 — Produce the files.** Generate complete replacement contents
for each of the following (if you are Claude Code, edit them in place;
otherwise output each in its own code block, clearly labeled):

- `profile/candidate.md` — the PUBLIC scoring profile: role universe,
  location tiers, scoring guidance, wildcards. Keep exact salary numbers
  OUT (write "floors live in the private profile"); keep personal contact
  data OUT.
- **The private profile** (not committed!) — same document with the real
  salary floors filled in. Tell me to paste it into the GitHub secret
  `CANDIDATE_PROFILE`.
- `claude-project/instructions.md` — the Vern coach persona, with the job
  seeker's real career summary woven into the opening, their level and
  market realities in the ageism/bias playbook section (adapt it: the
  template's version addresses age bias; adjust to whatever this job
  seeker actually faces), all coaching modes preserved (blunt Fit check,
  Interview prep, CV tailoring, Applications, Email & outreach,
  Negotiation, Weekly review), and the "AI tells" writing bans kept
  verbatim.
- `claude-project/knowledge/`: `master-cv.md` (structured from the
  resume), `achievements.md` (STAR-format story bank), `target.md` (tiers,
  roles, floors marked private), `voice-sample.md` (their real writing
  sample + what to imitate about it), `home-market.md` (their target
  region: key employers, the recruiter list, networking venues).
- `client/config.py` — THE search definition, and the only code file
  that changes per client (no other .py file is edited; that is what
  keeps template updates mergeable across client repos). Rebuild every
  block for this job seeker:
  - `HOME_REGION`, `TIER_LABELS`, `TIER_PATTERNS` (regexes evaluated in
    order; first match wins; no match = out of area) and
    `REGION_SOURCES` for their geography.
  - `TITLE_PASS`, `TITLE_BLOCK`, `WILDCARD` for their title universe
    (block wins over pass; wildcard only flags).
  - `JOBROOM_KEYWORDS` (their field's search terms, in every language
    the ads come in), `JOBROOM_CANTONS` (two-letter codes, or [] for all
    of Switzerland), `JOBROOM_WORKLOAD_MIN`. Job-Room is source #1 — the
    official board's ads carry the RAV form fields (address, workload,
    apply channel).
  - `LINKEDIN_GUEST_SEARCHES`, `LINKEDIN_AUTH_SEARCHES`,
    `ADZUNA_QUERIES` for their titles + regions (Adzuna "ch" first; add
    other country indexes only for tier-4 geographies).
  - `RECRUITER_WATCH` (watch panel, links only) and
    `RECRUITER_SCRAPED_FIRMS` + `RECRUITER_TITLE` (only firms whose
    listing page serves plain HTML links; verify before adding),
    `RECRUITER_WATCH_TITLE`, `RECRUITER_WATCH_BLURB`.
  - `AI_FEEDS` and `REGIONAL_BUSINESS_FEEDS`: RSS for their field and
    region; verify each URL returns items.
  - `INTERVIEW_BRIEF_PERSONA`, `INTERVIEW_BRIEF_DEFAULT_ROLE`.
- `.github/workflows/digest_pm.yml`: ONLY if the delivery hour changes
  (the CET/CEST cron pair + season guard are already Swiss; preserve the
  pattern exactly).
  - The repo variable list: include `RAV_MONTHLY_TARGET` from question
    6b, and mention the RAV Form workflow's schedule relative to their
    canton's submission deadline (move the cron earlier if their
    deadline is the 3rd or sooner).
- A filled list of what to put in each GitHub secret/variable (from
  onboarding/03-secrets-and-variables.md), with the private-profile text ready to
  paste.
- If you are an operator running several clients: write the files above
  into `clients/<name>/` (mirroring `client/`, `profile/`,
  `claude-project/`) plus a README with that secrets list, so
  `tools/apply_client.py <name>` can stamp them into the client's own
  repo. See onboarding/12-multi-client.md.

**Step 3 — Verify with me.** Give me: (a) three example job postings and
how the new gate/tiers would treat each, so I can sanity-check; (b) a
checklist of anything you could not do from here that I must do by hand.

Ground rules: never invent career facts — everything about the job seeker
comes from the resume and my answers; ask when something's missing. Keep
Vern's voice (measured, literate, no exclamation marks, no em-dashes) and
all of the template's safety behaviors (salary-floor hard rule,
restricted-hiring rule, never-repeat history, graceful source failures,
and the real-records-only rule of the RAV layer) exactly as they are.
Adapt the coach persona's bias playbook to this job seeker's actual
situation — for an RAV-registered candidate that usually means an
unemployment-gap / structured-search playbook rather than the template's
age-bias one.
