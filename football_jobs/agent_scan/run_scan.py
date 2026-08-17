"""Weekly scheduled-scan runner (reliable, no WebSearch rate limit).

Runs the app's own scraping engine (`scrape_all_clubs`) across all 176 clubs.
It hits careers pages and ATS JSON APIs directly over HTTP via `requests`, so it
does NOT use the rate-limited WebSearch tool and finishes in a couple of minutes.
Writes a dated report to `football_jobs/agent_scan/scans/scan-YYYY-MM-DD.md`.

LinkedIn is NOT covered here (scraper.py excludes it by design) — this is the
own-site / ATS / job-board sweep. The full LinkedIn scan is the local `/scan-jobs`.

Usage (from anywhere):
    python football_jobs/agent_scan/run_scan.py
Exit code is 0 on success. Prints a short summary to stdout (used as the
scheduled run's notification text).
"""

import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)  # football_jobs/
sys.path.insert(0, APP)
os.chdir(APP)  # so scraper's relative paths (.env, jobs.db) resolve

from scraper import scrape_all_clubs           # noqa: E402
from database import get_vacancies             # noqa: E402
from clubs import CLUBS, CLUBS_BY_LEAGUE       # noqa: E402
from keywords import classify_role, match_confidence, relevance_score  # noqa: E402

# Map the scraper's `source` field to a coarse "where found" label for the report.
_SOURCE_KIND = {
    "Careers Page": "Own site", "LiveFootballJobs": "Job board",
    "Web Search": "Web search", "Adzuna": "Job board", "LinkedIn": "LinkedIn",
}


def _kind(source: str) -> str:
    return _SOURCE_KIND.get(source, "ATS")


def _demojibake(name: str) -> str:
    if "Ã" not in name:
        return name
    try:
        return name.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def build_report(result: dict, rows: list[dict], today: str) -> str:
    clubs_with_hits = sorted({_demojibake(r["club_name"]) for r in rows})
    leagues_with_hits = sorted({r["league"] for r in rows})
    lines: list[str] = []
    lines.append(f"# Football analytics job scan — {today}")
    lines.append("")
    lines.append("> **Automated weekly run** via the app's own scraper "
                 "(`scrape_all_clubs`: L1 careers pages + L2 ATS JSON + L3 search + "
                 "L4 boards). **LinkedIn is NOT covered** — that's the local "
                 "`/scan-jobs`. This is the own-site / ATS / job-board sweep.")
    lines.append("")
    lines.append("## A. Summary")
    lines.append("")
    lines.append(f"**{len(rows)} matched data/analytics roles** at "
                 f"**{len(clubs_with_hits)} clubs** across **{len(leagues_with_hits)} "
                 f"leagues**, from **{result['clubs_scraped']}/{len(CLUBS)} clubs "
                 f"scanned**, as of **{today}**.")
    lines.append("")
    lines.append("## B. Matched roles (most relevant first)")
    lines.append("")
    lines.append("| # | Role | Club | League | Category | Conf. | Source | Posted | Link |")
    lines.append("|---|------|------|--------|----------|-------|--------|--------|------|")
    for i, r in enumerate(rows, 1):
        title = (r.get("job_title") or "").replace("|", "/").strip()
        lines.append(
            f"| {i} | {title} | {_demojibake(r.get('club_name',''))} | "
            f"{r.get('league','')} | {r['_cat']} | {r['_conf']} | "
            f"{_kind(r.get('source',''))} | {r.get('posted_date') or '—'} | "
            f"{r.get('url','')} |"
        )
    lines.append("")
    short = [r for r in rows if r["_conf"] == "high"][:5] or rows[:5]
    lines.append("## C. Worth applying to first")
    lines.append("")
    if short:
        for r in short:
            lines.append(f"- **{(r.get('job_title') or '').strip()}** — "
                         f"{_demojibake(r.get('club_name',''))} "
                         f"({r.get('league','')}, {r['_cat']}) — {r.get('url','')}")
    else:
        lines.append("_No matches this run._")
    lines.append("")
    lines.append("## D. Errors")
    lines.append("")
    errs = result.get("errors", {})
    if errs:
        for club, err in sorted(errs.items()):
            lines.append(f"- {_demojibake(club)}: {str(err)[:160]}")
    else:
        lines.append("_No clubs raised a hard error during the scrape._")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    print("=== running scrape_all_clubs() ===", flush=True)
    result = scrape_all_clubs()
    rows = get_vacancies()
    for r in rows:
        title = r.get("job_title", "")
        desc = r.get("description_snippet", "") or ""
        r["_cat"] = classify_role(title, desc)
        r["_conf"] = match_confidence(title, desc) or "low"
        r["_rel"] = relevance_score(title, desc)
    rows.sort(key=lambda r: r["_rel"], reverse=True)

    today = datetime.date.today().isoformat()
    report = build_report(result, rows, today)
    scans_dir = os.path.join(HERE, "scans")
    os.makedirs(scans_dir, exist_ok=True)
    out = os.path.join(scans_dir, f"scan-{today}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)

    # Concise summary for the scheduled run's notification/email.
    best = rows[0] if rows else None
    print("=== SCAN SUMMARY ===", flush=True)
    print(f"date: {today}", flush=True)
    print(f"clubs_scanned: {result['clubs_scraped']}/{len(CLUBS)}", flush=True)
    print(f"matched_roles: {len(rows)}", flush=True)
    if best:
        print(f"top_role: {best.get('job_title','').strip()} @ "
              f"{_demojibake(best.get('club_name',''))} — {best.get('url','')}", flush=True)
    print(f"report_file: {os.path.relpath(out, APP.rsplit('/', 1)[0])}", flush=True)


if __name__ == "__main__":
    main()
