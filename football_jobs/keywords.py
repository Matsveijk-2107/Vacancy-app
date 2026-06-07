"""
Role matching for a football *data / analytics* job hunt.

Design goals (high recall, the user is a football data scientist):
  • Catch EVERYTHING that looks like an analyst or a data role, in any of
    EN · NL · DE · FR · ES · IT · PT · DK.
  • Be accent-insensitive ("données" == "donnees", "táctico" == "tactico"),
    so multilingual titles stop slipping through.
  • Match on the job title *and* its description snippet when we have one.
  • Drop only the obvious non-football noise (security / finance / HR-type
    "analyst" roles) while keeping anything that mentions data.

`match_role(title, description="")` returns the list of human-readable terms
that matched (empty list = not a match). The terms are shown as chips in the UI.
"""

from __future__ import annotations

import re
import unicodedata


def _norm(text: str) -> str:
    """Lowercase and strip diacritics so accents never block a match."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


# ── Explicit phrases (used for nice, readable chips in the UI) ────────────────
# Substring-matched, so compound words (NL/DE "wedstrijdanalist") still hit.
ANALYTICS_KEYWORDS = [
    # ── English ──────────────────────────────────────────────────────────
    "data analyst", "data scientist", "data science", "data engineer",
    "data analytics", "analytics", "analyst", "machine learning",
    "performance analyst", "performance analysis", "video analyst", "technical analyst",
    "match analyst", "tactical analyst", "opposition analyst",
    "set piece analyst", "first team analyst", "recruitment analyst",
    "scouting analyst", "insight analyst", "insights analyst",
    "insights manager", "head of analysis", "head of data",
    "head of insight", "head of analytics", "head of research",
    "data manager", "data infrastructure", "business intelligence",
    "research scientist", "researcher", "quantitative analyst",
    "modelling", "statistician", "data scout", "technical scout",
    "python", "sql", "tableau", "power bi", "r programming",
    "tracking data", "event data", "statsbomb", "opta", "wyscout",
    "instat", "hudl", "skillcorner", "sports analytics", "football intelligence",
    # ── Dutch (NL / BE) ──────────────────────────────────────────────────
    "data-analist", "gegevensanalist", "wedstrijdanalist", "spelersanalist",
    "prestatieanalist", "prestatieanalyse", "videoanalist", "tactisch analist",
    "analist", "datawetenschapper", "hoofd analyse", "hoofd data",
    # ── German (DE) ──────────────────────────────────────────────────────
    "datenanalyst", "leistungsanalyst", "spielanalyst", "taktikanalyst",
    "videoanalyst", "datenwissenschaftler", "analytiker", "gegneranalyse",
    "leistungsdiagnostik", "dateningenieur", "datenmanager", "spielbeobachter",
    # ── French (FR) ──────────────────────────────────────────────────────
    "analyste", "analyste video", "analyste tactique", "analyste de donnees",
    "analyste performance", "data analyste", "science des donnees",
    "ingenieur donnees", "responsable donnees", "responsable data",
    # ── Spanish (ES) ─────────────────────────────────────────────────────
    "analista", "analista de datos", "analista de rendimiento",
    "analista tactico", "analista de video", "cientifico de datos",
    "ingeniero de datos", "jefe de datos", "jefe de analisis",
    # ── Italian (IT) ─────────────────────────────────────────────────────
    "analista dati", "analista video", "analista tattico",
    "scienziato dei dati", "ingegnere dei dati", "analisi tattica",
    "responsabile dati", "capo analisi",
    # ── Portuguese (PT) ──────────────────────────────────────────────────
    "analista de dados", "analista de desempenho", "analista de video",
    "cientista de dados", "engenheiro de dados", "chefe de analise",
    # ── Danish (DK) ──────────────────────────────────────────────────────
    "dataanalytiker", "praestationsanalytiker", "videoanalytiker",
    "taktisk analytiker", "dataingenior", "chefanalytiker", "analytiker",
]

# Normalised once at import for fast matching.
_KEYWORDS_NORM = [(_norm(kw), kw) for kw in ANALYTICS_KEYWORDS]


# ── Core tokens — the broad "analyst OR data" net (already accent-stripped) ───
# Analyst-family: substring-matched so compounds hit ("wedstrijdanalist",
# "datenanalyst"). "analy"/"analis" rarely collide with non-analyst words.
_ANALYST_TOKENS = (
    "analyst", "analytic", "analytik", "analyse", "analysis",
    "analist", "analiste", "analista", "analise", "analitic",
    "analitico", "analitica", "analiz",
)
# Science / signal: substring-matched, low collision risk.
# NB: bare "scientist" is deliberately excluded — it matched sports/recovery
# scientists (physiology, not data). Data-science is caught by the explicit
# "data scientist" phrase and the data-specific words below.
_LOOSE_TOKENS = (
    "datawetenschap", "datenwissenschaft",
    "insight", "intelligence", "statistic", "statistik", "estadistic",
    "machine learning", "tracking data", "event data", "modelling", "modeling",
    "quantitative", "wyscout", "statsbomb", "skillcorner", "instat",
)
# Short data words must match as WHOLE WORDS — otherwise "dati" hits "foundation"
# and "gegevens" hits "contactgegevens". \b treats hyphens as boundaries, so
# "data-analist" still matches.
_DATA_RE = re.compile(
    r"\b(data|datos|dati|daten|dado|dados|donnees?|gegevens?)\b"
)

# "Strong" = unmistakably a data role. These survive the exclude filter even
# when paired with an otherwise-excluded word (e.g. "Data Security Analyst").
_STRONG_LOOSE = ("analytic", "analytik")

# Obvious non-football-data functions. A role in one of these areas is noise for
# a data scientist, so drop it — unless the title/JD also explicitly names data.
# Includes medical / sports-science / physio roles: the user is a *data*
# scientist, so "Sports Scientist", "Recovery Scientist", "Physiotherapist",
# "Rehabilitation", "Nutritionist", "Sports Science & Medicine" etc. are noise.
EXCLUDE_TOKENS = (
    "financ", "security", "compliance", "payroll", "procurement",
    "accountant", "accounting", "auditor", "human resources",
    "physio", "physiother", "rehab", "therap", "nutrition", "dietit",
    "masseur", "massage", "medical", "medicine", "physician", "doctor",
    "wellbeing", "well-being", "kinesi", "osteopath", "chiro", "podiat",
    "psycholog", "sports scien", "sport scien", "exercise scien",
    "sports scientist", "recovery scientist", "strength and conditioning",
)

# Footer / legal links that mention "data" but are never jobs
# ("Data & Privacy", "Data Protection Policy", cookie notices, …).
_NOISE_TOKENS = (
    "privacy", "cookie", "gdpr", "data protection", "disclaimer",
    "terms of use", "terms and conditions", "data subject",
)


def _has_role_word(text_norm: str) -> bool:
    return any(t in text_norm for t in _ANALYST_TOKENS) or "data scientist" in text_norm


def _strong_data(text_norm: str) -> bool:
    return bool(_DATA_RE.search(text_norm)) or any(t in text_norm for t in _STRONG_LOOSE)


def match_role(title: str, description: str = "", *, strict: bool = False) -> list[str]:
    """Return matched display terms for a vacancy (empty list = no match).

    strict=True only counts the explicit ANALYTICS_KEYWORDS phrases (no broad
    analyst/data net). Use it when scanning loose page text (headings, nav)
    where the broad net would surface false positives.
    """
    text = _norm(f"{title} {description}")
    if not text.strip():
        return []

    # Exclusion gate: drop obvious non-football functions unless data is named.
    if any(x in text for x in EXCLUDE_TOKENS) and not _strong_data(text):
        return []

    # Footer / legal noise ("Data & Privacy"): keep only if a real role word is present.
    if any(n in text for n in _NOISE_TOKENS) and not _has_role_word(text):
        return []

    # Prefer the readable explicit phrases for chips.
    matched: list[str] = []
    seen: set[str] = set()
    for kw_norm, kw_label in _KEYWORDS_NORM:
        if kw_norm in text and kw_label not in seen:
            seen.add(kw_label)
            matched.append(kw_label)
    if matched:
        return matched
    if strict:
        return []

    # Broad fallback: any analyst-family / science / signal token, or a data word.
    core_hits = [t for t in (_ANALYST_TOKENS + _LOOSE_TOKENS) if t in text]
    if core_hits:
        return core_hits[:1]
    return ["data"] if _DATA_RE.search(text) else []


# ── Relevance scoring (for "most relevant first" sorting) ─────────────────────
# Tiered: a "Data Scientist" should outrank a borderline "Commercial Insights".
_TIER_TOP = (
    "data scientist", "data analyst", "machine learning", "data engineer",
    "research scientist", "datawetenschap", "datenwissenschaft",
    "cientifico de datos", "scienziato dei dati", "analyste de donnees",
    "datenanalyst", "analista de datos", "data analyste",
)
_TIER_HIGH = (
    "performance analyst", "match analyst", "video analyst", "tactical analyst",
    "opposition analyst", "set piece analyst", "first team analyst",
    "wedstrijdanalist", "prestatieanalist", "leistungsanalyst",
    "analista video", "analista tattico", "football intelligence", "sports analytics",
)
_TIER_MED = (
    "recruitment analyst", "scouting analyst", "technical scout", "data scout",
    "insight analyst", "insights analyst", "statistician",
)


def relevance_score(title: str, description: str = "") -> int:
    """Higher = more clearly a football data-science role. Used only for sorting."""
    text = _norm(f"{title} {description}")
    if any(t in text for t in _TIER_TOP):
        base = 100
    elif any(t in text for t in _TIER_HIGH):
        base = 70
    elif any(t in text for t in _TIER_MED):
        base = 50
    elif _DATA_RE.search(text):
        base = 35
    elif any(t in text for t in _ANALYST_TOKENS):
        base = 25
    else:
        base = 10
    # Small bonuses for explicit data tooling / science signals.
    if _DATA_RE.search(text):
        base += 8
    if "data scientist" in text or "machine learning" in text:
        base += 8
    return base
