"""
Scraping strategy (accuracy-first):

  L1 – Direct careers page (HTML) on the club's own domain
        Trusted external apply links (MS Forms, Pinpoint, etc.) also captured.
  L2 – ATS platform JSON APIs (slug always read from careers_url — no guessing):
         Teamtailor · Personio · Workday · Workable · Greenhouse · Lever
  L3 – LinkedIn Jobs via SerpAPI (only when SERPAPI_KEY is set)
  L4 – LiveFootballJobs (UK / NL / BE clubs)

Keywords are matched case-insensitively in: EN · NL · DE · FR · ES · IT · PT · DK
Every result must originate from a club's own domain or a known trusted host.
"""

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
del _sys, _os

import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from urllib.parse import urlparse
from dotenv import load_dotenv

from clubs import CLUBS, CLUBS_BY_LEAGUE
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
    # Major ATS / HRIS platforms
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
    "breezy.hr",
    "ashby.com",
    "pinpointhq.com",
    "recruitcrm.io",
    "talentlyft.com",
    "comeet.com",
    "recooty.com",
    # ERP / Enterprise HR (Workday, SuccessFactors, Oracle, etc.)
    "myworkdayjobs.com",
    "successfactors.com",
    "sapsf.com",
    "oraclecloud.com",
    "icims.com",
    "taleo.net",
    "silkroad.com",
    # German / DACH ATS
    "hrworks.de",
    "softgarden.io",
    "softgarden.de",
    "umantis.com",
    "haufe.de",
    "meinestelle.de",
    "stepstone.de",
    # French ATS / boards
    "talentsoft.com",
    "jobteaser.com",
    "welcometothejungle.com",
    "hellowork.com",
    "digitalrecruiters.com",
    # Dutch / Belgian
    "nationalevacaturebank.nl",
    "talenteon.nl",
    "carerix.com",
    # Application / form platforms
    "forms.office.com",       # Microsoft Forms (apply links)
    "typeform.com",
    "jotform.com",
    # Football-specific boards
    "livefootballjobs.com",
    "eurofootjobs.com",
    "sportyjob.com",
    "work-in-sports.com",
    "sportsprojobs.com",
    # LinkedIn (fallback — apply links from careers pages)
    "linkedin.com",
    # Specific ATS platforms whose careers URLs are hosted on the ATS domain
    # (same-domain links won't match generic job path hints without these)
    "candidatemanager.net",
    "webitrent.com",
    "webrecruitment.com",
    "networxrecruitment.com",
    "mhr.co.uk",
    "hireserve.com",
    "hirewire.co.uk",
    "vacancy.filler.co.uk",
    "applytojob.com",
    "jobs.smartrecruiters.com",
    "postingpandaapi-live.azurewebsites.net",
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
        raw_href = a["href"].strip()

        # Some ATS portals (e.g. webitrent) render job lists with javascript: hrefs.
        # The title is still meaningful — use the careers page URL as the job link.
        if raw_href.lower().startswith("javascript:"):
            if not title or not (4 < len(title) < 300):
                continue
            # Strip common suffixes like " Job profile" added by certain ATSes
            clean_title = title.removesuffix(" Job profile").strip()
            if clean_title in seen:
                continue
            matched = match_keywords(clean_title, ANALYTICS_KEYWORDS)
            if matched:
                seen.add(clean_title)
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=clean_title, source="Careers Page",
                    url=base, keywords_matched=", ".join(matched),
                ))
            continue

        abs_href = make_absolute(raw_href, base)

        if not title or not (4 < len(title) < 300):
            continue

        # Only links on the club's own domain or a known ATS/form host.
        # We intentionally do NOT filter by URL path patterns here — ATS platforms
        # use wildly different URL structures (query strings, hashed IDs, etc.).
        # Keyword matching on the link text is the real gate against nav/footer links.
        on_trusted_external = _is_trusted_url(abs_href) and not _is_same_domain(abs_href, base)
        if not (_is_same_domain(abs_href, base) or on_trusted_external):
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

    # Text fallback — for pages that list job titles as plain text rather than links
    # (e.g. Swansea City who publish a news-article-style vacancy list).
    # Only runs when no link-based results were found to avoid duplicates.
    if not results:
        # Strategy 1: scan individual short text elements
        for tag in soup.find_all(["li", "h2", "h3", "h4", "dt", "strong", "b"]):
            text = tag.get_text(" ", strip=True)
            if not text or not (5 < len(text) < 120):
                continue
            matched = match_keywords(text, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=text, source="Careers Page",
                    url=url, keywords_matched=", ".join(matched),
                ))

        # Strategy 2: split the full page text at "Closing Date:" markers
        # (catches clubs like Swansea that embed multiple roles in one paragraph)
        if not results:
            full_text = soup.get_text(" ", strip=True)
            import re as _re
            # Grab everything before each "Closing Date:" occurrence
            # Regex: optional leading "Month Year" prefix (e.g. "May 2026 ") before the title
            pat = r'(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+)?([A-Z][^.!?\n]{5,100}?)\s+Closing Date:'
            for candidate in _re.findall(pat, full_text):
                candidate = candidate.strip()
                matched = match_keywords(candidate, ANALYTICS_KEYWORDS)
                if matched:
                    results.append(_make_vacancy(
                        club, league, country,
                        job_title=candidate, source="Careers Page",
                        url=url, keywords_matched=", ".join(matched),
                    ))

    return results


