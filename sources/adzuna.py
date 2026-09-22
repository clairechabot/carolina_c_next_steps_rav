"""Adzuna job-search API (free tier) — aggregates many boards incl. Indeed.

Optional: requires ADZUNA_APP_ID + ADZUNA_APP_KEY (free at
developer.adzuna.com). Without keys the source is skipped cleanly.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from client import config as cfg  # noqa: E402
from http_fetch import fetch  # noqa: E402

API = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"

# (country, query) - Adzuna operates a Swiss index (country code "ch").
QUERIES = cfg.ADZUNA_QUERIES


# Adzuna reports salaries in the index's local currency; the scorer's
# salary-floor rule needs the right unit, never a hard-coded "$".
CURRENCY = {"ch": "CHF", "de": "EUR", "at": "EUR", "nl": "EUR", "be": "EUR",
            "fr": "EUR", "it": "EUR", "es": "EUR", "gb": "GBP", "us": "USD",
            "ca": "CAD", "au": "AUD", "nz": "NZD", "sg": "SGD", "pl": "PLN",
            "za": "ZAR", "in": "INR", "br": "BRL", "mx": "MXN"}


class MissingKeys(RuntimeError):
    pass


def fetch_jobs() -> list[dict]:
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise MissingKeys("ADZUNA_APP_ID / ADZUNA_APP_KEY not set (optional source)")
    jobs = []
    for country, query in QUERIES:
        params = {"app_id": app_id, "app_key": app_key,
                  "results_per_page": 30, "max_days_old": 14,
                  "sort_by": "date", **query}
        data = fetch(API.format(country=country), params=params).json()
        for item in data.get("results", []):
            jobs.append({
                "source": "Adzuna",
                "title": item.get("title", ""),
                "company": (item.get("company") or {}).get("display_name", ""),
                "location": (item.get("location") or {}).get("display_name", ""),
                "url": item.get("redirect_url", ""),
                "date_posted": (item.get("created") or "")[:10],
                "salary": (f"{item['salary_min']:,.0f}-{item['salary_max']:,.0f} "
                           f"{CURRENCY.get(country, country.upper())}"
                           if item.get("salary_min") and item.get("salary_max") else ""),
                "snippet": (item.get("description") or "")[:300],
            })
    return jobs
