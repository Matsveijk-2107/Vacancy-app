"""Visual theme for the dashboard: palette, league metadata, club logos, CSS.

Kept separate from app.py so the page logic stays readable and the large
lookup tables / stylesheet live in one place.
"""

from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path

try:
    from PIL import Image
    _HAS_PIL = True
except Exception:                      # pragma: no cover
    _HAS_PIL = False

_LOGO_DIR = Path(__file__).parent / "static" / "logos"
_LOGO_PX  = 64   # thumbnail size embedded (display is 14–38px, so this is crisp)


@lru_cache(maxsize=512)
def _logo_data_uri(fname: str) -> str:
    """Return a small base64 data URI for a logo, or '' if unavailable.

    Embedding the logo in the HTML removes any dependency on Streamlit static
    serving (which needs repo-root config on Streamlit Cloud and is awkward
    behind the app's auth gate). Logos are downscaled to a thumbnail so the
    embedded payload stays light despite the source PNGs being up to ~200KB.
    """
    path = _LOGO_DIR / fname
    if not path.exists():
        return ""
    try:
        if _HAS_PIL:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((_LOGO_PX, _LOGO_PX))
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            raw = buf.getvalue()
        else:
            raw = path.read_bytes()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    except Exception:
        return ""

# ── League colours & flags ───────────────────────────────────────────────────
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

DEFAULT_LEAGUE_COLOR = "#58a6ff"


def league_color(league: str) -> str:
    return LEAGUE_META.get(league, {}).get("color", DEFAULT_LEAGUE_COLOR)


# ── Source badges ─────────────────────────────────────────────────────────────
SOURCE_BADGE = {
    "LinkedIn":         "b-li",
    "Careers Page":     "b-cp",
    "Teamtailor":       "b-tt",
    "Workable":         "b-wb",
    "Greenhouse":       "b-gh",
    "Lever":            "b-lv",
    "LiveFootballJobs": "b-lf",
    "Pinpoint":         "b-pp",
    "Posting Panda":    "b-pp",
    "webitrent":        "b-wt",
    "Workday":          "b-wd",
    "Personio":         "b-pn",
    "Talos":            "b-ts",
    "Web Search":       "b-ws",
    "SuccessFactors":   "b-sf",
    "Adzuna":           "b-az",
}


def badge(source: str) -> str:
    css = SOURCE_BADGE.get(source, "b-df")
    return f'<span class="badge {css}">{source}</span>'