# ---------------------------------------------------------------------------
# Layer 2 – ATS platform APIs
# ---------------------------------------------------------------------------

def _slug_from_url(url: str, platform: str) -> str | None:
    """Extract the ATS tenant slug from a known careers URL pattern."""
    try:
        parsed = urlparse(url)
        host   = parsed.netloc.lower()
        path   = parsed.path.strip("/")
        if platform == "workable":
            if "apply.workable.com" in host:
                return path.split("/")[0] if path else None
            if "workable.com" in host:
                return host.replace(".workable.com", "")
        elif platform == "greenhouse":
            if "greenhouse.io" in host:
                return path.split("/")[0] if path else None
        elif platform == "lever":
            if "lever.co" in host:
                return path.split("/")[0] if path else None
        elif platform == "personio":
            if "jobs.personio" in host:
                return host.split(".jobs.personio")[0]
        elif platform == "workday":
            if "myworkdayjobs.com" in host:
                return host.split(".myworkdayjobs.com")[0]
        elif platform == "smartrecruiters":
            if "smartrecruiters.com" in host:
                return path.split("/")[0] if path else None
    except Exception:
        pass
    return None


def _teamtailor(club: dict, league: str, country: str) -> list[dict]:
    """Teamtailor public JSON API — only runs when teamtailor_slug is set."""
    explicit_slug = club.get("teamtailor_slug")
    if not explicit_slug:
        return []
    api_url = f"https://{explicit_slug}.teamtailor.com/jobs.json"
    resp = _get(api_url, json=True)
    if not resp:
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    results = []
    for job in data.get("data", []):
        attrs  = job.get("attributes", {})
        title  = attrs.get("title", "")
        status = attrs.get("human-status", "") or attrs.get("status", "")
        if "open" not in status.lower() and status:
            continue
        job_url = (
            job.get("links", {}).get("careersite-job-url")
            or f"https://{explicit_slug}.teamtailor.com/jobs/{job.get('id','')}"
        )
        matched = match_keywords(title, ANALYTICS_KEYWORDS)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Teamtailor",
                url=job_url, keywords_matched=", ".join(matched),
            ))
    return results


def _workable(club: dict, league: str, country: str) -> list[dict]:
    """Workable public widget API — slug extracted from careers_url."""
    careers = club.get("careers_url") or ""
    if "workable.com" not in careers:
        return []
    slug = _slug_from_url(careers, "workable")
    if not slug:
        return []
    api_url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}/jobs"
    resp = _get(api_url, json=True)
    if not resp:
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    results = []
    for job in data.get("results", []):
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
    return results


