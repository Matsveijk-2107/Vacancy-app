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
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    TimeoutError as FuturesTimeout,
)
from urllib.parse import urlparse
from dotenv import load_dotenv

from clubs import CLUBS, CLUBS_BY_LEAGUE
from keywords import match_role
from utils import (
    DEFAULT_HEADERS,
    can_fetch,
    dedup_by_url,
    make_absolute,
    now_iso,
    parse_date_loose,
    polite_delay,
)
from database import (
    init_db,
    log_scrape_session,
    sync_vacancies,
    prune_unseen,
    get_last_scraped,
)

load_dotenv()
logger = logging.getLogger(__name__)

SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
# Adzuna job-aggregator API (free key). Legitimate, structured replacement for
# LinkedIn (which blocks scraping) — covers job boards across GB/IT/ES/FR/DE/NL/BE.
ADZUNA_APP_ID:  str = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")
# Country → Adzuna market code (only the markets Adzuna supports).
_ADZUNA_COUNTRY = {
    "England": "gb", "Scotland": "gb", "Wales": "gb",
    "Italy": "it", "Spain": "es", "France": "fr", "Germany": "de",
    "Netherlands": "nl", "Belgium": "be",
    # Adzuna has no Portugal / Denmark market → those clubs skip this layer.
}
REQUEST_TIMEOUT = 10
CLUB_TIMEOUT    = 60   # hard cap per club

# How many clubs to scrape at once. Each club is independent network I/O, so
# fanning out turns a ~10-minute serial run into a couple of minutes.
SCRAPE_WORKERS = 8

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
    "workforceready.eu",
    "workforceready.com",
    "hibob.com",
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


# If the TITLE names one of these roles, it is NOT a data job no matter what its
# JD mentions — so don't let the description rescue it. A real "Data Scout" or
# "Performance Analyst" matches on the title directly and never reaches here.
_TITLE_BLOCK = (
    "coach", "scout", "physio", "physiother", "therap", "rehab", "nutrition",
    "medical", "medicine", "doctor", "physician", "masseur", "psycholog",
    "kinesi", "fitness", "conditioning", "goalkeep", "groundsman", "grounds ",
    "steward", "chef", "kitchen", "hospitality", "catering", "retail", "ticket",
    "sales", "matchday", "kit man", "kitman", "academy coach", "set-piece coach",
    "wellbeing", "welfare", "safeguard", "chaplain", "intern coach",
)


def _match(title: str, description: str = "") -> list[str]:
    """Match on the title; if that misses, rescue via an explicit role phrase in
    the description — but only for titles that aren't clearly a non-data role.

    The strict-description rescue used to flag coaching/scouting/medical roles
    whose JDs happen to mention "performance analysis" or "video analyst"
    (e.g. "U21 Assistant Coach", "National Academy Scout"). Blocking those
    titles keeps the rescue for genuinely vague-but-data roles only.
    """
    matched = match_role(title)
    if matched:
        return matched
    if description:
        from keywords import _norm
        if any(b in _norm(title) for b in _TITLE_BLOCK):
            return []
        return match_role(description, strict=True)
    return []


def _clean(html_text: str) -> str:
    """Strip HTML tags from an ATS description blob for keyword matching."""
    if not html_text:
        return ""
    return BeautifulSoup(html_text, "lxml").get_text(" ", strip=True)


def _epoch_ms_to_date(value) -> str:
    """Convert a millisecond epoch (Lever createdAt) to YYYY-MM-DD."""
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


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

# URL path fragments that indicate a link points to a specific job posting.
# Used to filter out nav/footer/content links on a club's own domain.
# Trusted external domains (ATS platforms) and careers pages already hosted on
# a trusted ATS domain bypass this check entirely.
_JOB_PATH_HINTS = (
    "/job", "/vacanc", "/career", "/opening", "/position", "/offre",
    "/empleo", "/stelle", "/lavoro", "/werken", "/jobs", "/posting",
    "/apply", "/application", "/bewerbung", "/aanmelding", "/sollicit",
    "/emploi", "/anuncio", "/annonce", "/stilling",
    # Italian / Spanish / Portuguese careers paths
    "/lavora", "/posizion", "/candidat", "/trabaja", "/oferta", "/empleo",
    "/vaga", "/connosco", "/recrutement", "/nous-rejoindre",
    "jobdetail", "jobdetails", "jobid=", "jid=", "vacancy_id=", "vacancyid=",
    "requisition", "req_id", "reqid=", "referenceid=",
)