# ── Club logos (file names live in static/logos/) ────────────────────────────
CLUB_LOGO: dict[str, str] = {
    # Netherlands
    "PSV": "PSV.png", "Ajax": "Ajax.png", "AZ Alkmaar": "AZ.png",
    "Feyenoord": "Feyenoord.png", "FC Utrecht": "FC Utrecht.png",
    # Belgium
    "Royal Antwerp FC": "Royal Antwerp.png",
    "Royale Union Saint-Gilloise": "Royale Union SG.png",
    "RSC Anderlecht": "RSC Anderlecht.png", "KRC Genk": "KRC Genk.png",
    "Club Brugge": "Club Brugge.png",
    # Germany
    "FC Bayern Munich": "Bayern Munich.png",
    "Borussia Dortmund": "Borussia Dortmund.png",
    "Bayer 04 Leverkusen": "Bayer Leverkusen.png",
    "RB Leipzig": "RB Leipzig.png", "VfB Stuttgart": "VfB Stuttgart.png",
    "Eintracht Frankfurt": "Eintracht Frankfurt.png",
    "SC Freiburg": "SC Freiburg.png", "1. FSV Mainz 05": "Mainz 05.png",
    "Borussia MÃ¶nchengladbach": "Borussia Mgladbach.png",
    "VfL Wolfsburg": "VfL Wolfsburg.png", "FC Augsburg": "FC Augsburg.png",
    "Werder Bremen": "Werder Bremen.png", "TSG Hoffenheim": "TSG Hoffenheim.png",
    "1. FC Union Berlin": "Union Berlin.png", "FC St. Pauli": "FC St Pauli.png",
    "1. FC Heidenheim": "FC Heidenheim.png", "Holstein Kiel": "Holstein Kiel.png",
    "VfL Bochum": "VfL Bochum.png", "Hamburger SV": "Hamburger SV.png",
    "1. FC KÃ¶ln": "FC Koeln.png",
    # France
    "Paris Saint-Germain": "Paris Saint-Germain.png",
    "Olympique de Marseille": "Olympique Marseille.png",
    "AS Monaco": "AS Monaco.png", "Olympique Lyonnais": "Olympique Lyonnais.png",
    "Lille OSC": "Lille OSC.png", "OGC Nice": "OGC Nice.png",
    "RC Lens": "RC Lens.png", "Stade Rennais FC": "Stade Rennais.png",
    "Stade Brestois 29": "Stade Brestois.png", "Toulouse FC": "Toulouse FC.png",
    "RC Strasbourg Alsace": "RC Strasbourg.png", "FC Nantes": "FC Nantes.png",
    "Montpellier HSC": "Montpellier HSC.png", "AJ Auxerre": "AJ Auxerre.png",
    "Le Havre AC": "Le Havre AC.png", "Angers SCO": "Angers SCO.png",
    "FC Metz": "FC Metz.png", "FC Lorient": "FC Lorient.png",
    # Spain - La Liga
    "Real Madrid CF": "Real Madrid.png", "FC Barcelona": "FC Barcelona.png",
    "Valencia CF": "Valencia CF.png",
    "Club Atletico de Madrid": "Atletico Madrid.png",
    "Real Betis Balompie": "Real Betis.png", "Sevilla FC": "Sevilla FC.png",
    "Real Sociedad": "Real Sociedad.png",
    "Athletic Club Bilbao": "Club_Athletic_Bilbao.png",
    "RCD Mallorca": "RCD Mallorca.png", "Villarreal CF": "Villarreal CF.png",
    "RC Celta de Vigo": "Celta Vigo.png", "CA Osasuna": "CA Osasuna.png",
    "Rayo Vallecano": "Rayo Vallecano.png", "Girona FC": "Girona FC.png",
    "Deportivo Alaves": "Deportivo Alaves.png", "Levante UD": "Levante UD.png",
    "Real Oviedo": "Real Oviedo.png",
    # Spain - La Liga 2
    "Real Racing Santander": "Racing Santander.png",
    "UD Las Palmas": "UD Las Palmas.png", "UD Almeria": "UD Almeria.png",
    "Malaga CF": "Malaga CF.png", "CD Castellon": "CD Castellon.png",
    "RC Deportivo de La Coruna": "RC Deportivo.png", "Burgos CF": "Burgos CF.png",
    "SD Eibar": "SD Eibar.png", "Cordoba CF": "Cordoba CF.png",
    "FC Andorra": "FC Andorra.png",
    "Real Sporting de Gijon": "Sporting de Gijon.png",
    "Albacete Balompie": "Albacete Balompie.png", "Granada CF": "Granada CF.png",
    "Real Valladolid CF": "Real Valladolid.png", "CD Leganes": "CD Leganes.png",
    "Cadiz CF": "Cadiz CF.png", "Real Zaragoza": "Real Zaragoza.png",
    # England - Premier League
    "Arsenal FC": "Arsenal FC.png", "Manchester City FC": "Manchester City.png",
    "Manchester United FC": "Manchester United.png",
    "Liverpool FC": "Liverpool FC.png", "Aston Villa FC": "Aston Villa.png",
    "AFC Bournemouth": "AFC Bournemouth.png", "Brentford FC": "Brentford FC.png",
    "Brighton & Hove Albion FC": "Brighton Hove Albion.png",
    "Chelsea FC": "Chelsea FC.png", "Everton FC": "Everton FC.png",
    "Fulham FC": "Fulham FC.png", "Sunderland AFC": "Sunderland AFC.png",
    "Newcastle United FC": "Newcastle United.png",
    "Leeds United FC": "Leeds United.png", "Crystal Palace FC": "Crystal Palace.png",
    "Nottingham Forest FC": "Nottingham Forest.png",
    "Tottenham Hotspur FC": "Tottenham Hotspur.png",
    "West Ham United FC": "West Ham United.png", "Burnley FC": "Burnley FC.png",
    "Wolverhampton Wanderers FC": "Wolverhampton Wanderers.png",
    # England - Championship
    "Birmingham City FC": "Birmingham City.png",
    "Blackburn Rovers FC": "Blackburn Rovers.png",
    "Bristol City FC": "Bristol City.png",
    "Charlton Athletic FC": "Charlton Athletic.png",
    "Coventry City FC": "Coventry City.png", "Derby County FC": "Derby County.png",
    "Hull City AFC": "Hull City.png", "Ipswich Town FC": "Ipswich Town.png",
    "Leicester City FC": "Leicester City.png",
    "Middlesbrough FC": "Middlesbrough.png", "Millwall FC": "Millwall.png",
    "Norwich City FC": "Norwich City.png", "Oxford United FC": "Oxford United.png",
    "Portsmouth FC": "Portsmouth.png",
    "Preston North End FC": "Preston North End.png",
    "Queens Park Rangers FC": "QPR.png",
    "Sheffield United FC": "Sheffield United.png",
    "Sheffield Wednesday FC": "Sheffield Wednesday.png",
    "Southampton FC": "Southampton.png", "Stoke City FC": "Stoke City.png",
    "Swansea City AFC": "Swansea City.png", "Watford FC": "Watford.png",
    "West Bromwich Albion FC": "West Bromwich Albion.png", "Wrexham AFC": "Wrexham.png",
    # Italy - Serie A
    "Inter Milan": "Inter Milan.png", "SSC Napoli": "SSC Napoli.png",
    "AC Milan": "AC Milan.png", "Juventus FC": "Juventus.png",
    "AS Roma": "AS Roma.png", "Como 1907": "Como 1907.png",
    "Atalanta BC": "Atalanta BC.png", "SS Lazio": "SS Lazio.png",
    "Bologna FC 1909": "Bologna FC.png", "ACF Fiorentina": "ACF Fiorentina.png",
    "Torino FC": "Torino FC.png", "Udinese Calcio": "Udinese Calcio.png",
    "Parma Calcio 1913": "Parma Calcio.png", "Genoa CFC": "Genoa CFC.png",
    "Cagliari Calcio": "Cagliari Calcio.png", "Hellas Verona FC": "Hellas Verona.png",
    "US Lecce": "US Lecce.png", "US Cremonese": "US Cremonese.png",
    "Sassuolo Calcio": "Sassuolo.png", "Pisa SC": "Pisa SC.png",
    # Italy - Serie B
    "US Avellino": "US Avellino.png", "SSC Bari": "SSC Bari.png",
    "Carrarese Calcio": "Carrarese Calcio.png", "US Catanzaro": "US Catanzaro.png",
    "Cesena FC": "AC Cesena.png", "Empoli FC": "Empoli FC.png",
    "Frosinone Calcio": "Frosinone Calcio.png", "SS Juve Stabia": "SS Juve Stabia.png",
    "Mantova 1911": "Mantova 1911.png", "Modena FC": "Modena FC.png",
    "AC Monza": "AC Monza.png", "Calcio Padova": "Calcio Padova.png",
    "Palermo FC": "Palermo FC.png", "Delfino Pescara": "Delfino Pescara.png",
    "AC Reggiana": "AC Reggiana.png", "UC Sampdoria": "UC Sampdoria.png",
    "Spezia Calcio": "Spezia Calcio.png", "FC Sudtirol": "FC Sudtirol.png",
    "Venezia FC": "Venezia FC.png", "Virtus Entella": "Virtus Entella.png",
    # Scotland
    "Rangers FC": "Rangers FC.png", "Celtic FC": "Celtic FC.png",
    # Portugal
    "SL Benfica": "SL Benfica.png", "Sporting CP": "Sporting CP.png",
    "FC Porto": "FC Porto.png",
    # Denmark
    "FC Copenhagen": "FC Copenhagen.png", "FC Midtjylland": "FC Midtjylland.png",
}


