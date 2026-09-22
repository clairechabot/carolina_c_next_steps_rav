"""THE per-client search configuration - the one code file that differs
between clients.

Everything the CUSTOMIZE.md interview used to scatter across curate.py,
fetch.py, sources/*.py, linkedin_authenticated.py, webpage.py and
interview_brief.py now lives here, so a client repo differs from the
template in a handful of files only:

    client/config.py            <- this file (search definition)
    profile/candidate.md        <- the public scoring profile
    claude-project/             <- the coach's instructions + knowledge

The code never changes per client. That is what lets one template update
flow to every client repo with a plain upstream merge (see
onboarding/12-multi-client.md).

This copy is the WORKING EXAMPLE: a finance professional in the Zurich
region. Private data (salary floors, contact details) never goes here -
it lives in the CANDIDATE_PROFILE secret and the private Claude Project.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------
# Label of tier 1, shown in the email/edition mastheads ("N in the <HOME_REGION>")
HOME_REGION = "Zurich region"

TIER_LABELS = {1: "Zürich region", 2: "Switzerland", 3: "Remote",
               4: "DACH / EU", 0: "Out of area"}

# Evaluated in order against "<location> <title>"; first match wins.
# Tier 0 (no match) = out of area, rejected by the gate.
TIER_PATTERNS = [
    (1, re.compile(r"\b(ZH|Z[uü]rich|Zurich|Winterthur|Zug|ZG|Baden|Aargau"
                   r"|AG)\b", re.I)),
    (3, re.compile(r"\b(remote|home ?office|telework|anywhere)\b", re.I)),
    (2, re.compile(r"\b(Switzerland|Schweiz|Suisse|Svizzera|CH|Basel"
                   r"|Bern|Gen[eè]ve|Geneva|Lausanne|Luzern|Lucerne"
                   r"|St\.? ?Gallen|SG|Lugano|Winterthur|Thun|Chur"
                   r"|Fribourg|Neuch[aâ]tel|Sion|Schaffhausen)\b", re.I)),
    (4, re.compile(r"\b(Germany|Deutschland|Austria|[ÖO]sterreich|M[uü]nchen"
                   r"|Munich|Frankfurt|Stuttgart|Wien|Vienna|Liechtenstein"
                   r"|Vaduz|Konstanz|Freiburg)\b", re.I)),
]

# Sources whose entire catchment is the home region: forced to tier 1 when
# the location text is vague. Job-Room ads carry city + canton, so this
# ships empty.
REGION_SOURCES: set[str] = set()

# ---------------------------------------------------------------------------
# Title gate (stage 1, free): block wins, then pass, then wildcard flag
# ---------------------------------------------------------------------------
TITLE_PASS = re.compile(
    r"(controller|controlling|finance manager|finanzmanager"
    r"|head of finance|head of accounting|finance lead"
    r"|leiter(in)?,? ?(finanzen|rechnungswesen|controlling)"
    r"|leitung (finanzen|rechnungswesen|controlling)"
    r"|finanzverantwortlich|finance business partner"
    r"|accounting manager|senior accountant|hauptbuchhalter"
    r"|finanzchef|treuhand|responsable finances|finance officer"
    r"|cfo|chief financial|treasur|comptable senior"
    r"|chef comptable)", re.I)

TITLE_BLOCK = re.compile(
    r"\b(junior|intern(ship)?|praktik(um|ant)|lehrstelle|lehrling|trainee"
    r"|werkstudent|aushilfe|sachbearbeiter|assistent|assistant|clerk"
    r"|payroll|lohnbuchhalt|debitoren|kreditoren|cook|server|cashier"
    r"|driver|technician|coordinator)\b", re.I)

WILDCARD = re.compile(r"\b(interim|fractional|mutterschaftsvertretung"
                      r"|maternity cover|gemeinde|stadtverwaltung|stiftung"
                      r"|ngo|non[- ]?profit)\b", re.I)

# ---------------------------------------------------------------------------
# Job-Room (arbeit.swiss) - source #1 of the RAV edition
# ---------------------------------------------------------------------------
JOBROOM_KEYWORDS = ["finance", "controller", "accounting"]
JOBROOM_CANTONS = ["ZH", "ZG", "AG", "SG"]   # [] = all of Switzerland
JOBROOM_WORKLOAD_MIN = 60                     # percent

# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------
# Guest endpoint: (keywords, location, f_WT) - f_WT="2" = remote only.
LINKEDIN_GUEST_SEARCHES = [
    ("finance manager OR controller OR \"head of finance\"", "Zurich, Switzerland", None),
    ("\"finance director\" OR CFO", "Zurich, Switzerland", None),
    ("finance manager OR controller", "Switzerland", "2"),
]

# Authenticated VM scan: (keywords, location, remote_only)
LINKEDIN_AUTH_SEARCHES = [
    ("finance manager OR controller OR \"head of finance\"", "Zurich, Switzerland", False),
    ("\"finance director\" OR CFO", "Switzerland", False),
    ("finance manager OR controller", "Switzerland", True),
]

# ---------------------------------------------------------------------------
# Adzuna (optional): (country, query params). Country stays "ch".
# ---------------------------------------------------------------------------
ADZUNA_QUERIES = [
    ("ch", {"what_or": "controller \"finance manager\" \"head of finance\" accountant treasury",
            "where": "Zurich", "distance": 50}),
    ("ch", {"what_or": "controller \"finance manager\" \"head of finance\"",
            "what_and": "remote"}),
    ("ch", {"what_or": "controller \"finanzverantwortliche\" buchhaltung"}),
]

# ---------------------------------------------------------------------------
# Recruiters
# ---------------------------------------------------------------------------
# Scraped firms: (name, listing url, default location, tier_hint). Only
# firms whose listing page serves plain HTML links belong here; most Swiss
# recruiter sites render client-side, so this often stays empty.
RECRUITER_SCRAPED_FIRMS: list[tuple[str, str, str, int]] = []

# Title filter applied to scraped recruiter anchors.
RECRUITER_TITLE = re.compile(
    r"\b(cfo|chief financial|finance|financial|controller|contr[oô]leur"
    r"|treasurer|treasury|accounting|fp&a|vp finance|directeur financier"
    r"|cao\b|chief administrative)\b", re.I)

# Watch panel in the web edition: (name, where/specialty, url). Links only.
RECRUITER_WATCH = [
    ("Michael Page Switzerland", "Zürich · multi-discipline",
     "https://www.michaelpage.ch/en/jobs"),
    ("Robert Walters Switzerland", "Zürich · professional services",
     "https://www.robertwalters.ch/en/jobs.html"),
    ("Hays Switzerland", "Zürich · contracting + permanent",
     "https://www.hays.ch/en/jobsearch"),
    ("Swisslinx", "Zürich · financial services",
     "https://www.swisslinx.com/en/jobs"),
    ("Nicoll Curtin", "Zürich · technology",
     "https://www.nicollcurtin.com/jobs"),
]
RECRUITER_WATCH_TITLE = "Recruiter watch — Switzerland"
RECRUITER_WATCH_BLURB = ("Finance postings from this firm appear in the job "
                         "sections automatically when they match.")

# ---------------------------------------------------------------------------
# Reading: (name, RSS url). AI_FEEDS power "AI for the workplace";
# REGIONAL_BUSINESS_FEEDS power the Sunday networking radar.
# ---------------------------------------------------------------------------
AI_FEEDS = [
    ("CFO Dive", "https://www.cfodive.com/feeds/news/"),
    ("MIT Sloan Management Review", "https://sloanreview.mit.edu/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("Harvard Business Review", "https://feeds.hbr.org/harvardbusiness"),
]

REGIONAL_BUSINESS_FEEDS = [
    ("Startupticker.ch", "https://www.startupticker.ch/en/rss/news"),
    ("Moneycab", "https://www.moneycab.com/feed/"),
    ("Finews.com", "https://www.finews.com/news/english-news?format=feed"),
]

# ---------------------------------------------------------------------------
# Interview brief: one line describing the candidate for the brief writer.
# ---------------------------------------------------------------------------
INTERVIEW_BRIEF_PERSONA = ("a finance professional interviewing for "
                           "controller/finance-manager seats in the Zurich "
                           "region")
INTERVIEW_BRIEF_DEFAULT_ROLE = "senior finance leadership role"