def _jobtoolz_embedded(html_text: str, club: dict, league: str, country: str) -> list[dict]:
    """Extract vacancies from a Jobtoolz careers page.

    Jobtoolz (used by many Belgian/Dutch clubs, e.g. Club Brugge) renders its job
    list client-side via an Alpine.js attribute:
        x-data="window.jobComponent([{"id":..,"title":"Game Preparation Analyst",
                                       "url":"https://.../game-preparation-analyst"}, ...])"
    so the links never appear as <a> tags. The JSON is sitting right there in the
    HTML (entity-encoded), so we unescape and parse it directly.
    """
    if "jobComponent(" not in html_text:
        return []
    import json as _json
    import html as _htmllib
    text = _htmllib.unescape(html_text)
    out: list[dict] = []
    seen: set[str] = set()
    decoder = _json.JSONDecoder()
    for m in re.finditer(r"jobComponent\(\s*(\[)", text):
        start = m.start(1)
        try:
            jobs, _ = decoder.raw_decode(text[start:])
        except Exception:
            continue
        if not isinstance(jobs, list):
            continue
        for job in jobs:
            if not isinstance(job, dict):
                continue
            title = (job.get("title") or "").strip()
            jurl  = (job.get("url") or "").strip()
            if not title or jurl in seen:
                continue
            matched = match_role(title)
            if matched:
                seen.add(jurl)
                out.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Careers Page",
                    url=jurl or club.get("careers_url", ""),
                    keywords_matched=", ".join(matched),
                ))
    return out


