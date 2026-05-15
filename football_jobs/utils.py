import time
import random
import logging
import urllib.robotparser
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

_ROBOT_CACHE: dict[str, urllib.robotparser.RobotFileParser | None] = {}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


def polite_delay(min_s: float = 0.5, max_s: float = 1.5) -> None:
    time.sleep(random.uniform(min_s, max_s))


def retry_with_backoff(func, max_retries: int = 2, base_delay: float = 1.5):
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt) + random.uniform(0, 0.5))
    raise last_exc  # type: ignore[misc]


def can_fetch(url: str, user_agent: str = "*") -> bool:
    """Check robots.txt using requests (with timeout), not urllib."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        if robots_url not in _ROBOT_CACHE:
            try:
                resp = requests.get(
                    robots_url,
                    timeout=5,
                    headers={"User-Agent": user_agent},
                )
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(resp.text.splitlines())
                _ROBOT_CACHE[robots_url] = rp
            except Exception:
                _ROBOT_CACHE[robots_url] = None  # assume allowed on error
        rp = _ROBOT_CACHE.get(robots_url)
        return rp is None or rp.can_fetch(user_agent, url)
    except Exception:
        return True


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def dedup_by_url(vacancies: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for v in vacancies:
        url = v.get("url", "").strip()
        if url and url not in seen:
            seen.add(url)
            result.append(v)
    return result


def make_absolute(href: str, base: str) -> str:
    if not href:
        return base
    if href.startswith("http"):
        return href
    return urljoin(base, href)


def parse_date_loose(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.strip()
    formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
        "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y",
        "%d.%m.%Y", "%Y.%m.%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")
