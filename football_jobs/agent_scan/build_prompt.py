#!/usr/bin/env python3
"""Regenerate the <CLUBS> block inside scan_prompt.md from clubs.py.

The agent-run prompt (scan_prompt.md) carries the same 176-club master list the
Streamlit app uses, so the two never drift. Rather than hand-maintain that list
in two places, this script reads CLUBS_BY_LEAGUE from clubs.py and rewrites only
the region between the ``<CLUBS>`` and ``</CLUBS>`` markers in scan_prompt.md.

Run it whenever clubs.py changes:

    python football_jobs/agent_scan/build_prompt.py          # rewrite in place
    python football_jobs/agent_scan/build_prompt.py --print  # just print the block
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import the club data from the parent package (clubs.py lives one level up).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from clubs import CLUBS_BY_LEAGUE  # noqa: E402

PROMPT_PATH = Path(__file__).resolve().parent / "scan_prompt.md"
START_MARKER = "<CLUBS>"
END_MARKER = "</CLUBS>"

# A search-only club (no curated careers page) still gets scanned — via L3/L4.
SEARCH_ONLY = "(no careers page — search layers only)"


def _demojibake(name: str) -> str:
    """Repair UTF-8-as-Latin1 mojibake in a club name (e.g. 'KÃ¶ln' → 'Köln').

    clubs.py stores a handful of names double-encoded. The scan uses the club
    name as a web-search term, so a garbled name would search for the wrong
    string — we fix it in the generated prompt without touching clubs.py.
    Only names carrying the mojibake signature ('Ã') are touched, and any name
    that fails the round-trip is left exactly as-is.
    """
    if "Ã" not in name:
        return name
    try:
        return name.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def build_clubs_block() -> str:
    """Return the markdown club list, grouped by the app's league display names.

    Each club carries two anchors — its careers/ATS page and its LinkedIn jobs page —
    so the scan checks both for every club, not just the club's own site.
    """
    lines: list[str] = [
        "Format:  Club name | careers: <careers/ATS URL> | linkedin: <LinkedIn jobs URL>",
        "Check BOTH anchors for every club. `(search layers only)` = no curated careers",
        "page found — lean on LinkedIn + L3/L4 (and find the club's live careers page first).",
        "",
    ]
    total = 0
    for league_display, clubs in CLUBS_BY_LEAGUE.items():
        if not clubs:
            continue
        lines.append(f"### {league_display}")
        for club in clubs:
            careers = club.get("careers_url") or SEARCH_ONLY
            linkedin = club.get("linkedin_jobs_url") or "—"
            lines.append(
                f"{_demojibake(club['name'])} | careers: {careers} | linkedin: {linkedin}"
            )
            total += 1
        lines.append("")
    lines.append(f"_Total: {total} clubs across {len(CLUBS_BY_LEAGUE)} league groups._")
    return "\n".join(lines).rstrip() + "\n"


def rewrite_in_place() -> None:
    """Replace the lines between a standalone <CLUBS> and </CLUBS> line.

    The markers are matched only when they are the entire (stripped) content of a
    line, so an inline mention like `<CLUBS>` inside prose is left untouched.
    """
    lines = PROMPT_PATH.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == START_MARKER)
        end = next(i for i, ln in enumerate(lines) if ln.strip() == END_MARKER)
    except StopIteration:
        raise SystemExit(
            f"Standalone {START_MARKER}/{END_MARKER} lines not found in {PROMPT_PATH.name}."
        )
    if end <= start:
        raise SystemExit(f"{END_MARKER} must come after {START_MARKER}.")
    block_lines = build_clubs_block().splitlines()
    new_lines = lines[: start + 1] + block_lines + lines[end:]
    PROMPT_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Rewrote {START_MARKER} block in {PROMPT_PATH.name}.")


def main() -> None:
    if "--print" in sys.argv:
        print(build_clubs_block(), end="")
        return
    rewrite_in_place()


if __name__ == "__main__":
    main()