def _layer1_careers_page(club: dict, league: str, country: str) -> list[dict]:
    url = club.get("careers_url")
    if not url:
        return []

    resp = _get(url)
    if not resp:
        return []

    # Use raw bytes so BeautifulSoup detects the page's real charset.
    # Passing resp.text relies on requests' header guess and produced mojibake
    # (e.g. "Women�s First Team") on pages served without a charset header.
    soup    = BeautifulSoup(resp.content, "lxml")
    results: list[dict] = []
    seen:    set[str]   = set()
    base    = url

    # Jobtoolz and similar embed their vacancy list as JSON in the page — pull
    # those out first (they have no crawlable <a> links).
    results.extend(_jobtoolz_embedded(resp.text, club, league, country))
    seen.update(r["url"] for r in results)

    # If the careers URL is already hosted on a trusted ATS domain, all same-domain
    # links are job links — no path-hint filtering needed.
    base_is_ats = _is_trusted_url(base)

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
            matched = match_role(clean_title)
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

        # Only follow links on the club's own domain or a known ATS/form host.
        on_trusted_external = _is_trusted_url(abs_href) and not _is_same_domain(abs_href, base)
        if not (_is_same_domain(abs_href, base) or on_trusted_external):
            continue

        # For same-domain links on a regular club website, require the URL to look
        # like a job posting (path hints). This prevents nav/footer/content links
        # whose text happens to match a keyword from being treated as vacancies.
        # Exceptions: (a) links to trusted external ATS domains skip this check,
        # (b) if the careers page itself is hosted on a trusted ATS domain every
        #     same-domain link is a job link by definition.
        if not on_trusted_external and not base_is_ats:
            if not any(h in abs_href.lower() for h in _JOB_PATH_HINTS):
                continue

        if abs_href in seen:
            continue
        seen.add(abs_href)

        # Skip obvious prose (full sentences / paragraphs) but keep real titles
        # that happen to contain a colon, e.g. "Analyst: First Team".
        if title.endswith((".", "!", "?")) or len(title.split()) > 14:
            continue

        matched = match_role(title)
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
            matched = match_role(text, strict=True)
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
                matched = match_role(candidate, strict=True)
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
    """Teamtailor public feed — reads {careers-domain}/jobs.json.

    Teamtailor career sites (custom domains like careers.arsenal.com as well as
    *.teamtailor.com subdomains) expose a JSONFeed at /jobs.json whose ``items``
    array lists every published job. The old ``data``/``attributes`` REST shape
    and the ``{slug}.teamtailor.com`` guess are kept only as fallbacks — the
    stored slugs (e.g. "careers.arsenal") do NOT resolve as subdomains.
    """
    careers = club.get("careers_url") or ""
    slug    = club.get("teamtailor_slug")
    if not (slug or "teamtailor" in careers.lower()):
        return []

    # Candidate origins, most reliable first: the careers custom domain, then a
    # bare-tenant subdomain guess.
    bases: list[str] = []
    if careers:
        p = urlparse(careers)
        if p.scheme and p.netloc:
            bases.append(f"{p.scheme}://{p.netloc}")
    if slug and "." not in slug:
        bases.append(f"https://{slug}.teamtailor.com")

    for base in bases:
        resp = _get(f"{base}/jobs.json", json=True)
        if not resp:
            continue
        try:
            data = resp.json()
        except Exception:
            continue

        results: list[dict] = []
        # Preferred: JSONFeed ``items``.
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            for job in data["items"]:
                title   = job.get("title", "")
                job_url = job.get("url", "") or f"{base}/jobs"
                desc    = job.get("content_text", "") or _clean(job.get("content_html", ""))
                date    = parse_date_loose((job.get("date_published") or "")[:10])
                matched = _match(title, desc)
                if matched:
                    results.append(_make_vacancy(
                        club, league, country,
                        job_title=title, source="Teamtailor", url=job_url,
                        posted_date=date, description_snippet=desc[:600],
                        keywords_matched=", ".join(matched),
                    ))
            return results

        # Fallback: legacy ``data``/``attributes`` REST shape.
        for job in (data.get("data", []) if isinstance(data, dict) else []):
            attrs  = job.get("attributes", {})
            title  = attrs.get("title", "")
            status = attrs.get("human-status", "") or attrs.get("status", "")
            if status and "open" not in status.lower():
                continue
            job_url = job.get("links", {}).get("careersite-job-url") or f"{base}/jobs"
            matched = match_role(title)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Teamtailor",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        return results

    return []


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
        desc    = _clean(job.get("description", ""))
        date    = parse_date_loose((job.get("published_on") or job.get("created_at") or "")[:10])
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Workable", url=job_url,
                posted_date=date, description_snippet=desc[:600],
                keywords_matched=", ".join(matched),
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
    # content=true returns each job's HTML description so we can match on it.
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
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
        desc    = _clean(job.get("content", ""))
        date    = parse_date_loose((job.get("updated_at") or "")[:10])
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Greenhouse", url=job_url,
                posted_date=date, description_snippet=desc[:600],
                keywords_matched=", ".join(matched),
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
        desc    = job.get("descriptionPlain", "") or _clean(job.get("description", ""))
        date    = _epoch_ms_to_date(job.get("createdAt"))
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Lever", url=job_url,
                posted_date=date, description_snippet=desc[:600],
                keywords_matched=", ".join(matched),
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
    # Use the host straight from the careers URL (correct TLD already), and only
    # fall back to guessing .de/.com if the careers URL was just a bare slug.
    host = urlparse(careers).netloc.lower()
    hosts = [host] if "personio." in host else [
        f"{slug}.jobs.personio.de", f"{slug}.jobs.personio.com"
    ]
    for h in hosts:
        # /search.json is the current public endpoint (/api/v1/jobs now 404s).
        resp = _get(f"https://{h}/search.json", json=True)
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
            job_url = f"https://{h}/job/{job_id}"
            matched = match_role(title)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="Personio",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
        return results   # got a valid response; stop trying hosts
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
        # Path may carry an optional locale prefix (/fr-FR/rejoigneznous) before
        # the board name — skip any xx-XX / xx_XX segment so we pick the board.
        segments = [s for s in parsed.path.strip("/").split("/") if s]
        segments = [s for s in segments if not re.fullmatch(r"[a-z]{2}[-_][A-Za-z]{2}", s)]
        board    = segments[0] if segments else ""
        if not board:
            return []
        # The public job URL keeps the FULL careers path (locale + board), e.g.
        # /fr-FR/rejoigneznous — without it Workday returns 404. The CXS API,
        # however, only takes the board name.
        career_path = parsed.path.strip("/")
        api_url = f"https://{host}/wday/cxs/{org_slug}/{board}/jobs"
        # Workday's CXS jobs endpoint requires POST with a JSON body; a GET
        # returns HTTP 400. Page through all results in batches of 20.
        if not can_fetch(api_url):
            return []
        results: list[dict] = []
        offset, limit, total = 0, 20, None
        while total is None or offset < total:
            resp = requests.post(
                api_url,
                headers={**DEFAULT_HEADERS, "Accept": "application/json",
                         "Content-Type": "application/json"},
                json={"appliedFacets": {}, "limit": limit,
                      "offset": offset, "searchText": ""},
                timeout=REQUEST_TIMEOUT,
            )
            if not resp.ok:
                break
            data    = resp.json()
            total   = data.get("total", 0) if total is None else total
            posts   = data.get("jobPostings", [])
            if not posts:
                break
            for job in posts:
                title   = job.get("title", "")
                ext_id  = job.get("externalPath", "")
                job_url = f"https://{host}/{career_path}{ext_id}" if ext_id else careers
                matched = match_role(title)
                if matched:
                    results.append(_make_vacancy(
                        club, league, country,
                        job_title=title, source="Workday",
                        url=job_url, keywords_matched=", ".join(matched),
                    ))
            offset += limit
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
        matched = match_role(title)
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
        matched = match_role(title)
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
            matched = match_role(title)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="webitrent",
                    url=job_url, keywords_matched=", ".join(matched),
                ))
    except Exception as exc:
        logger.debug("_webitrent %s: %s", club["name"], exc)

    return results