# Skip these tokens when building a club monogram fallback.
_MONOGRAM_SKIP = {"fc", "afc", "cf", "sc", "sv", "ac", "as", "ss", "us", "ud",
                  "rc", "sd", "cd", "club", "de", "of", "the", "1907", "1909",
                  "1911", "1913", "04", "05", "29"}
_MONOGRAM_COLORS = ("#1f6feb", "#238636", "#9e6a03", "#8957e5", "#bc4c00",
                    "#0e7490", "#a40e26", "#1a7f64")


def _monogram(club: str) -> str:
    words = [w for w in club.replace(".", " ").split()
             if w.lower() not in _MONOGRAM_SKIP and w[:1].isalpha()]
    words = words or club.split()
    initials = "".join(w[0] for w in words[:2]).upper() or "?"
    color = _MONOGRAM_COLORS[sum(map(ord, club)) % len(_MONOGRAM_COLORS)]
    return initials, color


def logo_img(club: str, size: int = 28) -> str:
    fname = CLUB_LOGO.get(club)
    if fname:
        uri = _logo_data_uri(fname)
        if uri:
            return (
                f'<img src="{uri}" loading="lazy" '
                f'style="width:{size}px;height:{size}px;object-fit:contain;'
                f'border-radius:4px;background:#fff;padding:1px;vertical-align:middle;">'
            )
    # Fallback: colored monogram so every card has a consistent visual anchor.
    initials, color = _monogram(club)
    fs = max(9, int(size * 0.4))
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:{size}px;height:{size}px;border-radius:4px;background:{color};'
        f'color:#fff;font-size:{fs}px;font-weight:700;vertical-align:middle;'
        f'font-family:-apple-system,sans-serif;">{initials}</span>'
    )


