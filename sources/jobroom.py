"""Job-Room (job-room.ch / arbeit.swiss) - the OFFICIAL Swiss public
employment service job board, run by SECO. Source #1 for the RAV edition:

- Applying to ads on the state's own board is unimpeachable proof of
  effort for the RAV.
- The public search API is JSON and rich: it returns the employer's FULL
  POSTAL ADDRESS, the workload percentage, and the apply channel - the
  exact fields the monthly "Nachweis persoenlicher Arbeitsbemuehungen"
  form asks for, which email-based detection can never recover. These
  ride along on each job (address / workload / method) into the pending
  pool, the Save-button payload, and the tracker sheet.
- It also syndicates ads from the big private boards (jobup.ch /
  jobs.ch), so it aggregates much of the Swiss market in one call.

KEYWORDS, CANTONS and WORKLOAD_MIN come from client/config.py. Verified
live 2026-08-31 with the example config: 61 finance ads in ZH over 7 days.
"""
from __future__ import annotations

import html as html_mod
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from client import config as cfg  # noqa: E402

API = ("https://www.job-room.ch/jobadservice/api/jobAdvertisements/_search"
       "?page={page}&size=60&sort=date_desc")
DETAIL = "https://www.job-room.ch/job-search/{ad_id}"

KEYWORDS = cfg.JOBROOM_KEYWORDS
CANTONS = cfg.JOBROOM_CANTONS         # [] = all of Switzerland
WORKLOAD_MIN = cfg.JOBROOM_WORKLOAD_MIN
ONLINE_SINCE_DAYS = 3                 # nightly window; dedup handles overlap

# Preferred description language order for the title we show.
LANG_ORDER = ["en", "de", "fr", "it"]


def _clean(text: str) -> str:
    """Job-Room titles/descriptions arrive with HTML entities and tags
    (&amp;, &nbsp;, <em> around matched keywords) - strip both."""
    text = html_mod.unescape(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.replace("\u00a0", " ").split())


def _best_description(descriptions: list[dict]) -> dict:
    by_lang = {d.get("languageIsoCode"): d for d in descriptions if d}
    for lang in LANG_ORDER:
        if lang in by_lang:
            return by_lang[lang]
    return descriptions[0] if descriptions else {}


def _address(company: dict) -> str:
    bits = [" ".join(b for b in (company.get("street"),
                                 company.get("houseNumber")) if b),
            " ".join(b for b in (company.get("postalCode"),
                                 company.get("city")) if b)]
    return ", ".join(b for b in bits if b)


def fetch_jobs() -> list[dict]:
    jobs = []
    for keyword in KEYWORDS:
        resp = requests.post(
            API.format(page=0),
            json={"workloadPercentageMin": WORKLOAD_MIN,
                  "workloadPercentageMax": 100,
                  "onlineSince": ONLINE_SINCE_DAYS,
                  "displayRestricted": False,
                  "keywords": [keyword],
                  "professionCodes": [],
                  "communalCodes": [],
                  "cantonCodes": CANTONS},
            headers={"Content-Type": "application/json"},
            timeout=40)
        resp.raise_for_status()
        for item in resp.json():
            ad = item.get("jobAdvertisement", item)
            content = ad.get("jobContent", {})
            desc = _best_description(content.get("jobDescriptions", []))
            company = content.get("company") or {}
            location = content.get("location") or {}
            employment = content.get("employment") or {}
            apply_channel = content.get("applyChannel") or {}
            wl_min = employment.get("workloadPercentageMin")
            wl_max = employment.get("workloadPercentageMax")
            workload = (f"{wl_min}-{wl_max}%" if wl_min != wl_max
                        else f"{wl_max}%") if wl_max else ""
            method = ("Online form" if apply_channel.get("formUrl")
                      else "Email" if apply_channel.get("emailAddress")
                      else "Post" if apply_channel.get("postAddress")
                      or apply_channel.get("rawPostAddress") else "")
            loc = ", ".join(b for b in (location.get("city"),
                                        location.get("cantonCode")) if b)
            jobs.append({
                "source": "Job-Room (arbeit.swiss)",
                "title": _clean(desc.get("title") or ""),
                "company": company.get("name", ""),
                "location": loc or "Switzerland",
                "url": DETAIL.format(ad_id=ad.get("id", "")),
                "date_posted": (ad.get("publication", {}) or {}).get(
                    "startDate", "") or "",
                "salary": "",
                "snippet": _clean(desc.get("description") or "")[:300],
                # RAV form fields - carried through to the tracker.
                "address": _address(company),
                "workload": workload,
                "method": method,
            })
    # Dedup across keyword queries by ad URL.
    seen, unique = set(), []
    for j in jobs:
        if j["url"] in seen or not j["title"]:
            continue
        seen.add(j["url"])
        unique.append(j)
    return unique