_TALOS_API = "https://api-careers-sites.talos360.com"


def _talos(club: dict, league: str, country: str) -> list[dict]:
    """Talos360 ATS — JS-rendered careers sites (Everton, Sunderland, …).

    The page itself is an Angular shell with no job links in static HTML, so
    Layer 1 sees nothing. The public API exposes the listing in two calls:
    fetch the site config (for the obfuscated site id), then POST a vacancy
    search. Fires for clubs flagged ats_platform="talos" or hosted on a
    talosats-careers.com domain.
    """
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "talos" and "talosats-careers.com" not in host:
        return []
    if not host:
        return []

    hdrs = {**DEFAULT_HEADERS, "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": f"https://{host}", "Referer": f"https://{host}/"}
    try:
        cfg = requests.get(
            f"{_TALOS_API}/api/careerssites/site/config/get?host={host}",
            headers=hdrs, timeout=REQUEST_TIMEOUT,
        )
        if not cfg.ok:
            return []
        site = cfg.json().get("siteConfig", {})
        oid  = site.get("obfuscatedId")
        if not oid:
            return []
        body = {"careersSiteObfuscatedId": oid, "whatCriteria": None,
                "whereCriteria": None, "metadataFilters": [],
                "preFilters": [], "siteType": site.get("siteType", "External")}
        r = requests.post(
            f"{_TALOS_API}/api/careerssite/vacancies/search",
            headers=hdrs, json=body, timeout=REQUEST_TIMEOUT,
        )
        if not r.ok:
            return []
        vacs = r.json().get("careersSiteVacancies", []) or []
    except Exception as exc:
        logger.debug("_talos %s: %s", club["name"], exc)
        return []

    results: list[dict] = []
    for job in vacs:
        title   = job.get("title") or job.get("jobTitle") or job.get("name") or ""
        slug    = job.get("vacancySlug") or job.get("slug") or ""
        vid     = job.get("id") or job.get("vacancyId") or ""
        job_url = (job.get("vacancyUrl") or job.get("url")
                   or (f"https://{host}/vacancies/{vid}/{slug}" if vid else careers))
        matched = match_role(title)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Talos",
                url=job_url, keywords_matched=", ".join(matched),
            ))
    return results


def _successfactors(club: dict, league: str, country: str) -> list[dict]:
    """SAP SuccessFactors Career Site Builder.

    CSB sites (often on a club's own custom domain, e.g. Man City's
    careers.cityfootballgroup.com) render a server-side job list at /search/ —
    `<a href="/job/<slug>/<id>/">Title</a>` tiles, paged 25 at a time via
    ?startrow=N. The SPA home page exposes nothing, so /search/ is the way in.
    """
    careers = club.get("careers_url") or ""
    if not careers:
        return []
    if not (club.get("ats_platform") == "successfactors"
            or "successfactors" in careers.lower()):
        return []

    parsed = urlparse(careers)
    base   = f"{parsed.scheme}://{parsed.netloc}"
    results: list[dict] = []
    seen:    set[str]   = set()
    for startrow in range(0, 250, 25):        # cap at 10 pages
        resp = _get(f"{base}/search/?startrow={startrow}")
        if not resp:
            break
        tiles = re.findall(
            r'<a[^>]+href="(/job/[^"]+/\d+/)"[^>]*>\s*([^<]{3,120})', resp.text
        )
        new = 0
        for href, raw_title in tiles:
            if href in seen:
                continue
            seen.add(href)
            new += 1
            title = re.sub(r"\s+", " ", raw_title).strip()
            matched = match_role(title)
            if matched:
                results.append(_make_vacancy(
                    club, league, country,
                    job_title=title, source="SuccessFactors",
                    url=make_absolute(href, base),
                    keywords_matched=", ".join(matched),
                ))
        if new == 0:                          # no further pages
            break
    return results


