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


# ── Explicit ROLE phrases (used for nice, readable chips in the UI) ───────────
# Distinctive, unambiguous analytics ROLES — multi-word titles or compounds that
# name a data/analytics job outright. Substring-matched so NL/DE compounds hit.
# NB: single topic words ("analytics", "data") and tools ("python", "sql") are
# deliberately NOT here — they are not roles and caused false positives
# (nav links like "CLUB DATA", JDs that merely list "SQL" as a skill).
ANALYTICS_KEYWORDS = [
    # ── English ──────────────────────────────────────────────────────────
    "data analyst", "data scientist", "data science", "data engineer",
    "data analytics", "machine learning", "performance analyst",
    "performance analysis", "video analyst", "technical analyst",
    "match analyst", "tactical analyst", "opposition analyst",
    "set piece analyst", "first team analyst", "recruitment analyst",
    "scouting analyst", "insight analyst", "insights analyst",
    "insights manager", "head of analysis", "head of data",
    "head of insight", "head of analytics", "head of research",
    "data manager", "data infrastructure", "business intelligence",
    "research scientist", "quantitative analyst", "statistician",
    "data scout", "technical scout", "sports analytics", "football intelligence",
    "statsbomb", "wyscout", "instat", "skillcorner",
    # ── Dutch (NL / BE) ──────────────────────────────────────────────────
    "data-analist", "gegevensanalist", "wedstrijdanalist", "spelersanalist",
    "prestatieanalist", "videoanalist", "tactisch analist",
    "datawetenschapper", "hoofd analyse", "hoofd data",
    # ── German (DE) ──────────────────────────────────────────────────────
    "datenanalyst", "leistungsanalyst", "spielanalyst", "taktikanalyst",
    "videoanalyst", "datenwissenschaftler", "gegneranalyse",
    "dateningenieur", "datenmanager",
    # ── French (FR) ──────────────────────────────────────────────────────
    "analyste video", "analyste tactique", "analyste de donnees",
    "analyste performance", "data analyste", "science des donnees",
    "ingenieur donnees", "responsable donnees", "responsable data",
    # ── Spanish (ES) ─────────────────────────────────────────────────────
    "analista de datos", "analista de rendimiento",
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
    "taktisk analytiker", "dataingenior", "chefanalytiker",
]

# Normalised once at import for fast matching.
_KEYWORDS_NORM = [(_norm(kw), kw) for kw in ANALYTICS_KEYWORDS]


# ── Analyst-family ROLE tokens — a title saying "analyst" IS a role on its own.
# Compound-friendly substrings ("wedstrijdanalist", "datenanalyst", "analytiker").
_ANALYST_ROLE = (
    "analyst", "analist", "analiste", "analista", "analytiker",
    "analitico", "analitica", "analitic", "analiz",
)

# ── Topic words — the SUBJECT of analytics. Qualify ONLY when a role noun is
# also present, so "CLUB DATA" / "Analyse VR" / a JD that lists "SQL" don't pass.
_TOPIC_TOKENS = (
    "analytics", "analytic", "analytik", "analyse", "analysis", "analisi",
    "intelligence", "insight", "statistic", "statistik", "estadistic",
    "machine learning", "tracking data", "event data", "modelling", "modeling",
    "quantitative", "wyscout", "statsbomb", "skillcorner", "instat",
    "datawetenschap", "datenwissenschaft",
)
# Short data words must match as WHOLE WORDS — otherwise "dati" hits "foundation"
# and "gegevens" hits "contactgegevens". \b treats hyphens as boundaries, so
# "data-analist" still matches.
_DATA_RE = re.compile(r"\b(data|datos|dati|daten|dado|dados|donnees?|gegevens?)\b")

# Generic job-role nouns. A data/analytics TOPIC + one of these = a data role
# ("Data Scientist", "Senior Analytics Engineer", "Scouting Insights Officer").
_ROLE_NOUNS = (
    "analyst", "analist", "analista", "analiste", "analytiker",
    "scientist", "cientifico", "cientista", "scienziato",
    "wetenschapper", "wissenschaftler",
    "engineer", "ingenieur", "ingegnere", "ingeniero", "engenheiro",
    "manager", "officer", "coordinator", "coordinador",
    "coordenador", "coordinatore", "specialist", "specialiste", "developer",
    "architect", "director", "scout", "consultant", "executive",
    "researcher", "onderzoeker", "chercheur", "investigador", "ricercatore",
    "internship", "trainee", "stagiaire", "stagiair", "stagista",
    "praktikant", "praktikum", "werkstudent", "responsable", "responsabile",
    "responsavel", "verantwortlich", "referent", "jefe", "capo", "chefe", "hoofd",
)
# Short, ambiguous role nouns matched as WHOLE WORDS only — "lead" must not hit
# "leadership", "head" not "headquarters", "intern" not "international".
_ROLE_NOUNS_RE = re.compile(r"\b(lead|head|chief|intern)\b")

