"""SQLite persistence for scraped vacancies.

Key design choice: a scrape NO LONGER wipes the table. Vacancies are synced by
URL so that:
  • "Done" (replied) marks survive every refresh,
  • we keep a first_seen / last_seen history → "new since last scan" badges,
  • roles that disappear from a club's site are pruned (unless you replied to
    them, so your Done history stays intact).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS vacancies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_name TEXT NOT NULL,
    league TEXT,
    country TEXT,
    job_title TEXT,
    source TEXT,
    url TEXT UNIQUE NOT NULL,
    description_snippet TEXT,
    posted_date TEXT,
    scraped_at DATETIME,
    is_analytics_match INTEGER DEFAULT 1,
    keywords_matched TEXT
);

CREATE TABLE IF NOT EXISTS scrape_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at DATETIME,
    finished_at DATETIME,
    clubs_scraped INTEGER DEFAULT 0,
    vacancies_found INTEGER DEFAULT 0
);
"""

# Columns added after the original schema shipped (idempotent migrations).
_MIGRATIONS = (
    "ALTER TABLE vacancies ADD COLUMN replied INTEGER DEFAULT 0",
    "ALTER TABLE vacancies ADD COLUMN first_seen DATETIME",
    "ALTER TABLE vacancies ADD COLUMN last_seen DATETIME",
    "ALTER TABLE vacancies ADD COLUMN is_new INTEGER DEFAULT 0",
    "ALTER TABLE vacancies ADD COLUMN starred INTEGER DEFAULT 0",
)


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript(_SCHEMA)
        for stmt in _MIGRATIONS:
            try:
                con.execute(stmt)
            except Exception:
                pass  # column already exists


# ── Scrape sync (non-destructive) ─────────────────────────────────────────────

def sync_vacancies(vacancies: list[dict], run_ts: str, *, mark_new: bool) -> int:
    """Upsert scraped vacancies by URL, preserving replied/starred/first_seen.

    Returns the number of rows written. `mark_new` should be False on the very
    first scrape (everything is baseline, nothing is "new").
    """
    written = 0
    with _conn() as con:
        for v in vacancies:
            url = v.get("url", "").strip()
            if not url:
                continue
            existing = con.execute(
                "SELECT id FROM vacancies WHERE url = ?", (url,)
            ).fetchone()
            if existing:
                con.execute(
                    """UPDATE vacancies SET
                         club_name=:club_name, league=:league, country=:country,
                         job_title=:job_title, source=:source,
                         description_snippet=:description_snippet,
                         posted_date=:posted_date, scraped_at=:scraped_at,
                         keywords_matched=:keywords_matched,
                         is_analytics_match=:is_analytics_match,
                         last_seen=:run_ts, is_new=0
                       WHERE url=:url""",
                    {**v, "run_ts": run_ts},
                )
            else:
                con.execute(
                    """INSERT INTO vacancies
                         (club_name, league, country, job_title, source, url,
                          description_snippet, posted_date, scraped_at,
                          is_analytics_match, keywords_matched,
                          first_seen, last_seen, is_new, replied, starred)
                       VALUES
                         (:club_name, :league, :country, :job_title, :source, :url,
                          :description_snippet, :posted_date, :scraped_at,
                          :is_analytics_match, :keywords_matched,
                          :run_ts, :run_ts, :is_new, 0, 0)""",
                    {**v, "run_ts": run_ts, "is_new": 1 if mark_new else 0},
                )
            written += 1
    return written


def prune_unseen(run_ts: str) -> int:
    """Delete vacancies not seen in the latest run — but keep ones you actioned."""
    with _conn() as con:
        cur = con.execute(
            "DELETE FROM vacancies WHERE last_seen < ? AND replied = 0 AND starred = 0",
            (run_ts,),
        )
        return cur.rowcount


# ── Reads ─────────────────────────────────────────────────────────────────────

def get_vacancies(leagues: list[str] | None = None, replied: bool = False) -> list[dict]:
    where = f"WHERE is_analytics_match = 1 AND replied = {1 if replied else 0}"
    params: list = []
    if leagues:
        placeholders = ",".join("?" * len(leagues))
        where += f" AND league IN ({placeholders})"
        params.extend(leagues)
    sql = f"SELECT * FROM vacancies {where} ORDER BY scraped_at DESC"
    with _conn() as con:
        rows = con.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_saved() -> list[dict]:
    """Starred but not-yet-replied roles (the shortlist)."""
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM vacancies WHERE is_analytics_match = 1 AND starred = 1 "
            "AND replied = 0 ORDER BY scraped_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_vacancy(vacancy_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM vacancies WHERE id = ?", (vacancy_id,)).fetchone()
    return dict(row) if row else None


def get_last_scraped() -> str | None:
    with _conn() as con:
        row = con.execute("SELECT MAX(finished_at) AS last FROM scrape_sessions").fetchone()
    return row["last"] if row and row["last"] else None


# ── Mutations from the UI ─────────────────────────────────────────────────────

def mark_as_replied(vacancy_id: int, replied: bool = True) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE vacancies SET replied = ? WHERE id = ?",
            (1 if replied else 0, vacancy_id),
        )


def toggle_star(vacancy_id: int) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE vacancies SET starred = CASE starred WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
            (vacancy_id,),
        )


# ── Sessions ──────────────────────────────────────────────────────────────────

def log_scrape_session(started_at: str, finished_at: str,
                       clubs_scraped: int, vacancies_found: int) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO scrape_sessions (started_at, finished_at, clubs_scraped, vacancies_found)"
            " VALUES (?, ?, ?, ?)",
            (started_at, finished_at, clubs_scraped, vacancies_found),
        )