def _recruitee(club: dict, league: str, country: str) -> list[dict]:
    """Recruitee — public JSON API at {careers-origin}/api/offers/ (PSV, etc.).
    Served on both the tenant subdomain and the club's custom careers domain."""
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "recruitee" and "recruitee" not in careers.lower() \
       and not host.startswith("werkenbij."):
        return []
    p = urlparse(careers)
    if not (p.scheme and p.netloc):
        return []
    resp = _get(f"{p.scheme}://{p.netloc}/api/offers/", json=True)
    if not resp:
        return []
    try:
        offers = resp.json().get("offers", [])
    except Exception:
        return []
    results = []
    for o in offers:
        if o.get("status") and o.get("status") != "published":
            continue
        title = o.get("title", "")
        url   = o.get("careers_url", "") or careers
        desc  = _clean(o.get("description", ""))
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Recruitee", url=url,
                posted_date=parse_date_loose((o.get("published_at") or "")[:10]),
                description_snippet=desc[:600], keywords_matched=", ".join(matched),
            ))
    return results


def _hrworks(club: dict, league: str, country: str) -> list[dict]:
    """HRworks 'MeDe' — vacancies are server-rendered as a.job-offer-content anchors."""
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "hrworks" and "hrworks" not in careers.lower() \
       and not host.startswith("jobs."):
        return []
    resp = _get(careers)
    if not resp or ("job-offer-content" not in resp.text and "HrwMeDe" not in resp.text):
        return []
    soup = BeautifulSoup(resp.content, "lxml")
    base = f"{urlparse(resp.url).scheme}://{urlparse(resp.url).netloc}"
    results, seen = [], set()
    for a in soup.select("a.job-offer-content[href]"):
        href = a["href"]
        if "id=" not in href:
            continue
        url = make_absolute(href, base)
        if url in seen:
            continue
        seen.add(url)
        title = (a.get("title") or a.get_text(" ", strip=True) or "").strip()
        matched = match_role(title)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="HRworks", url=url,
                keywords_matched=", ".join(matched),
            ))
    return results


def _softgarden(club: dict, league: str, country: str) -> list[dict]:
    """softgarden — JSON-LD DataFeed of all active jobs at {careers-origin}/jobs.feed.json."""
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "softgarden" and "softgarden" not in careers.lower() \
       and not host.startswith("karriere."):
        return []
    p = urlparse(careers)
    if not (p.scheme and p.netloc):
        return []
    resp = _get(f"{p.scheme}://{p.netloc}/jobs.feed.json", json=True)
    if not resp:
        return []
    try:
        elements = resp.json().get("dataFeedElement", [])
    except Exception:
        return []
    results = []
    for el in elements:
        job   = el.get("item", {}) if isinstance(el, dict) else {}
        title = job.get("title", "")
        url   = job.get("url", "") or careers
        desc  = _clean(job.get("description", ""))
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="softgarden", url=url,
                posted_date=parse_date_loose((job.get("datePosted") or "")[:10]),
                description_snippet=desc[:600], keywords_matched=", ".join(matched),
            ))
    return results


