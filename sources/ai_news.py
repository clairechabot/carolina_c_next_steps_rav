"""AI-for-the-workplace reading: RSS feeds curated for a professional
staying current on AI, not for engineers. Verified reachable 2026-08.

Both feed lists (AI reading + regional business news for the Sunday
"networking radar") live in client/config.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import feedparser

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from client import config as cfg  # noqa: E402
from http_fetch import fetch  # noqa: E402

AI_FEEDS = cfg.AI_FEEDS
REGIONAL_BUSINESS_FEEDS = cfg.REGIONAL_BUSINESS_FEEDS


def _fetch_feed(name: str, url: str, limit: int) -> list[dict]:
    resp = fetch(url, timeout=30, retries=2)
    parsed = feedparser.parse(resp.content)
    items = []
    for entry in parsed.entries[:limit]:
        items.append({
            "feed": name,
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "summary": (entry.get("summary", "") or "")[:500],
            "published": entry.get("published", ""),
        })
    return items


def fetch_articles(feeds: list[tuple[str, str]] | None = None,
                   limit_per_feed: int = 10) -> tuple[list[dict], dict]:
    """Returns (articles, per-feed status dict)."""
    articles, status = [], {}
    for name, url in (feeds or AI_FEEDS):
        try:
            items = _fetch_feed(name, url, limit_per_feed)
            articles.extend(items)
            status[name] = f"ok ({len(items)})"
        except Exception as e:  # noqa: BLE001 — boundary: external feeds
            status[name] = f"unavailable: {type(e).__name__}"
    return articles, status