def _greenhouse(club: dict, league: str, country: str) -> list[dict]:
    """Greenhouse public jobs board API — slug extracted from careers_url."""
    careers = club.get("careers_url") or ""
    if "greenhouse.io" not in careers:
        return []
    slug = _slug_from_url(careers, "greenhouse")
    if not slug:
        return []
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    resp = _get(api_url, json=True)
    if not resp:
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    results = []
    for job in data.get("jobs", []):
        title   = job.get("title", "")
        job_url = job.get("absolute_url", "")
        matched = match_keywords(title, ANALYTICS_KEYWORDS)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Greenhouse",
                url=job_url, keywords_matched=", ".join(matched),
            ))
    return results


def _lever(club: dict, league: str, country: str) -> list[dict]:
    """Lever public jobs API — slug extracted from careers_url."""
    careers = club.get("careers_url") or ""
    if "lever.co" not in careers:
        return []
    slug = _slug_from_url(careers, "lever")
    if not slug:
        return []
    api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    resp = _get(api_url, json=True)
    if not resp:
        return []
    try:
        jobs = resp.json()
    except Exception:
        return []
    if not isinstance(jobs, list):
        return []
    results = []
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
    return results


def _personio(club: dict, league: str, country: str) -> list[dict]:
    """Personio public jobs API — slug extracted from careers_url."""
    careers = club.get("careers_url") or ""
    if "personio" not in careers:
        return []
    slug = _slug_from_url(careers, "personio")
    if not slug:
        return []
    for tld in ("de", "com"):
        api_url = f"https://{slug}.jobs.personio.{tld}/api/v1/jobs"
        resp = _get(api_url, json=True)
        if not resp:
            continue
        try:
            jobs = resp.json()
        except Exception:
            continue
        if not isinstance(jobs, list):
            continue
        results = []
        for job in jobs:
            title   = job.get("name", "") or job.get("title", "")
            job_id  = job.get("id", "")
            job_url = f"https://{slug}.jobs.personio.{tld}/job/{job_id}"
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Personio",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        return results   # got a valid response; stop trying TLDs
    return []


def _workday(club: dict, league: str, country: str) -> list[dict]:
    """Workday jobs API — parses the JSON feed from myworkdayjobs.com."""
    careers = club.get("careers_url") or ""
    if "myworkdayjobs.com" not in careers:
        return []
    try:
        parsed   = urlparse(careers)
        host     = parsed.netloc.lower()        # e.g. avfc.wd502.myworkdayjobs.com
        org_full = host.split(".myworkdayjobs.com")[0]  # e.g. avfc.wd502
        org_slug = org_full.split(".")[0]       # e.g. avfc
        board    = parsed.path.strip("/").split("/")[0]  # e.g. avfc_careers
        if not board:
            return []
        api_url = f"https://{host}/wday/cxs/{org_slug}/{board}/jobs"
        resp = _get(api_url, json=True)
        if not resp:
            return []
        data = resp.json()
        results = []
        for job in data.get("jobPostings", []):
            title   = job.get("title", "")
            ext_id  = job.get("externalPath", "")
            job_url = f"https://{host}{ext_id}" if ext_id else careers
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Workday",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        return results
    except Exception as exc:
        logger.debug("Workday %s: %s", club["name"], exc)
        return []


def _pinpoint(club: dict, league: str, country: str) -> list[dict]:
    """Pinpoint ATS public API — {careers_url}/jobs.json."""
    if club.get("ats_platform") != "pinpoint":
        return []
    careers = club.get("careers_url") or ""
    if not careers:
        return []
    # Strip path/query so we always call the root /jobs.json
    parsed   = urlparse(careers)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    api_url  = f"{base_url}/jobs.json"
    resp = _get(api_url, json=True)
    if not resp:
        return []
    try:
        data = resp.json()
    except Exception:
        return []
    results = []
    for job in data.get("data", []):
        title   = job.get("title", "")
        job_url = job.get("url", "") or f"{base_url}/en/postings/{job.get('id','')}"
        matched = match_keywords(title, ANALYTICS_KEYWORDS)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Pinpoint",
                url=job_url, keywords_matched=", ".join(matched),
            ))
    return results