def _corehr_workforceready(club: dict, league: str, country: str) -> list[dict]:
    """UKG/Kronos WorkforceReady — public job-requisitions REST API (Chelsea)."""
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "corehr_workforceready" and "workforceready." not in host:
        return []
    m = re.match(r".*/(.+)\.careers|.*/(.+)\.jobs", careers)
    cid = (m.group(1) or m.group(2)) if m else None
    if not cid:
        return []
    origin = f"{urlparse(careers).scheme}://{host}"
    api = f"{origin}/ta/rest/ui/recruitment/companies/%7C{cid}/job-requisitions?offset=0&size=200&sort=desc"
    # Direct fetch (like _hibob/_postingpanda): this is the club's public candidate
    # API; the UKG vendor's blanket robots.txt would otherwise hide it.
    try:
        resp = requests.get(api, headers={**DEFAULT_HEADERS, "Accept": "application/json"},
                            timeout=REQUEST_TIMEOUT)
        if not resp.ok:
            return []
        jobs = resp.json().get("job_requisitions", [])
    except Exception as exc:
        logger.debug("workforceready %s: %s", club["name"], exc)
        return []
    results = []
    for j in jobs:
        title = j.get("job_title", "")
        desc  = j.get("job_description", "") or ""
        matched = _match(title, desc)
        if matched:
            url = f"{origin}/ta/{cid}.careers?ShowJob={j.get('id')}&lang=en-GB"
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="WorkforceReady", url=url,
                description_snippet=desc[:600], keywords_matched=", ".join(matched),
            ))
    return results


def _hellowork(club: dict, league: str, country: str) -> list[dict]:
    """Hellowork — French job board; club company page server-renders its offers."""
    careers = club.get("careers_url") or ""
    if "hellowork.com" not in careers.lower():
        return []
    resp = _get(careers)
    if not resp:
        return []
    import html as _htmllib
    base = f"{urlparse(careers).scheme}://{urlparse(careers).netloc}"
    pat  = re.compile(r'href="(/fr-fr/emplois/(\d+)\.html)"[^>]*?title="([^"]+)"', re.DOTALL)
    results, seen = [], set()
    for href, jid, raw_title in pat.findall(resp.text):
        if jid in seen:
            continue
        seen.add(jid)
        title = _htmllib.unescape(raw_title)
        if " - " in title:                       # strip trailing " - <Club Name>"
            title = re.sub(r"\s*-\s*[^-]+$", "", title).strip()
        matched = match_role(title)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="Hellowork",
                url=base + href, keywords_matched=", ".join(matched),
            ))
    return results


def _hibob(club: dict, league: str, country: str) -> list[dict]:
    """HiBob (Bob) careers — public JSON API at {host}/api/job-ad (Fulham)."""
    careers = club.get("careers_url") or ""
    host    = urlparse(careers).netloc.lower()
    if club.get("ats_platform") != "hibob" and not host.endswith("careers.hibob.com"):
        return []
    ident = host.split(".")[0]
    try:
        resp = requests.get(
            f"https://{host}/api/job-ad",
            headers={**DEFAULT_HEADERS, "Accept": "application/json",
                     "companyIdentifier": ident},
            timeout=REQUEST_TIMEOUT,
        )
        if not resp.ok:
            return []
        jobs = resp.json().get("jobAdDetails", [])
    except Exception as exc:
        logger.debug("hibob %s: %s", club["name"], exc)
        return []
    results = []
    for job in jobs:
        title = job.get("title", "")
        desc  = _clean(job.get("description", ""))
        url   = f"https://{host}/jobs/{job.get('id')}/overview"
        matched = _match(title, desc)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="hibob", url=url,
                posted_date=parse_date_loose((job.get("publishedAt") or "")[:10]),
                description_snippet=desc[:600], keywords_matched=", ".join(matched),
            ))
    return results


def _layer2_ats(club: dict, league: str, country: str) -> list[dict]:
    results = []
    for fn in [_teamtailor, _personio, _workday, _workable, _greenhouse, _lever,
               _pinpoint, _postingpanda, _webitrent, _talos, _successfactors,
               _recruitee, _hrworks, _softgarden, _corehr_workforceready,
               _hellowork, _hibob]:
        try:
            r = fn(club, league, country)
            results.extend(r)
        except Exception as exc:
            logger.debug("%s %s: %s", fn.__name__, club["name"], exc)
    return results


# ---------------------------------------------------------------------------
# Layer 3 – Web/LinkedIn search
#   • SerpAPI when SERPAPI_KEY is set (most reliable)
#   • free DuckDuckGo fallback otherwise — this is the ONLY layer that reaches
#     the ~56 clubs with no careers page (most of Italy, parts of Spain/France)
# Both paths are gated hard: the club's own name must appear in the result, or
# generic "analyst" hits from unrelated companies would pollute the results.
# ---------------------------------------------------------------------------

# Suffix/legal tokens that don't identify a club (used to pick the distinctive word).
_CLUB_STOPWORDS = {
    "fc", "afc", "cf", "sc", "sad", "sd", "ud", "rc", "ac", "as", "ss", "ssc",
    "us", "club", "calcio", "balompie", "real", "royal", "royale", "de", "the",
    "1907", "1909", "1911", "1913", "1846", "1899", "1848", "1893",
}


