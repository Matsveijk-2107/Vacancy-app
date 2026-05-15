"""
Scraping strategy (accuracy-first):

  L1 – Direct careers page (HTML) on the club's own domain only
  L2 – ATS platform JSON APIs: Teamtailor → Workable → Greenhouse → Lever
  L3 – LinkedIn Jobs via SerpAPI (only when SERPAPI_KEY is set)
  L4 – LiveFootballJobs (UK / NL / BE clubs)

General web searches removed — they return news articles, fan sites and
aggregators that happen to mention the club name near a keyword, not real
open positions. Every result must come from a trusted domain.
"""

import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from urllib.parse import urlparse
from dotenv import load_dotenv

from clubs import CLUBS
from keywords import ANALYTICS_KEYWORDS
from utils import (
    DEFAULT_HEADERS,
    can_fetch,
    dedup_by_url,
    make_absolute,
    match_keywords,
    now_iso,
    parse_date_loose,
    polite_delay,
)
from database import init_db, log_scrape_session, upsert_vacancies, clear_all_vacancies

load_dotenv()
logger = logging.getLogger(__name__)

SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
REQUEST_TIMEOUT = 10
CLUB_TIMEOUT    = 60   # hard cap per club

# Domains we trust to contain real job postings
TRUSTED_DOMAINS = {
    "linkedin.com",
    "teamtailor.com",
    "workable.com",
    "greenhouse.io",
    "lever.co",
    "smartrecruiters.com",
    "bamboohr.com",
    "personio.de",
    "personio.com",
    "jobvite.com",
    "recruitee.com",
    "join.com",
    "livefootballjobs.com",
    "eurofootjobs.com",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_vacancy(club: dict, league: str, country: str, **kw) -> dict:
    return {
        "club_name":           club["name"],
        "league":              league,
        "country":             country,
        "job_title":           kw.get("job_title", "")[:250],
        "source":              kw.get("source", "Unknown"),
        "url":                 kw.get("url", ""),
        "description_snippet": kw.get("description_snippet", "")[:600],
        "posted_date":         kw.get("posted_date", ""),
        "scraped_at":          now_iso(),
        "is_analytics_match":  1,
        "keywords_matched":    kw.get("keywords_matched", ""),
    }


def _is_trusted_url(url: str) -> bool:
    """Return True only if the URL comes from a domain we trust for job postings."""
    try:
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return any(td in domain for td in TRUSTED_DOMAINS)
    except Exception:
        return False


def _is_same_domain(url: str, base_url: str) -> bool:
    try:
        return urlparse(url).netloc == urlparse(base_url).netloc
    except Exception:
        return False


def _get(url: str, *, json: bool = False, timeout: int = REQUEST_TIMEOUT):
    """Fetch URL, return response or None."""
    try:
        if not can_fetch(url):
            return None
        headers = {**DEFAULT_HEADERS}
        if json:
            headers["Accept"] = "application/json"
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as exc:
        logger.debug("GET %s → %s", url, exc)
        return None


def _slugs(name: str) -> list[str]:
    """Generate ATS slug candidates from a club name."""
    lower = name.lower()
    # Strip common suffixes that ATS platforms usually omit
    stripped = re.sub(
        r"\b(fc|afc|sc|sv|vfl|vfb|fsv|bv|krc|rsc|ssc|sl|as|ss|ac|us|ud|rc|sd|"
        r"cd|aj|ogc|losc|tsg|spvgg|rsca|rafc|usg|hsv|bvb|1\.|rsca)\b",
        "", lower,
    )
    # Build slug variants
    full  = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    short = re.sub(r"[^a-z0-9]+", "-", stripped.strip()).strip("-")
    nodash = short.replace("-", "")
    # Unique, preserving order
    seen, result = set(), []
    for s in [short, nodash, full]:
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return result


# ---------------------------------------------------------------------------
# Layer 1 – Direct careers page
# ---------------------------------------------------------------------------

_JOB_PATH_HINTS = (
    "/job", "/vacanc", "/career", "/opening", "/position", "/offre",
    "/empleo", "/stelle", "/lavoro", "/werken", "/jobs",
)


def _layer1_careers_page(club: dict, league: str, country: str) -> list[dict]:
    url = club.get("careers_url")
    if not url:
        return []

    resp = _get(url)
    if not resp:
        return []

    soup    = BeautifulSoup(resp.text, "lxml")
    results: list[dict] = []
    seen:    set[str]   = set()
    base    = url

    for a in soup.find_all("a", href=True):
        title    = a.get_text(" ", strip=True)
        abs_href = make_absolute(a["href"], base)

        if not title or not (4 < len(title) < 300):
            continue

        # Only links on the club's own domain or a known ATS
        if not (_is_same_domain(abs_href, base) or _is_trusted_url(abs_href)):
            continue

        # URL must look like it leads to a specific job
        if not any(h in abs_href.lower() for h in _JOB_PATH_HINTS):
            continue

        if abs_href in seen:
            continue
        seen.add(abs_href)

        matched = match_keywords(title, ANALYTICS_KEYWORDS)
        if not matched:
            continue

        results.append(_make_vacancy(
            club, league, country,
            job_title=title, source="Careers Page",
            url=abs_href, keywords_matched=", ".join(matched),
        ))

    return results


# ---------------------------------------------------------------------------
# Layer 2 – ATS platform APIs
# ---------------------------------------------------------------------------

def _teamtailor(club: dict, league: str, country: str) -> list[dict]:
    """Teamtailor public JSON API — returns only open jobs."""
    results = []
    for slug in _slugs(club["name"]):
        api_url = f"https://{slug}.teamtailor.com/jobs.json"
        resp    = _get(api_url, json=True)
        if not resp:
            continue
        try:
            data = resp.json()
        except Exception:
            continue
        jobs = data.get("data", [])
        if not jobs:
            continue
        for job in jobs:
            attrs  = job.get("attributes", {})
            title  = attrs.get("title", "")
            status = attrs.get("human-status", "") or attrs.get("status", "")
            if "open" not in status.lower() and status:
                continue
            job_url = (
                job.get("links", {}).get("careersite-job-url")
                or f"https://{slug}.teamtailor.com/jobs/{job.get('id','')}"
            )
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Teamtailor",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        if results:
            break  # found a working slug, stop trying
    return results


def _workable(club: dict, league: str, country: str) -> list[dict]:
    """Workable public widget API."""
    results = []
    for slug in _slugs(club["name"]):
        api_url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}/jobs"
        resp    = _get(api_url, json=True)
        if not resp:
            continue
        try:
            data = resp.json()
        except Exception:
            continue
        jobs = data.get("results", [])
        if not jobs:
            continue
        for job in jobs:
            title   = job.get("title", "")
            code    = job.get("shortcode", "")
            job_url = f"https://apply.workable.com/{slug}/j/{code}"
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Workable",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        if results:
            break
    return results


