"""Football Analytics Job Tracker — dashboard."""

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
del _sys, _os

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone

from clubs import CLUBS_BY_LEAGUE as CLUBS
from database import get_last_scraped, get_vacancies, init_db
from scraper import scrape_all_clubs

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Jobs",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

# ── Hide sidebar ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
[data-testid="stMain"]  { padding-top: 0 !important; }
.block-container        { padding: 1.5rem 2.5rem 2rem !important; max-width: 100% !important; }

/* ── Header ──────────────────────────────────────────────────────────────── */
.hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 18px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 24px;
}
.hdr-title {
    font-size: 1.5rem; font-weight: 800; margin: 0;
    letter-spacing: -0.5px; color: #e6edf3;
}
.hdr-title span { color: #58a6ff; }
.hdr-sub  { margin: 3px 0 0; font-size: 0.8rem; color: #6e7681; }
.hdr-sub code { background: #161b22; padding: 1px 5px; border-radius: 4px;
                border: 1px solid #30363d; font-size: 0.77rem; color: #8b949e; }
.hdr-pill {
    display: inline-block; margin-left: 8px;
    padding: 1px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600;
}
.hdr-pill-fresh { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.35); }
.hdr-pill-stale { background: rgba(210,153,34,0.15); color: #d29922;  border: 1px solid rgba(210,153,34,0.35); }

/* ── KPI row ─────────────────────────────────────────────────────────────── */
.kpi-row  { display: flex; gap: 12px; margin-bottom: 28px; }
.kpi {
    flex: 1;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
}
.kpi::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 10px 10px 0 0;
}
.kpi-blue::before  { background: #58a6ff; }
.kpi-green::before { background: #3fb950; }
.kpi-amber::before { background: #d29922; }
.kpi-purple::before{ background: #a371f7; }
.kpi .num { font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.kpi-blue  .num { color: #58a6ff; }
.kpi-green .num { color: #3fb950; }
.kpi-amber .num { color: #d29922; }
.kpi-purple .num { color: #a371f7; }
.kpi .lbl  { font-size: 0.72rem; color: #6e7681; text-transform: uppercase; letter-spacing: 0.07em; }

/* ── Tab override ────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #21262d;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 18px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #6e7681 !important;
    border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #161b22 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-bottom-color: #161b22 !important;
}

/* ── Filter row ──────────────────────────────────────────────────────────── */
.filter-strip {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px 6px;
    margin-bottom: 18px;
}

/* ── League cards ────────────────────────────────────────────────────────── */
.lg-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 14px;
    height: 100%;
}
.lg-hdr  { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.lg-flag { font-size: 1.25rem; }
.lg-name { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.pg-wrap  { background: #21262d; border-radius: 4px; height: 4px; margin-bottom: 5px; overflow: hidden; }
.pg-fill  { height: 100%; border-radius: 4px; }
.pg-lbl   { font-size: 0.68rem; color: #6e7681; margin-bottom: 10px; }
.pills    { display: flex; flex-wrap: wrap; gap: 4px; }
.pill {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.66rem; font-weight: 600;
    padding: 2px 7px; border-radius: 20px; border: 1px solid;
    white-space: nowrap;
}
.pill-on  { background: rgba(63,185,80,0.12);  border-color: rgba(63,185,80,0.4);  color: #3fb950; }
.pill-off { background: rgba(139,148,158,0.06); border-color: #21262d; color: #484f58; }

/* ── Vacancy table tweaks ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #30363d !important; border-radius: 10px !important; }

/* ── Vacancy cards ───────────────────────────────────────────────────────── */
.vc {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}
.vc-title { font-size: 0.98rem; font-weight: 700; margin-bottom: 6px; color: #e6edf3; }
.vc-meta  { display: flex; flex-wrap: wrap; gap: 12px; font-size: 0.77rem; color: #6e7681; margin-bottom: 5px; }
.vc-club  { font-weight: 700; }
.vc-kw    { font-size: 0.68rem; color: #58a6ff; margin-bottom: 5px; }
.vc-link  { font-size: 0.77rem; color: #58a6ff; text-decoration: none; font-weight: 600; }
.vc-link:hover { text-decoration: underline; }

/* ── Badges ──────────────────────────────────────────────────────────────── */
.badge {
    display: inline-block; padding: 1px 7px;
    border-radius: 20px; font-size: 0.67rem; font-weight: 600;
    border: 1px solid;
}
.b-cp { background:rgba(35,134,54,0.2);   border-color:rgba(63,185,80,0.4);  color:#3fb950; }
.b-tt { background:rgba(14,116,144,0.2);  border-color:rgba(6,182,212,0.4);  color:#22d3ee; }
.b-wb { background:rgba(231,76,60,0.2);   border-color:rgba(231,76,60,0.4);  color:#f87171; }
.b-gh { background:rgba(63,185,80,0.2);   border-color:rgba(63,185,80,0.4);  color:#4ade80; }
.b-lv { background:rgba(110,64,201,0.2);  border-color:rgba(163,113,247,0.4);color:#a78bfa; }
.b-lf { background:rgba(180,83,9,0.2);    border-color:rgba(251,146,60,0.4); color:#fb923c; }
.b-li { background:rgba(10,102,194,0.2);  border-color:rgba(96,165,250,0.4); color:#60a5fa; }
.b-pp { background:rgba(168,85,247,0.2);  border-color:rgba(216,180,254,0.4);color:#d8b4fe; }
.b-wt { background:rgba(20,184,166,0.2);  border-color:rgba(45,212,191,0.4); color:#2dd4bf; }
.b-df { background:rgba(75,85,99,0.2);    border-color:#374151; color:#9ca3af; }

/* ── Divider ─────────────────────────────────────────────────────────────── */
.div  { border-bottom: 1px solid #21262d; margin: 20px 0; }

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty { text-align:center; padding:60px 20px; color:#6e7681; }
.empty .ei  { font-size:2.5rem; margin-bottom:10px; }
.empty h3   { color:#e6edf3; margin-bottom:4px; }

/* ── Result count ────────────────────────────────────────────────────────── */
.result-count {
    font-size: 0.8rem; color: #6e7681; margin-bottom: 14px;
}
.result-count strong { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────
CACHE_TTL = 21_600

LEAGUE_META: dict[str, dict] = {
    "Netherlands":              {"flag": "🇳🇱", "color": "#FF6B35"},
    "Belgium":                  {"flag": "🇧🇪", "color": "#F4C430"},
    "Germany":                  {"flag": "🇩🇪", "color": "#E63946"},
    "France":                   {"flag": "🇫🇷", "color": "#4361EE"},
    "Spain - La Liga":          {"flag": "🇪🇸", "color": "#F72585"},
    "Spain - La Liga 2":        {"flag": "🇪🇸", "color": "#C77DFF"},
    "England - Premier League": {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#7209B7"},
    "England - Championship":   {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#9B5DE5"},
    "Italy - Serie A":          {"flag": "🇮🇹", "color": "#3A86FF"},
    "Italy - Serie B":          {"flag": "🇮🇹", "color": "#4CC9F0"},
    "Scotland":                 {"flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "color": "#06D6A0"},
    "Portugal":                 {"flag": "🇵🇹", "color": "#118AB2"},
    "Denmark":                  {"flag": "🇩🇰", "color": "#EF476F"},
}

SOURCE_BADGE = {
    "LinkedIn":      "b-li",
    "Careers Page":  "b-cp",
    "Teamtailor":    "b-tt",
    "Workable":      "b-wb",
    "Greenhouse":    "b-gh",
    "Lever":         "b-lv",
    "LiveFootballJobs": "b-lf",
    "Pinpoint":      "b-pp",
    "Posting Panda": "b-pp",
    "webitrent":     "b-wt",
}

CLUB_LOGO: dict[str, str] = {
    # Netherlands
    "PSV":                       "PSV.png",
    "Ajax":                      "Ajax.png",
    "AZ Alkmaar":                "AZ.png",
    "Feyenoord":                 "Feyenoord.png",
    "FC Utrecht":                "FC Utrecht.png",
    # Belgium
    "Royal Antwerp FC":          "Royal Antwerp.png",
    "Royale Union Saint-Gilloise": "Royale Union SG.png",
    "RSC Anderlecht":            "RSC Anderlecht.png",
    "KRC Genk":                  "KRC Genk.png",
    "Club Brugge":               "Club Brugge.png",
    # Germany
    "FC Bayern Munich":          "Bayern Munich.png",
    "Borussia Dortmund":         "Borussia Dortmund.png",
    "Bayer 04 Leverkusen":       "Bayer Leverkusen.png",
    "RB Leipzig":                "RB Leipzig.png",
    "VfB Stuttgart":             "VfB Stuttgart.png",
    "Eintracht Frankfurt":       "Eintracht Frankfurt.png",
    "SC Freiburg":               "SC Freiburg.png",
    "1. FSV Mainz 05":           "Mainz 05.png",
    "Borussia M\u00c3\u00b6nchengladbach": "Borussia Mgladbach.png",
    "VfL Wolfsburg":             "VfL Wolfsburg.png",
    "FC Augsburg":               "FC Augsburg.png",
    "Werder Bremen":             "Werder Bremen.png",
    "TSG Hoffenheim":            "TSG Hoffenheim.png",
    "1. FC Union Berlin":        "Union Berlin.png",
    "FC St. Pauli":              "FC St Pauli.png",
    "1. FC Heidenheim":          "FC Heidenheim.png",
    "Holstein Kiel":             "Holstein Kiel.png",
    "VfL Bochum":                "VfL Bochum.png",
    "Hamburger SV":              "Hamburger SV.png",
    "1. FC K\u00c3\u00b6ln":     "FC Koeln.png",
    # France
    "Paris Saint-Germain":       "Paris Saint-Germain.png",
    "Olympique de Marseille":    "Olympique Marseille.png",
    "AS Monaco":                 "AS Monaco.png",
    "Olympique Lyonnais":        "Olympique Lyonnais.png",
    "Lille OSC":                 "Lille OSC.png",
    "OGC Nice":                  "OGC Nice.png",
    "RC Lens":                   "RC Lens.png",
    "Stade Rennais FC":          "Stade Rennais.png",
    "Stade Brestois 29":         "Stade Brestois.png",
    "Toulouse FC":               "Toulouse FC.png",
    "RC Strasbourg Alsace":      "RC Strasbourg.png",
    "FC Nantes":                 "FC Nantes.png",
    "Montpellier HSC":           "Montpellier HSC.png",
    "AJ Auxerre":                "AJ Auxerre.png",
    "Le Havre AC":               "Le Havre AC.png",
    "Angers SCO":                "Angers SCO.png",
    "FC Metz":                   "FC Metz.png",
    "FC Lorient":                "FC Lorient.png",
    # Spain - La Liga
    "Real Madrid CF":            "Real Madrid.png",
    "FC Barcelona":              "FC Barcelona.png",
    "Valencia CF":               "Valencia CF.png",
    "Club Atletico de Madrid":   "Atletico Madrid.png",
    "Real Betis Balompie":       "Real Betis.png",
    "Sevilla FC":                "Sevilla FC.png",
    "Real Sociedad":             "Real Sociedad.png",
    "Athletic Club Bilbao":      "Club_Athletic_Bilbao.png",
    "RCD Mallorca":              "RCD Mallorca.png",
    "Villarreal CF":             "Villarreal CF.png",
    "RC Celta de Vigo":          "Celta Vigo.png",
    "CA Osasuna":                "CA Osasuna.png",
    "Rayo Vallecano":            "Rayo Vallecano.png",
    "Girona FC":                 "Girona FC.png",
    "Deportivo Alaves":          "Deportivo Alaves.png",
    "Levante UD":                "Levante UD.png",
    "Real Oviedo":               "Real Oviedo.png",
    # Spain - La Liga 2
    "Real Racing Santander":     "Racing Santander.png",
    "UD Las Palmas":             "UD Las Palmas.png",
    "UD Almeria":                "UD Almeria.png",
    "Malaga CF":                 "Malaga CF.png",
    "CD Castellon":              "CD Castellon.png",
    "RC Deportivo de La Coruna": "RC Deportivo.png",
    "Burgos CF":                 "Burgos CF.png",
    "SD Eibar":                  "SD Eibar.png",
    "Cordoba CF":                "Cordoba CF.png",
    "FC Andorra":                "FC Andorra.png",
    "Real Sporting de Gijon":    "Sporting de Gijon.png",
    "Albacete Balompie":         "Albacete Balompie.png",
    "Granada CF":                "Granada CF.png",
    "Real Valladolid CF":        "Real Valladolid.png",
    "CD Leganes":                "CD Leganes.png",
    "Cadiz CF":                  "Cadiz CF.png",
    "Real Zaragoza":             "Real Zaragoza.png",
    # England - Premier League
    "Arsenal FC":                "Arsenal FC.png",
    "Manchester City FC":        "Manchester City.png",
    "Manchester United FC":      "Manchester United.png",
    "Liverpool FC":              "Liverpool FC.png",
    "Aston Villa FC":            "Aston Villa.png",
    "AFC Bournemouth":           "AFC Bournemouth.png",
    "Brentford FC":              "Brentford FC.png",
    "Brighton & Hove Albion FC": "Brighton Hove Albion.png",
    "Chelsea FC":                "Chelsea FC.png",
    "Everton FC":                "Everton FC.png",
    "Fulham FC":                 "Fulham FC.png",
    "Sunderland AFC":            "Sunderland AFC.png",
    "Newcastle United FC":       "Newcastle United.png",
    "Leeds United FC":           "Leeds United.png",
    "Crystal Palace FC":         "Crystal Palace.png",
    "Nottingham Forest FC":      "Nottingham Forest.png",
    "Tottenham Hotspur FC":      "Tottenham Hotspur.png",
    "West Ham United FC":        "West Ham United.png",
    "Burnley FC":                "Burnley FC.png",
    "Wolverhampton Wanderers FC": "Wolverhampton Wanderers.png",
    # England - Championship
    "Birmingham City FC":        "Birmingham City.png",
    "Blackburn Rovers FC":       "Blackburn Rovers.png",
    "Bristol City FC":           "Bristol City.png",
    "Charlton Athletic FC":      "Charlton Athletic.png",
    "Coventry City FC":          "Coventry City.png",
    "Derby County FC":           "Derby County.png",
    "Hull City AFC":             "Hull City.png",
    "Ipswich Town FC":           "Ipswich Town.png",
    "Leicester City FC":         "Leicester City.png",
    "Middlesbrough FC":          "Middlesbrough.png",
    "Millwall FC":               "Millwall.png",
    "Norwich City FC":           "Norwich City.png",
    "Oxford United FC":          "Oxford United.png",
    "Portsmouth FC":             "Portsmouth.png",
    "Preston North End FC":      "Preston North End.png",
    "Queens Park Rangers FC":    "QPR.png",
    "Sheffield United FC":       "Sheffield United.png",
    "Sheffield Wednesday FC":    "Sheffield Wednesday.png",
    "Southampton FC":            "Southampton.png",
    "Stoke City FC":             "Stoke City.png",
    "Swansea City AFC":          "Swansea City.png",
    "Watford FC":                "Watford.png",
    "West Bromwich Albion FC":   "West Bromwich Albion.png",
    "Wrexham AFC":               "Wrexham.png",
    # Italy - Serie A
    "Inter Milan":               "Inter Milan.png",
    "SSC Napoli":                "SSC Napoli.png",
    "AC Milan":                  "AC Milan.png",
    "Juventus FC":               "Juventus.png",
    "AS Roma":                   "AS Roma.png",
    "Como 1907":                 "Como 1907.png",
    "Atalanta BC":               "Atalanta BC.png",
    "SS Lazio":                  "SS Lazio.png",
    "Bologna FC 1909":           "Bologna FC.png",
    "ACF Fiorentina":            "ACF Fiorentina.png",
    "Torino FC":                 "Torino FC.png",
    "Udinese Calcio":            "Udinese Calcio.png",
    "Parma Calcio 1913":         "Parma Calcio.png",
    "Genoa CFC":                 "Genoa CFC.png",
    "Cagliari Calcio":           "Cagliari Calcio.png",
    "Hellas Verona FC":          "Hellas Verona.png",
    "US Lecce":                  "US Lecce.png",
    "US Cremonese":              "US Cremonese.png",
    "Sassuolo Calcio":           "Sassuolo.png",
    "Pisa SC":                   "Pisa SC.png",
    # Italy - Serie B
    "US Avellino":               "US Avellino.png",
    "SSC Bari":                  "SSC Bari.png",
    "Carrarese Calcio":          "Carrarese Calcio.png",
    "US Catanzaro":              "US Catanzaro.png",
    "Cesena FC":                 "AC Cesena.png",
    "Empoli FC":                 "Empoli FC.png",
    "Frosinone Calcio":          "Frosinone Calcio.png",
    "SS Juve Stabia":            "SS Juve Stabia.png",
    "Mantova 1911":              "Mantova 1911.png",
    "Modena FC":                 "Modena FC.png",
    "AC Monza":                  "AC Monza.png",
    "Calcio Padova":             "Calcio Padova.png",
    "Palermo FC":                "Palermo FC.png",
    "Delfino Pescara":           "Delfino Pescara.png",
    "AC Reggiana":               "AC Reggiana.png",
    "UC Sampdoria":              "UC Sampdoria.png",
    "Spezia Calcio":             "Spezia Calcio.png",
    "FC Sudtirol":               "FC Sudtirol.png",
    "Venezia FC":                "Venezia FC.png",
    "Virtus Entella":            "Virtus Entella.png",
    # Scotland
    "Rangers FC":                "Rangers FC.png",
    "Celtic FC":                 "Celtic FC.png",
    # Portugal
    "SL Benfica":                "SL Benfica.png",
    "Sporting CP":               "Sporting CP.png",
    "FC Porto":                  "FC Porto.png",
    # Denmark
    "FC Copenhagen":             "FC Copenhagen.png",
    "FC Midtjylland":            "FC Midtjylland.png",
}

ALL_LEAGUES   = list(CLUBS.keys())
ALL_COUNTRIES = sorted({lg.split(" - ")[0] if " - " in lg else lg for lg in ALL_LEAGUES})


# ── Helpers ──────────────────────────────────────────────────────────────────

def _country_of(lg: str) -> str:
    return lg.split(" - ")[0] if " - " in lg else lg


@st.cache_data(ttl=CACHE_TTL)
def _load_vacancies() -> list[dict]:
    return get_vacancies()


def _stale(last: str | None) -> bool:
    if not last:
        return True
    try:
        ts = datetime.fromisoformat(last)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() > CACHE_TTL
    except ValueError:
        return True


def _badge(source: str) -> str:
    css = SOURCE_BADGE.get(source, "b-df")
    return f'<span class="badge {css}">{source}</span>'


def _logo_img(club: str, size: int = 28) -> str:
    fname = CLUB_LOGO.get(club)
    if not fname:
        return ""
    from urllib.parse import quote
    encoded = quote(fname)
    return (
        f'<img src="/app/static/logos/{encoded}" '
        f'style="width:{size}px;height:{size}px;object-fit:contain;'
        f'border-radius:3px;background:#fff;padding:1px;vertical-align:middle;">'
    )


def _run_scrape(placeholder) -> None:
    _load_vacancies.clear()
    with placeholder.container():
        prog = st.progress(0.0, text="Starting scraper…")
        def cb(f: float, msg: str) -> None:
            prog.progress(min(f, 1.0), text=msg)
        result = scrape_all_clubs(progress_callback=cb)
        st.success(
            f"Done — **{result['total']}** vacancies found across {result['clubs_scraped']} clubs.",
            icon="✅",
        )
        if result["errors"]:
            with st.expander(f"{len(result['errors'])} clubs had errors"):
                for club, msg in result["errors"].items():
                    st.caption(f"• **{club}**: {msg}")
    _load_vacancies.clear()
    st.rerun()


def _league_card(league: str, clubs: list[dict], clubs_with_jobs: set[str]) -> str:
    meta  = LEAGUE_META.get(league, {"flag": "🌍", "color": "#58a6ff"})
    color = meta["color"]
    flag  = meta["flag"]
    found = sum(1 for c in clubs if c["name"] in clubs_with_jobs)
    total = len(clubs)
    pct   = int(found / total * 100) if total else 0
    short = league.replace("England - ", "").replace("Spain - ", "").replace("Italy - ", "")
    pills = "".join(
        f'<span class="pill {"pill-on" if c["name"] in clubs_with_jobs else "pill-off"}">'
        f'{_logo_img(c["name"], 14)}{c["name"]}</span>'
        for c in clubs
    )
    return f"""
    <div class="lg-card" style="border-top:3px solid {color};">
      <div class="lg-hdr">
        <span class="lg-flag">{flag}</span>
        <span class="lg-name" style="color:{color};">{short}</span>
        <span style="margin-left:auto;font-size:0.72rem;color:#6e7681;">{found}/{total}</span>
      </div>
      <div class="pg-wrap"><div class="pg-fill" style="width:{pct}%;background:{color};"></div></div>
      <div class="pg-lbl">{pct}% of clubs have open roles</div>
      <div class="pills">{pills}</div>
    </div>
    """


# ── Header ───────────────────────────────────────────────────────────────────
last     = get_last_scraped()
last_str = last[:16] if last else "never"
stale    = _stale(last)
pill_cls = "hdr-pill-stale" if stale else "hdr-pill-fresh"
pill_txt = "⚠ stale" if stale else "✓ live"

hcol1, hcol2 = st.columns([4, 1])
with hcol1:
    st.markdown(f"""
    <div class="hdr">
      <div>
        <div class="hdr-title">⚽ Football Analytics <span>Jobs</span></div>
        <div class="hdr-sub">
          Data science, analytics &amp; performance analysis roles across European clubs
          &nbsp;·&nbsp; Last scan: <code>{last_str} UTC</code>
          <span class="hdr-pill {pill_cls}">{pill_txt}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with hcol2:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    refresh_clicked = st.button("🔄 Refresh data", type="primary", use_container_width=True)

scrape_placeholder = st.empty()
if refresh_clicked:
    _run_scrape(scrape_placeholder)

# ── Load data ─────────────────────────────────────────────────────────────────
raw_vacancies   = _load_vacancies()
clubs_with_jobs = {v["club_name"] for v in raw_vacancies}
total_clubs     = sum(len(c) for c in CLUBS.values())
leagues_active  = len({v["league"] for v in raw_vacancies})

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi kpi-blue">
    <div class="num">{len(raw_vacancies)}</div>
    <div class="lbl">Open vacancies</div>
  </div>
  <div class="kpi kpi-green">
    <div class="num">{len(clubs_with_jobs)}</div>
    <div class="lbl">Clubs hiring</div>
  </div>
  <div class="kpi kpi-amber">
    <div class="num">{total_clubs - len(clubs_with_jobs)}</div>
    <div class="lbl">No openings</div>
  </div>
  <div class="kpi kpi-purple">
    <div class="num">{leagues_active}</div>
    <div class="lbl">Leagues with roles</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_vac, tab_overview = st.tabs(["💼  Vacancies", "🗺️  League Overview"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – Vacancies
# ════════════════════════════════════════════════════════════════════════════
with tab_vac:
    if not raw_vacancies:
        st.markdown("""
        <div class="empty">
          <div class="ei">💼</div>
          <h3>No vacancies yet</h3>
          <p>Click <strong>Refresh data</strong> to start scraping.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Filter strip ──────────────────────────────────────────────────
        st.markdown('<div class="filter-strip">', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.5, 1.2, 1.5, 1])

        with fc1:
            sel_leagues = st.multiselect(
                "League", options=ALL_LEAGUES, default=[],
                placeholder="All leagues",
            )
        with fc2:
            avail_clubs = sorted({
                c["name"] for lg in (sel_leagues or ALL_LEAGUES)
                for c in CLUBS.get(lg, [])
            })
            sel_clubs = st.multiselect(
                "Club", options=avail_clubs, default=[],
                placeholder="All clubs",
            )
        with fc3:
            all_sources = sorted({v["source"] for v in raw_vacancies})
            sel_source = st.selectbox("Source", ["All"] + all_sources)
        with fc4:
            kw = st.text_input("Keyword", placeholder="e.g. python, SQL, analyst…")
        with fc5:
            recent = st.toggle("Last 30 days", value=False)
            view   = st.radio("View", ["Table", "Cards"], horizontal=True,
                              label_visibility="collapsed")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Filter data ───────────────────────────────────────────────────
        df = pd.DataFrame(raw_vacancies)

        if sel_leagues:
            df = df[df["league"].isin(sel_leagues)]
        if sel_clubs:
            df = df[df["club_name"].isin(sel_clubs)]
        if sel_source != "All":
            df = df[df["source"] == sel_source]
        if kw.strip():
            mask = (
                df["job_title"].str.contains(kw, case=False, na=False)
                | df["keywords_matched"].str.contains(kw, case=False, na=False)
            )
            df = df[mask]
        if recent:
            cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            df = df[df["posted_date"].notna() & (df["posted_date"] >= cutoff)]

        st.markdown(
            f'<div class="result-count">Showing <strong>{len(df)}</strong> '
            f'of {len(raw_vacancies)} vacancies</div>',
            unsafe_allow_html=True,
        )

        if df.empty:
            st.markdown("""
            <div class="empty">
              <div class="ei">🎯</div>
              <h3>No results</h3><p>Try widening your filters.</p>
            </div>""", unsafe_allow_html=True)

        elif view == "Table":
            cols_map = {
                "job_title":  "Job Title",
                "club_name":  "Club",
                "league":     "League",
                "source":     "Source",
                "posted_date":"Posted",
                "keywords_matched": "Keywords",
                "url":        "Link",
            }
            disp = df[list(cols_map)].rename(columns=cols_map).copy()

            def _row_bg(row: pd.Series) -> list[str]:
                c = LEAGUE_META.get(row["League"], {}).get("color", "#333")
                h = c.lstrip("#")
                r2, g2, b2 = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                return [f"background-color:rgba({r2},{g2},{b2},0.07)"] * len(row)

            st.dataframe(
                disp.style.apply(_row_bg, axis=1),
                column_config={
                    "Link": st.column_config.LinkColumn("Link", display_text="Open ↗"),
                    "Job Title": st.column_config.TextColumn("Job Title", width="large"),
                    "Keywords":  st.column_config.TextColumn("Keywords",  width="medium"),
                    "Club":      st.column_config.TextColumn("Club",       width="medium"),
                },
                use_container_width=True,
                hide_index=True,
                height=min(60 + 38 * len(disp), 700),
            )

        else:  # Cards
            for _, row in df.iterrows():
                color  = LEAGUE_META.get(row["league"], {}).get("color", "#58a6ff")
                badge  = _badge(row["source"])
                date   = f"📅 {row['posted_date']}" if row.get("posted_date") else ""
                kw_str = row.get("keywords_matched", "")
                url    = row.get("url", "#")
                logo   = _logo_img(row["club_name"], 36)
                st.markdown(f"""
                <div class="vc" style="border-left-color:{color};">
                  <div style="display:flex;align-items:flex-start;gap:10px;">
                    {f'<div style="flex-shrink:0;padding-top:2px;">{logo}</div>' if logo else ''}
                    <div style="flex:1;">
                      <div class="vc-title">{row['job_title']}</div>
                      <div class="vc-meta">
                        <span class="vc-club" style="color:{color};">{row['club_name']}</span>
                        <span>{row['league']}</span>
                        {badge}
                        {date}
                      </div>
                      {"<div class='vc-kw'>🏷 " + kw_str + "</div>" if kw_str else ""}
                      <a class="vc-link" href="{url}" target="_blank">Open posting ↗</a>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – League Overview
# ════════════════════════════════════════════════════════════════════════════
with tab_overview:
    if not raw_vacancies:
        st.markdown("""
        <div class="empty">
          <div class="ei">🔍</div>
          <h3>No data yet</h3>
          <p>Click <strong>Refresh data</strong> above to start scraping.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.caption("Green pills = club has at least one open analytics role")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Row 1: Scotland · PL · Championship · Denmark
        r1 = st.columns(4)
        for col, lg in zip(r1, ["Scotland", "England - Premier League",
                                 "England - Championship", "Denmark"]):
            with col:
                st.markdown(_league_card(lg, CLUBS[lg], clubs_with_jobs),
                            unsafe_allow_html=True)

        # Row 2: Netherlands · Germany · Belgium
        r2 = st.columns([1, 2, 1])
        with r2[0]:
            st.markdown(_league_card("Netherlands", CLUBS["Netherlands"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r2[1]:
            st.markdown(_league_card("Germany", CLUBS["Germany"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r2[2]:
            st.markdown(_league_card("Belgium", CLUBS["Belgium"], clubs_with_jobs),
                        unsafe_allow_html=True)

        # Row 3: France · Portugal
        r3 = st.columns([2, 1])
        with r3[0]:
            st.markdown(_league_card("France", CLUBS["France"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r3[1]:
            st.markdown(_league_card("Portugal", CLUBS["Portugal"], clubs_with_jobs),
                        unsafe_allow_html=True)

        # Row 4: Spain La Liga · Spain La Liga 2 · Italy SA · Italy SB
        r4 = st.columns(4)
        for col, lg in zip(r4, ["Spain - La Liga", "Spain - La Liga 2",
                                  "Italy - Serie A", "Italy - Serie B"]):
            with col:
                st.markdown(_league_card(lg, CLUBS[lg], clubs_with_jobs),
                            unsafe_allow_html=True)