def _postingpanda(club: dict, league: str, country: str) -> list[dict]:
    """Posting Panda ATS API — routes by Origin header to return club-specific jobs."""
    if club.get("ats_platform") != "postingpanda":
        return []
    careers = club.get("careers_url") or ""
    if not careers:
        return []
    parsed     = urlparse(careers)
    origin_url = f"{parsed.scheme}://{parsed.netloc}"
    api_url    = "https://postingpandaapi-live.azurewebsites.net/api/liveadverts"
    try:
        resp = requests.get(
            api_url,
            headers={**DEFAULT_HEADERS, "Accept": "application/json",
                     "Origin": origin_url, "Referer": careers},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        jobs = resp.json()
    except Exception as exc:
        logger.debug("PostingPanda %s: %s", club["name"], exc)
        return []
    if not isinstance(jobs, list):
        return []
    results = []
    seen: set[str] = set()
    for job in jobs:
        title  = job.get("JobTitle", "")
        job_id = job.get("ID", "")
        job_url = f"{origin_url}/job/{job_id}"
        if job_url in seen:
            continue
        seen.add(job_url)
        matched = match_keywords(title, ANALYTICS_KEYWORDS)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Posting Panda",
                url=job_url, keywords_matched=", ".join(matched),
            ))
    return results


def _webitrent(club: dict, league: str, country: str) -> list[dict]:
    """MHR webitrent ATS — two-step: get USESSION from search page, then call
    etrec106gf.json with a custom `mhrParams` header to retrieve all live jobs."""
    if club.get("ats_platform") != "webitrent":
        return []
    careers = club.get("careers_url") or ""
    if not careers:
        return []

    # Parse the base URL and wvid from the careers URL
    parsed  = urlparse(careers)
    wvid_m  = re.search(r'[?&]wvid=([^&]+)', careers, re.IGNORECASE)
    if not wvid_m:
        return []
    wvid    = wvid_m.group(1)
    base    = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"

    results: list[dict] = []
    try:
        # Step 1: load the search page to obtain a valid USESSION token
        r1 = requests.get(careers, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        if not r1.ok:
            return []
        usession_m = re.search(r'USESSION=([A-F0-9]{32})', r1.text)
        if not usession_m:
            return []
        usession    = usession_m.group(1)
        base_params = f"WVID={wvid}&USESSION={usession}&LANG=USA"

        # Step 2: call the JSON search endpoint with mhrParams header
        json_url = f"{base}etrec106gf.json?{base_params}"
        r2 = requests.get(
            json_url,
            headers={
                **DEFAULT_HEADERS,
                "Accept":    "application/json",
                "mhrParams": f"{base_params}&RESULTS_PP=100",
                "Referer":   careers,
            },
            timeout=REQUEST_TIMEOUT,
        )
        if not r2.ok:
            return []
        data    = r2.json()
        jobs    = data.get("results", [])
        seen: set[str] = set()

        for job in jobs:
            title     = job.get("job_title", "")
            vacancy_id = job.get("vacancy_id", "")
            job_url   = f"{base}ETREC107GF.open?VACANCY_ID={vacancy_id}&WVID={wvid}"
            if job_url in seen:
                continue
            seen.add(job_url)
            matched = match_keywords(title, ANALYTICS_KEYWORDS)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="webitrent",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
    except Exception as exc:
        logger.debug("_webitrent %s: %s", club["name"], exc)

    return results


def _layer2_ats(club: dict, league: str, country: str) -> list[dict]:
    results = []
    for fn in [_teamtailor, _personio, _workday, _workable, _greenhouse, _lever,
               _pinpoint, _postingpanda, _webitrent]:
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
    total_clubs = sum(len(v) for v in CLUBS_BY_LEAGUE.values())
    processed   = 0
    total_found = 0
    errors: dict[str, str] = {}

    for league, clubs in CLUBS_BY_LEAGUE.items():
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