def _greenhouse(club: dict, league: str, country: str) -> list[dict]:
    """Greenhouse public jobs board API."""
    results = []
    for slug in _slugs(club["name"]):
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        resp    = _get(api_url, json=True)
        if not resp:
            continue
        try:
            data = resp.json()
        except Exception:
            continue
        jobs = data.get("jobs", [])
        if not jobs:
            continue
        for job in jobs:
            title   = job.get("title", "")
            job_url = job.get("absolute_url", "")
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Greenhouse",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        if results:
            break
    return results


def _lever(club: dict, league: str, country: str) -> list[dict]:
    """Lever public jobs API."""
    results = []
    for slug in _slugs(club["name"]):
        api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        resp    = _get(api_url, json=True)
        if not resp:
            continue
        try:
            jobs = resp.json()
        except Exception:
            continue
        if not isinstance(jobs, list) or not jobs:
            continue
        for job in jobs:
            title   = job.get("text", "")
            job_url = job.get("hostedUrl", "")
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Lever",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        if results:
            break
    return results


def _layer2_ats(club: dict, league: str, country: str) -> list[dict]:
    results = []
    for fn in [_teamtailor, _workable, _greenhouse, _lever]:
        try:
            r = fn(club, league, country)
            results.extend(r)
        except Exception as exc:
            logger.debug("%s %s: %s", fn.__name__, club["name"], exc)
    return results


# ---------------------------------------------------------------------------
# Layer 3 – LinkedIn via SerpAPI (trusted URLs only)
# ---------------------------------------------------------------------------