# ── Stylesheet ────────────────────────────────────────────────────────────────
CSS = """
<style>
/* Hide Streamlit chrome: sidebar, top header/toolbar, main menu, footer */
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stHeader"]         { display: none !important; }
[data-testid="stToolbar"]        { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stStatusWidget"]   { display: none !important; }
#MainMenu, footer                { display: none !important; }

/* ── Reset & base ──────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1200px 600px at 80% -10%, rgba(88,166,255,0.06), transparent 60%),
        radial-gradient(900px 500px at -10% 0%, rgba(163,113,247,0.05), transparent 55%),
        #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
[data-testid="stMain"]  { padding-top: 0 !important; }
.block-container        { padding: 1.6rem 2.5rem 3rem !important; max-width: 1480px !important; }
/* Tighten Streamlit's default vertical gaps between blocks */
[data-testid="stVerticalBlock"] { gap: 0.55rem; }
::-webkit-scrollbar       { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* ── Header ────────────────────────────────────────────────────────────── */
.hdr {
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 0 18px; border-bottom: 1px solid #21262d; margin-bottom: 24px;
}
.hdr-title { font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; color: #e6edf3; }
.hdr-title span { color: #58a6ff; }
.hdr-sub  { margin: 3px 0 0; font-size: 0.8rem; color: #6e7681; }
.hdr-sub code { background: #161b22; padding: 1px 5px; border-radius: 4px;
                border: 1px solid #30363d; font-size: 0.77rem; color: #8b949e; }
.hdr-pill { display: inline-block; margin-left: 8px; padding: 1px 8px;
            border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.hdr-pill-fresh { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.35); }
.hdr-pill-stale { background: rgba(210,153,34,0.15); color: #d29922;  border: 1px solid rgba(210,153,34,0.35); }

/* ── KPI row ───────────────────────────────────────────────────────────── */
.kpi-row  { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 28px; }
.kpi { flex: 1 1 160px; background: #161b22; border: 1px solid #30363d; border-radius: 10px;
       padding: 16px 20px; position: relative; overflow: hidden; transition: border-color .15s; }
.kpi:hover { border-color: #484f58; }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 10px 10px 0 0; }
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

/* ── Tabs ──────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #21262d; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; border-radius: 6px 6px 0 0 !important;
    padding: 8px 18px !important; font-size: 0.88rem !important; font-weight: 600 !important;
    color: #6e7681 !important; border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #161b22 !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-bottom-color: #161b22 !important;
}
/* Recolor Streamlit's default (red) active-tab indicator to match the accent */
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #58a6ff !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"]    { background-color: #21262d !important; }

/* ── Filter panel (real keyed container .st-key-filterbar) ─────────────── */
.st-key-filterbar {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 14px 18px 16px !important;
    margin-bottom: 18px;
}
.st-key-filterbar [data-testid="stVerticalBlock"] { gap: 0.4rem; }
/* Widget labels: small, uppercase, muted — consistent across the panel */
.st-key-filterbar label p,
.st-key-filterbar [data-testid="stWidgetLabel"] p {
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.05em; color: #8b949e !important;
}

/* ── Native widget theming (BaseWeb) ───────────────────────────────────── */
/* Text input + the closed selectbox/multiselect control share this look */
[data-baseweb="input"], [data-baseweb="select"] > div,
.stTextInput input, [data-testid="stTextInputRootElement"] {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-testid="stTextInputRootElement"]:focus-within {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.25) !important;
}
.stTextInput input::placeholder { color: #6e7681 !important; }
[data-baseweb="input"] input { background: transparent !important; color: #e6edf3 !important; }

/* Dropdown popovers (selectbox / multiselect option lists) */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px rgba(1,4,9,0.6) !important;
}
[data-baseweb="menu"] li:hover,
[role="option"]:hover { background: #21262d !important; }

/* Multiselect chosen tags */
[data-baseweb="tag"] {
    background: rgba(88,166,255,0.15) !important;
    border: 1px solid rgba(88,166,255,0.4) !important;
    color: #cfe3ff !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #cfe3ff !important; }

/* Radio (View: Cards/Table) → segmented look */
.st-key-filterbar [role="radiogroup"] {
    display: inline-flex; gap: 0; background: #0d1117;
    border: 1px solid #30363d; border-radius: 8px; padding: 2px;
}
.st-key-filterbar [role="radiogroup"] label {
    margin: 0 !important; padding: 4px 12px !important; border-radius: 6px;
    cursor: pointer; transition: background .12s;
}
.st-key-filterbar [role="radiogroup"] label:has(input:checked) {
    background: #21262d;
}
.st-key-filterbar [role="radiogroup"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.8rem !important; color: #e6edf3 !important;
}
/* hide the radio dots — the highlighted segment is the indicator */
.st-key-filterbar [role="radiogroup"] [data-baseweb="radio"] > div:first-child { display: none !important; }

/* Toggle accent */
[data-baseweb="checkbox"] [aria-checked="true"] { background: #2563eb !important; }

/* Primary button (Refresh) */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(180deg, #2f81f7, #1f6feb) !important;
    border: 1px solid #1f6feb !important; border-radius: 8px !important;
    font-weight: 600 !important; box-shadow: 0 1px 0 rgba(1,4,9,0.4) !important;
}
[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.08); }

/* ── League cards ──────────────────────────────────────────────────────── */
.lg-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px;
           padding: 14px 16px; margin-bottom: 14px; height: 100%; }
.lg-hdr  { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.lg-flag { font-size: 1.25rem; }
.lg-name { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.pg-wrap  { background: #21262d; border-radius: 4px; height: 4px; margin-bottom: 5px; overflow: hidden; }
.pg-fill  { height: 100%; border-radius: 4px; }
.pg-lbl   { font-size: 0.68rem; color: #6e7681; margin-bottom: 10px; }
.pills    { display: flex; flex-wrap: wrap; gap: 4px; }
.pill { display: inline-flex; align-items: center; gap: 4px; font-size: 0.66rem; font-weight: 600;
        padding: 2px 7px; border-radius: 20px; border: 1px solid; white-space: nowrap; }
.pill-on  { background: rgba(63,185,80,0.12);  border-color: rgba(63,185,80,0.4);  color: #3fb950; }
.pill-off { background: rgba(139,148,158,0.06); border-color: #21262d; color: #484f58; }

/* ── DataFrame ─────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #30363d !important; border-radius: 10px !important; }

/* ── Vacancy cards ─────────────────────────────────────────────────────── */
.vc { background: #161b22; border: 1px solid #30363d; border-left: 4px solid;
      border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; transition: border-color .15s, transform .15s; }
.vc:hover { border-color: #484f58; transform: translateY(-1px); }
.vc-title { font-size: 0.98rem; font-weight: 700; margin-bottom: 6px; color: #e6edf3; }
.vc-meta  { display: flex; flex-wrap: wrap; gap: 12px; font-size: 0.77rem; color: #6e7681; margin-bottom: 5px; }
.vc-club  { font-weight: 700; }
.vc-kw    { font-size: 0.68rem; color: #58a6ff; margin-bottom: 5px; }
.vc-link  { font-size: 0.77rem; color: #58a6ff; text-decoration: none; font-weight: 600; }
.vc-link:hover { text-decoration: underline; }

/* Card action buttons (query-param links → no Streamlit re-render per row) */
.vc-actions { display: flex; flex-direction: column; gap: 6px; align-items: center; justify-content: center; }
.vc-act { display: inline-flex; align-items: center; justify-content: center;
          width: 30px; height: 30px; border-radius: 7px; text-decoration: none;
          border: 1px solid #30363d; background: #21262d; font-size: 0.9rem;
          transition: background .12s, border-color .12s, transform .12s; }
.vc-act:hover { background: #30363d; border-color: #58a6ff; transform: scale(1.08); }
.vc-act-star.on { background: rgba(210,153,34,0.18); border-color: rgba(210,153,34,0.5); }

/* "NEW" / posted-date chips on cards */
.vc-new { display:inline-block; padding:0 7px; border-radius:20px; font-size:0.63rem;
          font-weight:700; letter-spacing:0.04em; background:rgba(63,185,80,0.18);
          color:#3fb950; border:1px solid rgba(63,185,80,0.45); text-transform:uppercase; }

/* ── Badges ────────────────────────────────────────────────────────────── */
.badge { display: inline-block; padding: 1px 7px; border-radius: 20px;
         font-size: 0.67rem; font-weight: 600; border: 1px solid; }
.b-cp { background:rgba(35,134,54,0.2);   border-color:rgba(63,185,80,0.4);  color:#3fb950; }
.b-tt { background:rgba(14,116,144,0.2);  border-color:rgba(6,182,212,0.4);  color:#22d3ee; }
.b-wb { background:rgba(231,76,60,0.2);   border-color:rgba(231,76,60,0.4);  color:#f87171; }
.b-gh { background:rgba(63,185,80,0.2);   border-color:rgba(63,185,80,0.4);  color:#4ade80; }
.b-lv { background:rgba(110,64,201,0.2);  border-color:rgba(163,113,247,0.4);color:#a78bfa; }
.b-lf { background:rgba(180,83,9,0.2);    border-color:rgba(251,146,60,0.4); color:#fb923c; }
.b-li { background:rgba(10,102,194,0.2);  border-color:rgba(96,165,250,0.4); color:#60a5fa; }
.b-pp { background:rgba(168,85,247,0.2);  border-color:rgba(216,180,254,0.4);color:#d8b4fe; }
.b-wt { background:rgba(20,184,166,0.2);  border-color:rgba(45,212,191,0.4); color:#2dd4bf; }
.b-wd { background:rgba(245,158,11,0.18); border-color:rgba(245,158,11,0.4); color:#fbbf24; }
.b-pn { background:rgba(99,102,241,0.18); border-color:rgba(129,140,248,0.45);color:#a5b4fc; }
.b-ts { background:rgba(236,72,153,0.16); border-color:rgba(244,114,182,0.4); color:#f9a8d4; }
.b-ws { background:rgba(56,189,248,0.16); border-color:rgba(56,189,248,0.4);  color:#7dd3fc; }
.b-sf { background:rgba(16,185,129,0.16); border-color:rgba(16,185,129,0.4);  color:#6ee7b7; }
.b-az { background:rgba(124,58,237,0.16); border-color:rgba(139,92,246,0.45); color:#c4b5fd; }
.b-df { background:rgba(75,85,99,0.2);    border-color:#374151; color:#9ca3af; }

/* ── Misc ──────────────────────────────────────────────────────────────── */
.empty { text-align:center; padding:60px 20px; color:#6e7681; }
.empty .ei  { font-size:2.5rem; margin-bottom:10px; }
.empty h3   { color:#e6edf3; margin-bottom:4px; }
.result-count { font-size: 0.8rem; color: #6e7681; margin-bottom: 14px; }
.result-count strong { color: #e6edf3; }
</style>
"""
