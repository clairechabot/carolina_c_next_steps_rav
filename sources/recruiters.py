"""Recruiter / executive-search listings - best-effort anchor scrapes of
the firms on the client's shortlist, filtered by a title regex.

Specialist seats often go through these firms before (or instead of)
public boards. Each firm gets a best-effort anchor scrape; per-firm
failures degrade gracefully via fetch.py.

RECRUITER_SCRAPED_FIRMS ships EMPTY in the template config: most Swiss
recruiter sites render listings client-side or sit behind search forms, so
scraping them is per-firm work. The web edition's "Recruiter watch" panel
(RECRUITER_WATCH in client/config.py) covers the shortlist as one-click
outreach targets instead; add scraped entries only after verifying a
firm's listing page serves plain HTML links.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from client import config as cfg  # noqa: E402
from http_fetch import fetch_with_proxy_fallback  # noqa: E402

# (name, listing url, default location, tier_hint) - tier_hint 0 = no hint:
# out-of-area unless the title itself carries a tierable region. Lives in
# client/config.py; ships empty in the template (see module docstring).
FIRMS = cfg.RECRUITER_SCRAPED_FIRMS

TITLE_FILTER = cfg.RECRUITER_TITLE

# Anchors that are navigation/marketing, not postings. Careful with broad
# words: "services" here once killed TrueNorth's "Healthcare Services" CFO
# mandates - URL-shaped patterns only for anything that can appear in a
# legitimate title. "-cfo-search/" hits CFO Search Inc's city marketing
# pages (/los-angeles-cfo-search/) but not its domain or /cfo-jobs/ links.
NAV_NOISE = re.compile(
    r"(submit|alert|sign.?up|resume|about|contact|home|privacy|linkedin"
    r"|facebook|instagram|blog|salary|job.?description|when.to.hire"
    r"|headhunters|executive-search|recruiters|interim-cfo-services"
    r"|-cfo-search/|/advice/|recruitment-expertise|case-stud|/blogs?/"
    r"|press-release|/news/)", re.I)


def _scrape_firm(name: str, listing_url: str, location: str,
                 tier_hint: int) -> list[dict]:
    resp = fetch_with_proxy_fallback(listing_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs, seen = [], set()
    for a in soup.find_all("a", href=True):
        text = " ".join(a.stripped_strings)
        href = a["href"]
        if (not text or len(text) < 6 or len(text) > 120
                or NAV_NOISE.search(text) or NAV_NOISE.search(href)):
            continue
        if not TITLE_FILTER.search(text):
            continue
        url = urljoin(listing_url, href)
        if url in seen or url.rstrip("/") == listing_url.rstrip("/"):
            continue
        seen.add(url)
        job = {
            "source": f"{name} (recruiter)",
            "title": text,
            "company": f"via {name}",
            "location": location,
            "url": url,
            "date_posted": "",
            "salary": "",
            "snippet": "",
        }
        if tier_hint:
            job["tier_hint"] = tier_hint
        jobs.append(job)
    return jobs


def fetch_jobs() -> list[dict]:
    """One combined source; individual firm failures are tolerated here so a
    single 404 doesn't hide the other firms."""
    jobs, failures = [], []
    for name, url, location, hint in FIRMS:
        try:
            jobs.extend(_scrape_firm(name, url, location, hint))
        except Exception as e:  # noqa: BLE001 - boundary: external sites
            failures.append(f"{name}: {type(e).__name__}")
    if failures and not jobs:
        raise RuntimeError("; ".join(failures))
    if failures:
        print(f"[recruiters] partial: {'; '.join(failures)}", flush=True)
    return jobs