def _layer3_linkedin(club: dict, league: str, country: str) -> list[dict]:
    if not SERPAPI_KEY:
        return []
    try:
        from serpapi import GoogleSearch  # type: ignore
        name  = club.get("linkedin_search", club["name"])
        query = f'site:linkedin.com/jobs/view "{name}" (analyst OR "data scientist" OR analytics)'
        data  = GoogleSearch({
            "q": query, "api_key": SERPAPI_KEY, "num": 10,
        }).get_dict()
        results = []
        for r in data.get("organic_results", []):
            title   = r.get("title", "")
            url     = r.get("link", "")
            snippet = r.get("snippet", "")
            date    = parse_date_loose(r.get("date", ""))
            if not title or not url:
                continue
            if "linkedin.com" not in url:          # safety check
                continue
            matched = match_keywords(f"{title} {snippet}", ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="LinkedIn",
                    url=url, description_snippet=snippet,
                    posted_date=date, keywords_matched=", ".join(matched),
                ))
        return results
    except Exception as exc:
        logger.warning("LinkedIn/SerpAPI %s: %s", club["name"], exc)
        return []


# ---------------------------------------------------------------------------
# Layer 4 – LiveFootballJobs
# ---------------------------------------------------------------------------

def _layer4_livefootballjobs(club: dict, league: str, country: str) -> list[dict]:
    if country not in ("England", "Scotland", "Netherlands", "Belgium"):
        return []
    search_url = f"https://www.livefootballjobs.com/?s={requests.utils.quote(club['name'])}"
    resp = _get(search_url)
    if not resp:
        return []
    soup    = BeautifulSoup(resp.text, "lxml")
    results = []
    for a in soup.select("a[href*='/job/']"):
        title   = a.get_text(strip=True)
        href    = make_absolute(a.get("href", ""), search_url)
        if not title:
            continue
        matched = match_keywords(f"{title} {club['name']}", ANALYTICS_KEYWORDS)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="LiveFootballJobs",
                url=href, keywords_matched=", ".join(matched),
            ))
    return results


# ---------------------------------------------------------------------------
# Per-club orchestration
# ---------------------------------------------------------------------------

def _scrape_club_inner(club: dict, league: str, country: str) -> list[dict]:
    all_results: list[dict] = []

    for label, fn in [
        ("careers page", _layer1_careers_page),
        ("ATS",          _layer2_ats),
        ("LinkedIn",     _layer3_linkedin),
        ("job boards",   _layer4_livefootballjobs),
    ]:
        try:
            r = fn(club, league, country)
            all_results.extend(r)
            if r:
                polite_delay(0.5, 1.0)
        except Exception as exc:
            logger.warning("%s %s (%s): %s", label, club["name"], league, exc)

    return dedup_by_url(all_results)


def scrape_club(club: dict, league: str, country: str) -> list[dict]:
    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(_scrape_club_inner, club, league, country)
        try:
            return future.result(timeout=CLUB_TIMEOUT)
        except FuturesTimeout:
            logger.warning("Timed out (%ds): %s", CLUB_TIMEOUT, club["name"])
            future.cancel()
            return []
        except Exception as exc:
            logger.error("Error %s: %s", club["name"], exc)
            return []


# ---------------------------------------------------------------------------
# Full scrape
# ---------------------------------------------------------------------------

def scrape_all_clubs(progress_callback=None) -> dict:
    init_db()
    clear_all_vacancies()
    started_at  = now_iso()
    total_clubs = sum(len(v) for v in CLUBS.values())
    processed   = 0
    total_found = 0
    errors: dict[str, str] = {}

    for league, clubs in CLUBS.items():
        country = league.split(" - ")[0] if " - " in league else league
        for club in clubs:
            if progress_callback:
                progress_callback(
                    processed / total_clubs,
                    f"Scraping {club['name']}  ({processed + 1}/{total_clubs})",
                )
            try:
                vacancies   = scrape_club(club, league, country)
                inserted    = upsert_vacancies(vacancies)
                total_found += inserted
            except Exception as exc:
                errors[club["name"]] = str(exc)
                logger.error("Failed %s: %s", club["name"], exc)
            processed += 1

    log_scrape_session(started_at, now_iso(), processed, total_found)
    if progress_callback:
        progress_callback(1.0, f"Done — {total_found} vacancies across {processed} clubs.")

    return {"total": total_found, "clubs_scraped": processed, "errors": errors}
