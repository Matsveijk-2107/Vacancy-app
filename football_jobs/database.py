import sqlite3
from contextlib import contextmanager
from datetime import datetime
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


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript(_SCHEMA)


def upsert_vacancy(v: dict) -> None:
    sql = """
    INSERT OR REPLACE INTO vacancies
        (club_name, league, country, job_title, source, url,
         description_snippet, posted_date, scraped_at,
         is_analytics_match, keywords_matched)
    VALUES
        (:club_name, :league, :country, :job_title, :source, :url,
         :description_snippet, :posted_date, :scraped_at,
         :is_analytics_match, :keywords_matched)
    """
    with _conn() as con:
        con.execute(sql, v)


def clear_all_vacancies() -> None:
    with _conn() as con:
        con.execute("DELETE FROM vacancies")


def upsert_vacancies(vacancies: list[dict]) -> int:
    inserted = 0
    for v in vacancies:
        try:
            upsert_vacancy(v)
            inserted += 1
        except Exception:
            pass
    return inserted


def get_vacancies(leagues: list[str] | None = None) -> list[dict]:
    where = "WHERE is_analytics_match = 1"
    params: list = []
    if leagues:
        placeholders = ",".join("?" * len(leagues))
        where += f" AND league IN ({placeholders})"
        params.extend(leagues)
    sql = f"SELECT * FROM vacancies {where} ORDER BY scraped_at DESC"
    with _conn() as con:
        rows = con.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_last_scraped() -> str | None:
    with _conn() as con:
        row = con.execute(
            "SELECT MAX(scraped_at) AS last FROM vacancies"
        ).fetchone()
    return row["last"] if row else None


def log_scrape_session(started_at: str, finished_at: str, clubs_scraped: int, vacancies_found: int) -> None:
    sql = """
    INSERT INTO scrape_sessions (started_at, finished_at, clubs_scraped, vacancies_found)
    VALUES (?, ?, ?, ?)
    """
    with _conn() as con:
        con.execute(sql, (started_at, finished_at, clubs_scraped, vacancies_found))


def clear_vacancies_older_than(hours: int = 24) -> None:
    with _conn() as con:
        con.execute(
            "DELETE FROM vacancies WHERE scraped_at < datetime('now', ? || ' hours')",
            (f"-{hours}",),
        )


def log_scrape_session(started_at: str, finished_at: str, clubs: int, vacancies: int) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO scrape_sessions (started_at, finished_at, clubs_scraped, vacancies_found) VALUES (?,?,?,?)",
            (started_at, finished_at, clubs, vacancies),
        )