# Corporate "data" functions that are never a football-analytics role, even
# though they contain "data" + a role noun (Master Data Management / governance).
_CORP_DATA_NOISE = ("master data", "data governance", "data entry",
                    "reference data", "data protection", "data steward")

# Kept for relevance_score (broad analyst-family, topics included).
_ANALYST_TOKENS = _ANALYST_ROLE + ("analytic", "analytik", "analyse", "analysis")

# "Strong" = unmistakably a data role. These survive the exclude filter even
# when paired with an otherwise-excluded word (e.g. "Data Security Analyst").
_STRONG_LOOSE = ("analytic", "analytik")


def _has_role_noun(text_norm: str) -> bool:
    return (any(n in text_norm for n in _ROLE_NOUNS)
            or bool(_ROLE_NOUNS_RE.search(text_norm)))


def _has_topic(text_norm: str) -> bool:
    return bool(_DATA_RE.search(text_norm)) or any(t in text_norm for t in _TOPIC_TOKENS)

# HARD excludes — never a football-data role, even if the title says "analyst"
# (e.g. "Financial Analyst", "Physiotherapist", "Recovery Scientist").
_HARD_EXCLUDE = (
    "financ", "security", "compliance", "payroll", "procurement",
    "accountant", "accounting", "auditor", "human resources",
    "physio", "physiother", "rehab", "therap", "nutrition", "dietit",
    "masseur", "massage", "medical", "medicine", "physician", "doctor",
    "wellbeing", "well-being", "kinesi", "osteopath", "chiro", "podiat",
    "psycholog", "recovery scientist", "first aid", "soigneur",
)
# Sports-science / performance-physiology area — included ONLY when it leans
# DATA (a data/analytics/analyst signal is also present). So "Sports Science
# Analyst" / "Performance Data Scientist" pass, but a plain "Sports Scientist"
# or "Strength & Conditioning Coach" does not. (The user wants the data-leaning
# sports-science roles, not the physical-performance/medical ones.)
_SPORTSCI_TOKENS = (
    "sports scien", "sport scien", "exercise scien", "sports scientist",
    "sport scientist", "strength and conditioning", "s&c coach",
    "physical performance", "athletic performance",
)
# Back-compat alias (some call sites import EXCLUDE_TOKENS).
EXCLUDE_TOKENS = _HARD_EXCLUDE + _SPORTSCI_TOKENS

# Footer / legal links that mention "data" but are never jobs
# ("Data & Privacy", "Data Protection Policy", cookie notices, …).
_NOISE_TOKENS = (
    "privacy", "cookie", "gdpr", "data protection", "disclaimer",
    "terms of use", "terms and conditions", "data subject",
)


def _has_role_word(text_norm: str) -> bool:
    return any(t in text_norm for t in _ANALYST_ROLE) or "scientist" in text_norm


def _strong_data(text_norm: str) -> bool:
    return bool(_DATA_RE.search(text_norm)) or any(t in text_norm for t in _STRONG_LOOSE)