def _club_identifiers(club: dict) -> list[str]:
    """Distinctive lowercased name tokens (>=4 chars, accent-stripped)."""
    from keywords import _norm
    toks = re.split(r"[^a-z0-9]+", _norm(club["name"]))
    ids  = [t for t in toks if len(t) >= 4 and t not in _CLUB_STOPWORDS]
    return ids or [t for t in toks if t]          # never return empty


def _result_is_about_club(club: dict, text: str) -> bool:
    from keywords import _norm
    t = _norm(text)
    return any(ident in t for ident in _club_identifiers(club))


def _layer3_serpapi(club: dict, league: str, country: str) -> list[dict]:
    from serpapi import GoogleSearch  # type: ignore
    name  = club.get("linkedin_search", club["name"])
    query = f'site:linkedin.com/jobs/view "{name}" (analyst OR "data scientist" OR analytics)'
    data  = GoogleSearch({"q": query, "api_key": SERPAPI_KEY, "num": 10}).get_dict()
    results = []
    for r in data.get("organic_results", []):
        title, url, snippet = r.get("title", ""), r.get("link", ""), r.get("snippet", "")
        if not title or "linkedin.com" not in url:
            continue
        if not _result_is_about_club(club, f"{title} {snippet}"):
            continue
        matched = match_role(title, snippet)
        if matched:
            results.append(_make_vacancy(
                club, league, country,
                job_title=title, source="LinkedIn", url=url,
                description_snippet=snippet,
                posted_date=parse_date_loose(r.get("date", "")),
                keywords_matched=", ".join(matched),
            ))
    return results


def _layer3_ddg(club: dict, league: str, country: str) -> list[dict]:
    """Keyless fallback via DuckDuckGo. Accepts only trusted-domain results that
    mention the club by name (DDG ignores site:/quote operators, so we filter)."""
    try:
        from ddgs import DDGS              # type: ignore
    except Exception:
        try:
            from duckduckgo_search import DDGS  # type: ignore
        except Exception:
            return []
    name  = club.get("linkedin_search", club["name"])
    query = f'"{name}" football (analyst OR "data scientist" OR analytics OR analista OR analyste)'
    try:
        with DDGS() as ddg:
            hits = list(ddg.text(query, max_results=15))
    except Exception as exc:
        logger.debug("DDG %s: %s", club["name"], exc)
        return []

    results, seen = [], set()
    for h in hits:
        url     = h.get("href") or h.get("link") or ""
        title   = h.get("title", "")
        snippet = h.get("body") or h.get("snippet") or ""
        if not url or not title or url in seen:
            continue
        if not (_is_trusted_url(url) and "/job" in url.lower()):
            continue
        if not _result_is_about_club(club, f"{title} {snippet}"):
            continue
        matched = match_role(title, snippet)
        if not matched:
            continue
        seen.add(url)
        source = "LinkedIn" if "linkedin.com" in url.lower() else "Web Search"
        results.append(_make_vacancy(
            club, league, country,
            job_title=title, source=source, url=url,
            description_snippet=snippet, keywords_matched=", ".join(matched),
        ))
    return results


def _adzuna(club: dict, league: str, country: str) -> list[dict]:
    """Adzuna aggregator API — the LinkedIn replacement.

    Adzuna indexes job boards across many markets. ``what_phrase`` forces the
    club's own name to appear in the posting, which keeps precision high, and we
    still gate on match_role + a club-name check. Needs a free API key
    (ADZUNA_APP_ID / ADZUNA_APP_KEY); silently skips when unset.
    """
    if not (ADZUNA_APP_ID and ADZUNA_APP_KEY):
        return []
    cc = _ADZUNA_COUNTRY.get(country)
    if not cc:
        return []
    name = club.get("linkedin_search") or club["name"]
    url  = f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID, "app_key": ADZUNA_APP_KEY,
        "what_phrase": name,                 # club name must appear in the ad
        "results_per_page": 50, "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params,
                            headers={**DEFAULT_HEADERS, "Accept": "application/json"},
                            timeout=REQUEST_TIMEOUT)
        if not resp.ok:
            return []
        data = resp.json()
    except Exception as exc:
        logger.debug("Adzuna %s: %s", club["name"], exc)
        return []

    out, seen = [], set()
    for job in data.get("results", []):
        title = job.get("title", "") or ""
        comp  = (job.get("company") or {}).get("display_name", "")
        jurl  = job.get("redirect_url", "")
        if not title or jurl in seen:
            continue
        if not _result_is_about_club(club, f"{title} {comp}"):
            continue
        matched = _match(title, job.get("description", ""))
        if not matched:
            continue
        seen.add(jurl)
        out.append(_make_vacancy(
            club, league, country,
            job_title=title, source="Adzuna", url=jurl,
            description_snippet=(job.get("description", "") or "")[:300],
            posted_date=parse_date_loose((job.get("created", "") or "")[:10]),
            keywords_matched=", ".join(matched),
        ))
    return out


