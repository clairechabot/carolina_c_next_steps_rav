"""Curation: free regex gate -> Vern (Claude) scores against
profile/candidate.md with location tiers, salary floors, title-level rules;
writes per-job summary + why + watch_out, a "start here" kickoff prompt for
3-5 star jobs, AI-article picks, and Vern's daily note.

Two-stage cost control from Ellipsis Athena's enrichment gate: the regex gate
discards obvious non-fits so the LLM only prices plausible ones. Without
CLAUDE_API_KEY the pipeline still works in gate-only mode (no scores).

Usage:  python curate.py [--edition morning|evening]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).parent
IN_FILE = HERE / "fetched_data.json"
OUT_FILE = HERE / "curated_data.json"
PROFILE_FILE = HERE / "profile" / "candidate.md"
ZURICH = ZoneInfo("Europe/Zurich")

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")

sys.path.insert(0, str(HERE))
from client import config as cfg  # noqa: E402 - per-client search definition

TIER_LABELS = cfg.TIER_LABELS

# ---------------------------------------------------------------------------
# Stage 1: free regex gate. The title universe lives in client/config.py.
# ---------------------------------------------------------------------------
TITLE_PASS = cfg.TITLE_PASS
TITLE_BLOCK = cfg.TITLE_BLOCK
WILDCARD = cfg.WILDCARD


def gate(job: dict) -> bool:
    title = job.get("title", "")
    if TITLE_BLOCK.search(title):
        return False  # block wins: "Assistant Corporate Controller" is out
    if job.get("tier", 0) == 0:
        return False
    if TITLE_PASS.search(title):
        job["wildcard"] = bool(WILDCARD.search(title))
        return True
    return False


# ---------------------------------------------------------------------------
# Stage 2: Vern (Claude) scoring
# ---------------------------------------------------------------------------
SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "summary": {"type": "string"},
                    "why": {"type": "string"},
                    "watch_out": {"type": "string"},
                    "kickoff_prompt": {"type": "string"},
                    "attachments": {"type": "array",
                                    "items": {"type": "string"}},
                },
                "required": ["index", "score", "summary", "why",
                             "watch_out", "kickoff_prompt", "attachments"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["jobs"],
    "additionalProperties": False,
}

PICKS_SCHEMA = {
    "type": "object",
    "properties": {
        "ai_picks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "note": {"type": "string"},
                },
                "required": ["index", "note"],
                "additionalProperties": False,
            },
        },
        "encouragement": {"type": "string"},
        "one_action": {"type": "string"},
    },
    "required": ["ai_picks", "encouragement", "one_action"],
    "additionalProperties": False,
}

SCORER_SYSTEM = """\
You are Vern, the career scout for one specific candidate. The candidate
profile below is your only source of truth about them - never invent facts.
Apply its location tiers, title universe, and salary rule exactly.

Scoring scale:
5 = apply today: the profile's core titles, tier 1-2 location (or great
    remote), right scope and language
4 = strong fit, minor mismatch (tier 3-4 location, sector stretch, or a
    notch-down title with real scope)
3 = worth a look: plausibly right, needs the candidate's judgment
2 = weak fit (too junior, wrong region, wrong language)
1 = dealbreaker per profile

HARD RULE - salary floors: the profile's floors are firm. If a posting STATES compensation below the floor for
its region - in the salary field OR anywhere in the description snippet -
score it 1 regardless of everything else, and quote the number in
watch_out. Never rank a below-floor posting as worth an evening. If no
compensation is stated, score normally and say nothing about salary.
(Figures often sit in the description rather than the salary field -
check both.)

HARD RULE - restricted hiring: if the posting states the role is reserved
for, or gives strong preference to, members of a specific community or
group the candidate does not belong to - e.g. citizenship-restricted
government roles, internal-only postings, or reintegration placements -
score it 1 and name the
restriction plainly in watch_out. These are legitimate hiring practices;
they simply mean the seat is not winnable and must not cost an evening.