def match_role(title: str, description: str = "", *, strict: bool = False) -> list[str]:
    """Return matched display terms for a vacancy (empty list = no match).

    Match rules, in order:
      1. an explicit analytics ROLE phrase ("data analyst", "business intelligence", …)
      2. an analyst-family role token ("analyst", "analist", "analytiker", …)
      3. a data/analytics TOPIC word + a job-role noun ("Data Scientist",
         "Analytics Engineer", "Insights Officer")

    A bare topic word ("data", "analyse", "analytics") or a tool ("SQL") never
    matches on its own — that was the source of "CLUB DATA"-style noise.

    strict=True keeps only rule 1 (explicit phrases). Use it when scanning loose
    page text (headings, nav) or rescuing from a description.
    """
    text = _norm(f"{title} {description}")
    if not text.strip():
        return []

    # Hard exclusion: finance / HR / medical roles are never a data job.
    if any(x in text for x in _HARD_EXCLUDE):
        return []

    # Corporate data-governance functions ("Master Data Manager") are not football analytics.
    if any(x in text for x in _CORP_DATA_NOISE):
        return []

    # Sports-science roles count only when they lean data (analyst/data signal).
    if any(x in text for x in _SPORTSCI_TOKENS) and not _has_role_word(text) \
            and not _strong_data(text):
        return []

    # Footer / legal noise ("Data & Privacy"): keep only if a real role word is present.
    if any(n in text for n in _NOISE_TOKENS) and not _has_role_word(text):
        return []

    # Rule 1 — explicit role phrases (best, readable chips).
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

    # Rule 2 — an analyst-family token is a role by itself.
    analyst_hit = [t for t in _ANALYST_ROLE if t in text]
    if analyst_hit:
        return [analyst_hit[0]]

    # Rule 3 — a topic word only counts alongside a job-role noun.
    if _has_topic(text) and _has_role_noun(text):
        topic = next((t for t in _TOPIC_TOKENS if t in text), None)
        if topic is None and _DATA_RE.search(text):
            topic = "data"
        return [topic] if topic else []

    return []


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


# ── Role categories (so "all roles" stays organised & filterable) ─────────────
# Order matters: the first bucket whose signals appear wins.
CATEGORIES = (
    "Data Science & ML",
    "Analytics & Insights",
    "Performance Analysis",
    "Scouting & Recruitment",
    "Sports Science",
)

_CAT_SCOUTING = ("scout", "recruitment analyst", "recruitment data", "talent id",
                 "talent identification", "spielbeobachter", "ojeador")
_CAT_PERF = ("performance analy", "match analy", "video analy", "opposition analy",
             "tactical analy", "set piece analy", "first team analy",
             "wedstrijdanalist", "spelersanalist", "prestatieanalist",
             "spielanalyst", "taktikanalyst", "leistungsanalyst",
             "analyste video", "analyste tactique", "analista video",
             "analista tattico", "analisi tattica", "videoanaly")
_CAT_SPORTSCI = ("sports scien", "sport scien", "exercise scien", "sports scientist",
                 "sport scientist", "physical performance", "athletic performance",
                 "strength and conditioning")
_CAT_DSML = ("data scientist", "data engineer", "machine learning", "research scientist",
             "datawetenschap", "datenwissenschaft", "cientifico de datos",
             "scienziato dei dati", "cientista de dados", "data infrastructure",
             "dateningenieur", "ingenieur donnees", "ingegnere dei dati",
             "ingeniero de datos", "engenheiro de dados", "deep learning",
             "modelling", "modeling")


# Signals that make a match unambiguously about DATA/analytics (→ high confidence).
_HIGH_CONF = (
    "analytic", "analytik", "scientist", "cientifico", "cientista", "scienziato",
    "machine learning", "datawetenschap", "datenwissenschaft", "statsbomb",
    "wyscout", "skillcorner", "instat", "statistic", "statistik",
)


def match_confidence(title: str, description: str = "") -> str | None:
    """'high', 'low', or None — how confident we are the role is football-data.

    HIGH = an explicit data-role phrase, or a 'data' word, or a strong data
    signal (analytics/scientist/ML/tracking-tool) appears in the TITLE.
    LOW  = matched only via a bare analyst-family token (e.g. "Business
    Analyst") or rescued from the description — show it, but badge it.
    """
    if not match_role(title, description):
        return None
    t = _norm(title)
    if any(kw_norm in t for kw_norm, _ in _KEYWORDS_NORM):
        return "high"
    if _DATA_RE.search(t) or any(s in t for s in _HIGH_CONF):
        return "high"
    return "low"


def classify_role(title: str, description: str = "") -> str:
    """Bucket a matched vacancy into a high-level category for filtering."""
    t = _norm(f"{title} {description}")
    if any(s in t for s in _CAT_SCOUTING):
        return "Scouting & Recruitment"
    if any(s in t for s in _CAT_SPORTSCI):
        return "Sports Science"
    if any(s in t for s in _CAT_PERF):
        return "Performance Analysis"
    if any(s in t for s in _CAT_DSML):
        return "Data Science & ML"
    return "Analytics & Insights"
