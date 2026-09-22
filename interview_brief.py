"""On-demand interview prep brief: give it a company name, get a one-pager
emailed to your dad (pattern borrowed from the Ellipsis meeting-prep-brief).

Fetches the company website when provided, then has Claude assemble what a
CFO candidate needs before an interview. Facts the model is not sure of are
marked [VERIFY] rather than invented.

Usage:  python interview_brief.py --company "IMP Group" [--website https://impgroup.com] [--role "VP Finance"]
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from render import send_email

HERE = Path(__file__).parent
PROFILE_FILE = HERE / "profile" / "candidate.md"
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")

sys.path.insert(0, str(HERE))
from client import config as cfg  # noqa: E402

BRIEF_SYSTEM = f"""\
You prepare interview one-pagers for {cfg.INTERVIEW_BRIEF_PERSONA}. Produce
clean HTML (no <html>/<body> wrapper, inline styles only, email-safe
tables ok) with these sections:

1. The company in five bullets (what they do, scale, ownership, recent news)
2. Their finance picture (what this seat would inherit; funding/margins
   if known)
3. Likely interview themes for this seat, with a suggested angle for THIS
   candidate drawing on their background (see the attached profile)
4. Five sharp questions they can ask the interviewers
5. One paragraph: how to address the employment gap / current job-search
   situation for this specific company, framed as readiness rather than
   apology

Mark anything you are not confident about as [VERIFY] instead of guessing.
Use ASCII hyphens, never em-dashes."""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--website", default="")
    parser.add_argument("--role", default=cfg.INTERVIEW_BRIEF_DEFAULT_ROLE)
    args = parser.parse_args()

    if not os.environ.get("CLAUDE_API_KEY"):
        sys.exit("ERROR: CLAUDE_API_KEY required for interview briefs")

    website_text = ""
    if args.website:
        try:
            from bs4 import BeautifulSoup
            from http_fetch import fetch
            soup = BeautifulSoup(fetch(args.website).text, "html.parser")
            website_text = " ".join(soup.get_text(" ").split())[:6000]
        except Exception as e:  # noqa: BLE001 — boundary: external site
            website_text = f"(website fetch failed: {e})"

    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=BRIEF_SYSTEM,
        messages=[{"role": "user", "content":
                   f"CANDIDATE PROFILE:\n{PROFILE_FILE.read_text(encoding='utf-8')}\n\n"
                   f"COMPANY: {args.company}\nROLE: {args.role}\n"
                   f"WEBSITE TEXT (may be empty):\n{website_text}"}],
    )
    if response.stop_reason == "refusal":
        sys.exit("ERROR: model refused the request")
    brief_html = next((b.text for b in response.content if b.type == "text"), "")

    now = datetime.datetime.now(ZoneInfo("Europe/Zurich"))
    body = (f'<div style="font-family:Georgia,serif;max-width:640px;'
            f'margin:0 auto;padding:20px;color:#1f2937;">{brief_html}</div>')
    subject = f"Interview brief: {args.company} ({now:%b %-d})"
    (HERE / "newsletter.html").write_text(body, encoding="utf-8")
    if os.environ.get("ALLOW_NO_EMAIL") == "1":
        print(f"[brief] wrote newsletter.html ({subject}); send skipped")
    else:
        send_email(body, subject)


if __name__ == "__main__":
    main()
