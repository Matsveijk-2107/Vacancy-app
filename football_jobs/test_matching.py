"""Behavioural tests for the role matcher and DB sync.

Run:  pytest football_jobs/test_matching.py
These are network-free and lock in the recall / noise / history behaviour.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest

from keywords import match_role, relevance_score
import database as db


# ── Recall: real football data/analytics roles must match ────────────────────
@pytest.mark.parametrize("title", [
    "First Team Data Analyst",
    "Performance Analyst - Women's",
    "Data Scientist",
    "Machine Learning Engineer",
    "Datawetenschapper",                 # NL
    "Wedstrijdanalist",                  # NL compound
    "Analyste de données",               # FR, accented
    "Cientifico de Datos",               # ES
    "Analista di prestazione",           # IT
    "Datenwissenschaftler (m/w/d)",      # DE
    "Præstationsanalytiker",             # DK
    "Technical Scout",
    "Head of Football Intelligence",
])
def test_real_roles_match(title):
    assert match_role(title), f"should match: {title!r}"


# ── Precision: obvious non-football / footer / legal noise must NOT match ────
@pytest.mark.parametrize("title", [
    "Information Security Risk Analyst",
    "Financial Analyst",
    "Payroll Officer",
    "Groundsman",
    "Data & Privacy",
    "Data Protection Officer",
    "Cookie Policy",
    "FOUNDATION",                        # contains 'dati' substring
    "Contactgegevens",                   # NL footer link
    "Validation Officer",
])
def test_noise_does_not_match(title):
    assert not match_role(title), f"should NOT match: {title!r}"


# ── Strict mode (used on loose page text) only keeps explicit role phrases ────
def test_strict_mode_drops_bare_data():
    assert match_role("Data & privacy", strict=True) == []
    assert match_role("Performance Analyst", strict=True)


# ── Relevance ordering: data-science > performance > generic > bare ──────────
def test_relevance_ordering():
    assert (relevance_score("Data Scientist")
            > relevance_score("Performance Analyst")
            > relevance_score("Data Coordinator")
            > relevance_score("Business Analyst"))


# ── DB: a scrape must NOT wipe replied/starred history ───────────────────────
def test_sync_preserves_replied_and_tracks_new(tmp_path):
    db.DB_PATH = tmp_path / "t.db"
    db.init_db()

    def vac(url, title="Data Analyst"):
        return dict(club_name="Ajax", league="Netherlands", country="Netherlands",
                    job_title=title, source="Greenhouse", url=url,
                    description_snippet="", posted_date="2026-06-01",
                    scraped_at="2026-06-06T10:00:00", is_analytics_match=1,
                    keywords_matched="data analyst")

    # First run — nothing is "new".
    db.sync_vacancies([vac("u/1"), vac("u/2")], "t1", mark_new=False)
    db.prune_unseen("t1")
    db.log_scrape_session("t1", "t1", 1, 2)
    assert len(db.get_vacancies()) == 2

    # User replies to u/1.
    db.mark_as_replied(db.get_vacancies()[0]["id"])

    # Second run: u/1 vanished, u/2 stays, u/3 is new.
    db.sync_vacancies([vac("u/2"), vac("u/3", "Data Scientist")], "t2", mark_new=True)
    db.prune_unseen("t2")

    open_urls = {v["url"] for v in db.get_vacancies()}
    replied_urls = {v["url"] for v in db.get_vacancies(replied=True)}
    new_urls = {v["url"] for v in db.get_vacancies() if v["is_new"]}

    assert open_urls == {"u/2", "u/3"}        # u/1 pruned from open
    assert replied_urls == {"u/1"}            # but replied history preserved
    assert new_urls == {"u/3"}                # only the genuinely new one flagged
