# Scan reports

Dated reports from the **automated weekly scan** land here as `scan-YYYY-MM-DD.md`
and are committed to the repo, so every run's results are durably findable on
GitHub (not dependent on email or an ephemeral session).

- **Producer:** `../run_scan.py`, driven by the weekly Routine (Friday ~01:00 CET).
  It runs the app's own `scrape_all_clubs()` engine (careers pages + ATS JSON +
  L3 search + job boards) over HTTP — no rate-limited web-search calls.
- **Coverage:** own-site / ATS / job-board sweep across all 176 clubs.
  **LinkedIn is *not* covered here** — that's the local `/scan-jobs` run.
- **Newest first:** sort by filename; the latest `scan-*.md` is the most recent run.