def _layer3_search(club: dict, league: str, country: str) -> list[dict]:
    """Search layer: Adzuna aggregator (keyed) → keyless DuckDuckGo last resort.

    LinkedIn is intentionally NOT used — it blocks scraping. SerpAPI/LinkedIn
    helpers remain in the file but are no longer wired in.
    """
    try:
        hits = _adzuna(club, league, country)
        if hits:
            return hits
        return _layer3_ddg(club, league, country)
    except Exception as exc:
        logger.warning("Layer3 search %s: %s", club["name"], exc)
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
    soup    = BeautifulSoup(resp.content, "lxml")
    results = []
    for a in soup.select("a[href*='/job/']"):
        title   = a.get_text(strip=True)
        href    = make_absolute(a.get("href", ""), search_url)
        if not title:
            continue
        matched = match_role(title)
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

    # Deterministic, club-owned sources always run.
    primary = [
        ("careers page", _layer1_careers_page),
        ("ATS",          _layer2_ats),
        ("job boards",   _layer4_livefootballjobs),
    ]
    for label, fn in primary:
        try:
            r = fn(club, league, country)
            all_results.extend(r)
            if r:
                polite_delay(0.5, 1.0)
        except Exception as exc:
            logger.warning("%s %s (%s): %s", label, club["name"], league, exc)

    # Search layer (Adzuna aggregator → DuckDuckGo). Adzuna runs for every club
    # when keys are set (precise: requires the club name in the ad). The keyless
    # DDG fallback only runs when nothing else was found, confining it to clubs
    # with no working careers/ATS source and avoiding DDG rate-bans.
    run_search = bool(ADZUNA_APP_ID and ADZUNA_APP_KEY) or not all_results
    if run_search:
        try:
            all_results.extend(_layer3_search(club, league, country))
        except Exception as exc:
            logger.warning("search %s (%s): %s", club["name"], league, exc)

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
    """Scrape every club concurrently, then sync (non-destructively) to the DB.

    Replied/starred marks and first_seen history survive the run; vacancies that
    vanished from a club's site are pruned afterwards. New roles (since the last
    completed scan) are flagged is_new=1.
    """
    init_db()
    started_at  = now_iso()
    run_ts      = started_at
    mark_new    = get_last_scraped() is not None   # first ever run → no "new" noise

    jobs = [
        (club, league, league.split(" - ")[0] if " - " in league else league)
        for league, clubs in CLUBS_BY_LEAGUE.items()
        for club in clubs
    ]
    total_clubs = len(jobs)
    processed   = 0
    total_found = 0
    errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=SCRAPE_WORKERS) as ex:
        futures = {
            ex.submit(scrape_club, club, league, country): club
            for club, league, country in jobs
        }
        for future in as_completed(futures):
            club = futures[future]
            try:
                vacancies = future.result()
                if vacancies:
                    # DB writes happen here in the main thread only (no lock needed).
                    total_found += sync_vacancies(vacancies, run_ts, mark_new=mark_new)
            except Exception as exc:
                errors[club["name"]] = str(exc)
                logger.error("Failed %s: %s", club["name"], exc)
            processed += 1
            if progress_callback:
                progress_callback(
                    processed / total_clubs,
                    f"Scanned {processed}/{total_clubs} clubs · {total_found} roles",
                )

    pruned = prune_unseen(run_ts)
    logger.info("Pruned %d vacancies no longer listed", pruned)
    log_scrape_session(started_at, now_iso(), processed, total_found)
    if progress_callback:
        progress_callback(1.0, f"Done — {total_found} vacancies across {processed} clubs.")

    return {"total": total_found, "clubs_scraped": processed, "errors": errors}