Per job, write:
- "summary": 1-2 sentences - what this job actually is (from title, company,
  location, description snippet) and how it aligns with the profile,
  calibrated to your score ("Mid-size industrial group, real controlling
  scope - exactly the profile you want" vs "Controller title, bookkeeping
  scope - misaligned").
- "why": 1-2 plain sentences addressed to the candidate ("International
  team, immediate start wanted - your situation is an asset here"). Call
  out stated benefits here.
- "watch_out": one honest caveat or "" (below-floor salary quoted here;
  "title below your level - confirm full P&L" for notch-down titles).
- "kickoff_prompt": ONLY for scores 3-5, else "". A copy-paste-ready prompt
  addressed to Vern in the candidate's Claude Project. It must: (a) name
  the role,
  company and URL; (b) open with "Run a blunt fit check on this posting
  first - pros and cons against my resume, verdict included"; (c) for score
  3, weight toward "tell me if this is worth an evening"; for 4-5, continue
  "then tailor my CV emphasis for this seat, draft a cover letter in my
  own voice (in the ad's language), and suggest one human route in";
  (d) if a hiring
  contact is listed, add "draft a LinkedIn note to <name>, <title>";
  (e) end with: "I'm pasting the posting text below." Keep it under 130
  words, first person, plain text.
- "attachments": ONLY for scores 3-5, else []. The checklist of what he
  the candidate must add to the chat alongside the prompt: 1-3 short
  imperative items ("Paste the full posting text - open the job link and
  copy everything"). Always include the posting text item. Add others only
  when the prompt genuinely needs them (e.g. a company page or contact
  profile worth pasting). The CV and targets already live in the Project
  knowledge, so never list those unless the prompt asks to update them.

No em-dashes anywhere. Return every job you were given, by index."""

PICKS_SYSTEM = """\
You are Vern, curating an "AI for the workplace" section for the candidate
described in the profile excerpt provided. Respect the profile's location
priorities (never frame the home-region choice as a compromise). Pick the
2-3 articles most useful for that reader: AI in their function, AI strategy
leaders in their field are expected to have a view on, adoption in their
industry. Skip model-release hype and engineering deep dives. For each pick write
"note": one sentence on what it means for a professional in the
candidate's target field.

Also write "encouragement": Vern's note at the top of the evening edition,
90-130 words. Vern's character is, quietly, Captain Picard of the
Enterprise: measured, literate, dignified gravitas; a captain addressing a
respected officer, never a cheerleader. The register - not cosplay:
- Complete, unhurried sentences; the occasional classical, literary, or
  seafaring allusion; understatement over exclamation (no exclamation
  marks, ever).
- Deep respect for experience: the career record is a command record,
  not a liability. Duty, patience, and standards are virtues.
- Honest about difficulty the way a captain is: name the long odds calmly,
  then set the course.
- End with ONE concrete order-like action for this week, framed as an
  invitation ("I would suggest...", "Might I recommend..."), and when it
  lands naturally - not every night - close that line with "Make it so."
- Never mention Star Trek, starships, captains, or Picard by name. No
  space metaphors. The personality lives in cadence and bearing only.
- Rotate substance nightly: the value of the operating record, patience
  in a structured search, a networking move, tonight's strongest lead,
  the AI reading as an edge, the steady monthly rhythm as momentum. Do
  NOT reuse the themes or sentence structures of the recent notes
  provided.
No em-dashes anywhere.

Separately, write "one_action": a single sentence for the "Tonight in one
minute" digest - the one concrete thing to do this week, in Vern's
voice, standalone (it also appears outside the note). May differ from the
note's action or restate it more briefly. No em-dashes."""


def _client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])


def _structured(client, system: str, user: str, schema: dict) -> dict | None:
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        system=system,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": user}],
    )
    if response.stop_reason == "refusal":
        print("[curate] WARNING: model refused; falling back", file=sys.stderr)
        return None
    text = next((b.text for b in response.content if b.type == "text"), "")
    return json.loads(text)


def _job_line(i: int, j: dict) -> str:
    contact = ""
    if j.get("contacts"):
        c = j["contacts"][0]
        contact = f" | hiring contact: {c.get('name')}, {c.get('title', '')}"
    return (f"[{i}] tier={TIER_LABELS.get(j.get('tier'), '?')}"
            f"{' WILDCARD' if j.get('wildcard') else ''} | {j['title']}"
            f" | {j.get('company', '?')} | {j.get('location', '?')}"
            f" | salary: {j.get('salary', 'not stated')}"
            f" | {j.get('snippet', '')[:200]}{contact} | url: {j.get('url', '')}")


def score_jobs(client, jobs: list[dict], profile: str) -> None:
    if not jobs:
        return
    # Batch in chunks of 25 to keep responses well-formed.
    for start in range(0, len(jobs), 25):
        chunk = jobs[start:start + 25]
        listing = "\n".join(_job_line(i, j) for i, j in enumerate(chunk))
        result = _structured(
            client, SCORER_SYSTEM,
            f"CANDIDATE PROFILE:\n{profile}\n\nJOB POSTINGS:\n{listing}",
            SCORE_SCHEMA)
        if not result:
            continue
        by_index = {row["index"]: row for row in result.get("jobs", [])}
        for i, job in enumerate(chunk):
            row = by_index.get(i)
            if row:
                job.update(score=row["score"], summary=row["summary"],
                           why=row["why"], watch_out=row["watch_out"],
                           kickoff_prompt=row["kickoff_prompt"],
                           attachments=row.get("attachments", []))


def pick_ai_articles(client, articles: list[dict],
                     recent_notes: list[str] | None = None,
                     top_jobs: list[str] | None = None,
                     progress: str = "",
                     profile_excerpt: str = "") -> tuple[list[dict], str]:
    if not articles:
        return [], ""
    listing = "\n".join(
        f"[{i}] ({a['feed']}) {a['title']} :: {a.get('summary', '')[:200]}"
        for i, a in enumerate(articles[:40]))
    recent = "\n".join(f"- {n}" for n in (recent_notes or [])[-7:]) or "(none yet)"
    tonight = "; ".join((top_jobs or [])[:3]) or "(no standout leads tonight)"
    result = _structured(
        client, PICKS_SYSTEM,
        f"CANDIDATE PROFILE (excerpt):\n{profile_excerpt}\n\n"
        f"ARTICLES:\n{listing}\n\nRECENT NOTES (do not repeat their themes or "
        f"structures):\n{recent}\n\nTONIGHT'S STRONGEST LEADS (usable as a "
        f"theme): {tonight}"
        + (f"\n\nHIS REAL PROGRESS (from the application tracker; usable as "
           f"a theme, cite specifics sparingly): {progress}" if progress
           else ""),
        PICKS_SCHEMA)
    if not result:
        return [], ""
    picks = []
    for row in result.get("ai_picks", [])[:3]:
        if 0 <= row["index"] < len(articles):
            article = dict(articles[row["index"]])
            article["note"] = row["note"]
            picks.append(article)
    return picks, result.get("encouragement", ""), result.get("one_action", "")


def fetch_dad_joke(hist: dict) -> str:
    """One fresh joke per edition from icanhazdadjoke.com (the candidate's request,
    2026-08-06). Joke ids are remembered in history.json so a joke never
    repeats; the API is random, so retry a few times for an unseen one.
    Failure returns "" - the edition renders fine without a joke."""
    import requests
    seen = set(hist.get("joke_ids", []))
    try:
        for _ in range(6):
            resp = requests.get(
                "https://icanhazdadjoke.com/",
                headers={"Accept": "application/json",
                         "User-Agent": ("The Next Chapter newsletter "
                                        "(Next Chapter newsletter)")},
                timeout=10)
            resp.raise_for_status()
            d = resp.json()
            if d.get("id") and d["id"] not in seen:
                hist["joke_ids"] = (hist.get("joke_ids", []) + [d["id"]])[-500:]
                return d.get("joke", "")
    except Exception as e:  # noqa: BLE001 - boundary: external API
        print(f"[curate] dad joke unavailable: {type(e).__name__}",
              file=sys.stderr)
    return ""


def load_tracker() -> list[dict]:
    """Rows from tracker_data.json (written by fetch.py from the sheet's
    published CSV). Absent/broken file = empty: read-back quietly off."""
    f = HERE / "tracker_data.json"
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - boundary: generated file
        return []


def tracker_progress(rows: list[dict]) -> tuple[str, str]:
    """(digest-row value, Vern-context line) for live applications."""
    live = [r for r in rows if r.get("status") in
            ("Applied", "Heard back", "Interview", "Offer")]
    if not live:
        return "", ""
    quiet_days = 0
    for r in live:
        if r.get("status") == "Applied" and r.get("applied_on") \
                and not r.get("last_contact_on"):
            try:
                d = (datetime.date.today() - datetime.date.fromisoformat(
                    r["applied_on"][:10])).days
                quiet_days = max(quiet_days, d)
            except ValueError:
                pass
    meetings = [r for r in live if r.get("status") == "Interview"]
    value = f"{len(live)} application{'s' if len(live) != 1 else ''} live"
    if meetings:
        value += f", {len(meetings)} interview{'s' if len(meetings) != 1 else ''} booked"
    if quiet_days >= 10:
        value += f"; one quiet {quiet_days} days - a short follow-up is due"
    context = "; ".join(
        f"{r.get('title') or r.get('company')} at {r.get('company', '?')}: "
        f"{r.get('status')}" for r in live[:5])
    return value + ".", context


def rav_meter(rows: list[dict],
              now: datetime.datetime) -> tuple[str, bool]:
    """('7 of 12 applications this month - on pace', behind?) from the
    tracker's Applied dates. RAV_MONTHLY_TARGET unset/0 = meter off.
    Pace compares the count against a straight-line month (day 15 of 30
    with a target of 12 expects 6). Month boundary is Europe/Zurich."""
    target = int(os.environ.get("RAV_MONTHLY_TARGET") or 0)
    if not target:
        return "", False
    import calendar
    month = now.strftime("%Y-%m")
    n = sum(1 for r in rows if (r.get("applied_on") or "")[:7] == month)
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    behind = n < int(target * now.day / days_in_month)
    pace = "behind pace" if behind else "on pace"
    return (f"{n} of {target} application{'s' if target != 1 else ''} "
            f"this month - {pace}"), behind


def build_digest(gated: list[dict], total_read: int, one_action: str,
                 inplay_value: str = "", rav_value: str = "") -> list[dict]:
    """The 'Tonight in one minute' rows, shared by the email and the full
    edition so the two always agree."""
    scored = [j for j in gated if j.get("score")]
    top = max(scored, key=lambda j: j["score"], default=None)
    apply_n = sum(1 for j in gated if (j.get("score") or 0) >= 4)
    ns = [j for j in gated if j.get("tier") == 1]
    rows = []
    if rav_value:
        rows.append({"label": "RAV meter", "value": rav_value + "."})
    if inplay_value:
        rows.append({"label": "In play", "value": inplay_value})
    if top and top["score"] >= 3:
        rows.append({"label": "Top pick",
                     "value": f"{top['title']} at {top.get('company', '?')}"
                              f" ({TIER_LABELS.get(top.get('tier'), '?')})."})
    rows.append({"label": "New tonight",
                 "value": f"{total_read} postings read; "
                          f"{apply_n or 'none'} apply-worthy, "
                          f"{len(gated)} cleared the gate."})
    if ns:
        best_ns = max(ns, key=lambda j: j.get("score") or 0)
        rows.append({"label": "Home turf",
                     "value": f"{len(ns)} {cfg.HOME_REGION} posting"
                              f"{'s' if len(ns) != 1 else ''} tonight, led by "
                              f"{best_ns['title']}."})
    rows.append({"label": "One action",
                 "value": one_action or "Open the full edition and give the "
                          "top pick ten unhurried minutes."})
    # 6, not 5: the RAV-meter row must never crowd out "One action".
    return rows[:6]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", choices=["morning", "evening"],
                        help="default: by Zurich clock (<12 = morning)")
    args = parser.parse_args()

    data = json.loads(IN_FILE.read_text(encoding="utf-8"))
    now = datetime.datetime.now(ZURICH)
    edition = args.edition or ("morning" if now.hour < 12 else "evening")

    gated = [j for j in data["jobs"] if gate(j)]
    print(f"[curate] gate: {len(gated)} passed, {len(data['jobs']) - len(gated)} rejected")

    # Application tracker read-back: never re-pitch a job he's already
    # applied to (or further along on) - it lives in the In-play section.
    tracker_rows = load_tracker()
    in_flight = {r.get("normalized_url") for r in tracker_rows
                 if r.get("status") in ("Applied", "Heard back", "Interview",
                                        "Offer", "Rejected")}
    in_flight |= {r.get("fingerprint") for r in tracker_rows
                  if r.get("status") in ("Applied", "Heard back", "Interview",
                                         "Offer", "Rejected")}
    from history import job_fingerprint, normalize_url
    before = len(gated)
    gated = [j for j in gated
             if normalize_url(j.get("url", "")) not in in_flight
             and job_fingerprint(j) not in in_flight]
    if before != len(gated):
        print(f"[curate] tracker: {before - len(gated)} job(s) already "
              f"applied to excluded from tonight's pitch")
    inplay_value, progress = tracker_progress(tracker_rows)
    rav_value, rav_behind = rav_meter(tracker_rows, now)

    history_file = HERE / "history.json"
    hist = (json.loads(history_file.read_text(encoding="utf-8-sig"))
            if history_file.exists() else {})

    encouragement = ""
    one_action = ""
    ai_picks: list[dict] = []
    if os.environ.get("CLAUDE_API_KEY"):
        client = _client()
        # Privacy option for the public repo: a CANDIDATE_PROFILE secret
        # (full markdown) overrides the committed profile file.
        profile = (os.environ.get("CANDIDATE_PROFILE")
                   or PROFILE_FILE.read_text(encoding="utf-8"))
        score_jobs(client, gated, profile)
        # Nightly variety: Vern sees his last week of notes (stored in
        # history.json, Curated Canopy recent_greetings pattern) plus
        # tonight's best leads, and must not repeat himself.
        top_jobs = [f"{j['title']} at {j.get('company', '?')}"
                    for j in gated if (j.get("score") or 0) >= 4]
        ai_picks, encouragement, one_action = pick_ai_articles(
            client, data["ai_articles"], hist.get("recent_notes", []),
            top_jobs, progress, profile[:1200])
        if encouragement:
            hist["recent_notes"] = (hist.get("recent_notes", [])
                                    + [encouragement])[-7:]
        print(f"[curate] Vern scored {len(gated)} jobs, picked {len(ai_picks)} articles")
    else:
        print("[curate] CLAUDE_API_KEY not set: gate-only mode (no scores)")

    # Behind pace on the monthly RAV quota beats any other single action -
    # a missed quota is a benefit sanction, not a missed opportunity.
    if rav_behind:
        one_action = (f"The RAV meter reads {rav_value}. Pick tonight's "
                      "best apply-worthy seat and send a real application.")

    dad_joke = fetch_dad_joke(hist)
    history_file.write_text(
        json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")

    OUT_FILE.write_text(json.dumps({
        "curated_at": now.isoformat(),
        "edition": edition,
        "weekday": now.strftime("%A"),
        "jobs": sorted(gated, key=lambda j: -(j.get("score") or 0)),
        "ai_picks": ai_picks,
        "ai_articles": data.get("ai_articles", []),
        "ns_articles": data.get("ns_articles", []),
        "encouragement": encouragement,
        "dad_joke": dad_joke,
        "digest": build_digest(gated, len(data["jobs"]), one_action,
                               inplay_value, rav_value),
        "stats": {
            "postings_read": len(data["jobs"]),
            "apply": sum(1 for j in gated if (j.get("score") or 0) >= 4),
            "home": sum(1 for j in gated if j.get("tier") == 1),
            "rav": rav_value,
        },
        "source_status": data.get("source_status", {}),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[curate] wrote {OUT_FILE.name} ({edition} edition)")


if __name__ == "__main__":
    main()
