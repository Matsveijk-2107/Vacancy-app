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
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,600;1,9..144,700&family=Inter:wght@400;500;600;700&family=Roboto+Mono:wght@400;500;600&display=swap');

/* ══════════════════════════════════════════════════════════════════════════
   ALMANAC '26 — "The Scouting Annual" (LIGHT)
   A premium light warm-newsprint data almanac (Financial Times / StatsBomb
   feel). Depth comes from three paper tones + hairline rules + one coloured
   "spine" per card — no drop-shadows (except floating menus). League + source
   hues are demoted to thin ticks. One terracotta accent, spent only on a
   small, countable set of live/actionable things.
   Typography triad: Fraunces (serif headlines) · Inter (body/widgets) ·
   Roboto Mono (every figure + uppercase caption).
   ══════════════════════════════════════════════════════════════════════════ */
:root {
  --bg:#F4EFE6; --paper:#FBF8F2; --paper-raised:#FFFFFF; --paper-wash:#FFFDF8;
  --hairline:#E4DCCD; --hairline-strong:#CFC6B4; --hairline-bright:#B8AD97;
  --ink-hi:#1A1814; --ink-mid:#403A30; --ink-lo:#6B6358;
  --accent:#B5481F; --accent-hi:#CC5A2C; --accent-deep:#8F3818;
  --accent-wash:rgba(181,72,31,0.08);
  --positive:#2F6E4F; --warning:#9A6A1E; --danger:#A8392B; --sage:#5E7468;
  --display:'Fraunces',Georgia,serif;
  --body:'Inter',-apple-system,sans-serif;
  --mono:'Roboto Mono',ui-monospace,monospace;
  --ease:cubic-bezier(0.2,0.6,0.2,1); --dur-fast:120ms; --dur:160ms;
}

/* Hide Streamlit chrome */
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer { display: none !important; }

/* ── Reset & base ──────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--ink-hi);
    font-family: var(--body);
    font-optical-sizing: auto;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stMain"]  { padding-top: 0 !important; }
.block-container { padding: 1.8rem 2.6rem 3rem !important; max-width: 1500px !important; }
[data-testid="stVerticalBlock"] { gap: 0.5rem; }
.num, .vc-meta, .pg-lbl, .result-count, .hdr-sub code, .lg-frac {
    font-variant-numeric: tabular-nums lining-nums; }
::-webkit-scrollbar       { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--hairline-strong); border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: var(--hairline-bright); }

/* ── Header / masthead ─────────────────────────────────────────────────── */
.hdr {
    display: flex; align-items: center; justify-content: space-between;
    padding: 22px 0 16px; margin-bottom: 26px;
    border-bottom: 1px solid var(--hairline-bright);
    box-shadow: 0 3px 0 var(--hairline);      /* FT double-rule */
}
.hdr-title { font-family: var(--display); font-size: 1.7rem; font-weight: 700;
             letter-spacing: -0.02em; color: var(--ink-hi); margin: 0; }
.hdr-title span { color: var(--accent); font-style: italic; }
.hdr-sub  { margin: 6px 0 0; font-family: var(--mono); font-size: 0.72rem;
            letter-spacing: 0.03em; color: var(--ink-lo); }
.hdr-sub code { background: var(--paper-raised); padding: 1px 6px; border-radius: 2px;
                border: 1px solid var(--hairline-strong); font-size: 0.7rem; color: var(--ink-hi); }
.hdr-pill { display: inline-flex; align-items: center; gap: 6px; margin-left: 10px;
            padding: 2px 8px; border-radius: 2px; font-family: var(--mono);
            font-size: 0.64rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
            background: transparent; border: 1px solid; }
.hdr-pill::before { content:''; width:5px; height:5px; border-radius:50%; background: currentColor; }
.hdr-pill-fresh { color: var(--positive); border-color: var(--positive); }
.hdr-pill-stale { color: var(--warning); border-color: var(--warning); }
@media (prefers-reduced-motion: no-preference) {
  .hdr-pill-fresh::before { animation: pulse 2.4s var(--ease) infinite; }
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }

/* ── KPI ledger band ───────────────────────────────────────────────────── */
.kpi-row { display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 0;
           border: 1px solid var(--hairline-strong); border-radius: 2px; overflow: hidden;
           background: var(--paper-raised); box-shadow: inset 0 1px 0 var(--hairline-bright);
           margin-bottom: 30px; }
.kpi { position: relative; background: transparent; border: none;
       border-right: 1px solid var(--hairline); border-radius: 0;
       padding: 18px 22px 16px; transition: background var(--dur-fast) var(--ease); }
.kpi:last-child { border-right: none; }
.kpi:hover { background: var(--paper); }
.kpi::before { content:''; position: absolute; top: 0; left: 22px; width: 24px; height: 2px; }
.kpi-blue::before  { background: var(--accent); }
.kpi-green::before { background: var(--positive); }
.kpi-amber::before { background: var(--warning); }
.kpi-purple::before{ background: var(--sage); }
.kpi .num { font-family: var(--display); font-size: 2.4rem; font-weight: 700;
            letter-spacing: -0.02em; line-height: 0.95; color: var(--ink-hi); margin-bottom: 6px; }
.kpi .num-act { color: var(--accent) !important; }
.kpi .lbl  { font-family: var(--mono); font-size: 0.64rem; font-weight: 600;
             letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-lo); }
@media (prefers-reduced-motion: no-preference) {
  .kpi .num { animation: fadein 240ms var(--ease) both; }
}
@keyframes fadein { from{opacity:0} to{opacity:1} }

/* ── Tabs as editorial section headers ─────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid var(--hairline); }
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; border: none !important; border-radius: 0 !important;
    padding: 8px 16px !important; font-family: var(--mono) !important;
    font-size: 0.74rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important; color: var(--ink-lo) !important; }
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important; color: var(--ink-hi) !important; border: none !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--accent) !important; height: 2px; }
[data-testid="stTabs"] [data-baseweb="tab-border"]    { background-color: var(--hairline) !important; }

/* ── Filter toolbar ────────────────────────────────────────────────────── */
.st-key-filterbar {
    background: var(--paper-raised); border: none; border-radius: 0;
    border-top: 1px solid var(--hairline-bright); border-bottom: 1px solid var(--hairline);
    box-shadow: inset 0 1px 0 var(--hairline-bright);
    padding: 16px 20px !important; margin-bottom: 20px; }
.st-key-filterbar [data-testid="stVerticalBlock"] { gap: 0.4rem; }
.st-key-filterbar label p,
.st-key-filterbar [data-testid="stWidgetLabel"] p {
    font-family: var(--mono) !important; font-size: 0.62rem !important; font-weight: 600 !important;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-lo) !important; }

/* Inputs / closed selects */
[data-baseweb="input"], [data-baseweb="select"] > div,
.stTextInput input, [data-testid="stTextInputRootElement"] {
    background: var(--paper) !important; border: 1px solid var(--hairline-strong) !important;
    border-radius: 2px !important; color: var(--ink-hi) !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within,
[data-testid="stTextInputRootElement"]:focus-within {
    border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
.stTextInput input::placeholder { color: var(--ink-lo) !important; }
[data-baseweb="input"] input { background: transparent !important; color: var(--ink-hi) !important; }
[data-baseweb="select"] svg { color: var(--ink-lo) !important; }

/* Popovers — the ONE place a shadow is allowed (must float above paper) */
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] {
    background: var(--paper-raised) !important; border: 1px solid var(--hairline-bright) !important;
    border-radius: 2px !important; box-shadow: 0 12px 32px rgba(0,0,0,0.55) !important; }
[data-baseweb="menu"] li:hover, [role="option"]:hover {
    background: var(--paper) !important; box-shadow: inset 2px 0 0 var(--accent); }

/* Multiselect tags — hue gone, accent left tick */
[data-baseweb="tag"] {
    background: transparent !important; border: 1px solid var(--hairline-strong) !important;
    border-left: 2px solid var(--accent) !important; color: var(--ink-hi) !important;
    border-radius: 2px !important; }
[data-baseweb="tag"] span { color: var(--ink-hi) !important; }

/* Radio (View) → underline-tab segments */
.st-key-filterbar [role="radiogroup"] {
    display: inline-flex; gap: 0; background: var(--paper);
    border: 1px solid var(--hairline-strong); border-radius: 2px; padding: 2px; }
.st-key-filterbar [role="radiogroup"] label {
    margin: 0 !important; padding: 4px 14px !important; border-radius: 0; cursor: pointer;
    transition: box-shadow var(--dur-fast) var(--ease); }
.st-key-filterbar [role="radiogroup"] label:has(input:checked) {
    background: var(--paper-raised); box-shadow: inset 0 -2px 0 var(--accent); }
.st-key-filterbar [role="radiogroup"] [data-testid="stMarkdownContainer"] p {
    font-family: var(--mono) !important; font-size: 0.72rem !important; color: var(--ink-hi) !important; }
.st-key-filterbar [role="radiogroup"] [data-baseweb="radio"] > div:first-child { display: none !important; }

/* Toggle */
[data-baseweb="checkbox"] [aria-checked="true"] { background: var(--accent) !important; }

/* Primary button — the single loudest accent moment */
[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important; border: 1px solid var(--accent-deep) !important;
    border-radius: 2px !important; color: var(--paper) !important;
    font-family: var(--mono) !important; font-weight: 600 !important;
    letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.74rem !important;
    box-shadow: none !important; transition: filter var(--dur-fast) var(--ease); }
[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.06); }

/* ── League overview — standings blocks ────────────────────────────────── */
.lg-card { background: var(--paper-raised); border: 1px solid var(--hairline); border-top-width: 2px;
           border-radius: 2px; padding: 16px 18px; margin-bottom: 14px; height: 100%;
           box-shadow: inset 0 1px 0 var(--hairline-bright); }
.lg-hdr  { display: flex; align-items: center; gap: 8px; margin-bottom: 11px; }
.lg-flag { font-size: 1.2rem; }
.lg-name { font-family: var(--mono); font-size: 0.72rem; font-weight: 700;
           letter-spacing: 0.1em; text-transform: uppercase; }
.lg-frac { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-hi); }
.pg-wrap  { background: var(--hairline); border-radius: 0; height: 3px; margin-bottom: 6px; overflow: hidden; }
.pg-fill  { height: 100%; border-radius: 0; }
.pg-lbl   { font-family: var(--mono); font-size: 0.64rem; color: var(--ink-lo); margin-bottom: 11px; }
.pills    { display: flex; flex-wrap: wrap; gap: 5px; }
.pill { display: inline-flex; align-items: center; gap: 5px; font-family: var(--mono);
        font-size: 0.62rem; padding: 2px 6px; border-radius: 2px; border: 1px solid; white-space: nowrap; }
.pill-on  { background: transparent; border-color: var(--hairline-bright);
            border-left: 2px solid var(--positive); color: var(--ink-hi); }
.pill-off { background: transparent; border-color: var(--hairline); color: var(--ink-lo); opacity: 0.55; }
.pill-on:hover { border-color: var(--accent); }
.pill img { border-radius: 2px !important; }

/* ── DataFrame ─────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid var(--hairline-strong) !important; border-radius: 2px !important; }

/* ── Vacancy cards — ledger entries ────────────────────────────────────── */
.vc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
           gap: 1px; background: var(--hairline); margin-bottom: 8px; align-items: stretch; }
.vc { background: var(--paper); border: 1px solid var(--hairline); border-left: 2px solid;
      border-radius: 2px; padding: 18px 20px 16px;
      transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease); }
.vc:hover { border-color: var(--hairline-bright); box-shadow: inset 2px 0 0 var(--accent); }
.vc:focus-within { outline: 1px solid var(--accent); outline-offset: -1px; }
.vc img { border-radius: 2px !important; }
.vc > div:first-child img { border: 1px solid var(--hairline); }
.vc-title { font-family: var(--display); font-size: 1.02rem; font-weight: 600; letter-spacing: -0.01em;
            line-height: 1.25; color: var(--ink-hi); margin-bottom: 8px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.vc:hover .vc-title { color: #FFFDF8; }
.vc-meta  { display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
            font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.02em;
            color: var(--ink-lo); margin-bottom: 9px; }
.vc-club  { font-weight: 600; }
.vc-dot   { color: var(--hairline-strong); }
.vc-cat   { background: transparent; border: 1px solid var(--hairline-strong); color: var(--ink-hi);
            border-radius: 2px; font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.06em;
            text-transform: uppercase; padding: 1px 6px; }
.vc-kw    { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }
.vc-chip  { font-family: var(--mono); font-size: 0.6rem; padding: 1px 6px; border-radius: 2px;
            background: transparent; border: 1px solid var(--hairline-strong);
            color: var(--ink-lo); letter-spacing: 0.03em; white-space: nowrap;
            transition: border-color var(--dur-fast) var(--ease); }
.vc:hover .vc-chip { border-color: var(--hairline-bright); }
.vc-link  { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.03em; color: var(--ink-hi);
            text-decoration: underline; text-decoration-color: var(--hairline-bright);
            text-underline-offset: 3px; transition: text-decoration-color var(--dur) var(--ease); }
.vc-link:hover { text-decoration-color: var(--accent); }

.vc-actions { display: flex; flex-direction: column; gap: 6px; align-items: center; justify-content: center; }
.vc-act { display: inline-flex; align-items: center; justify-content: center;
          width: 30px; height: 30px; border-radius: 2px; text-decoration: none;
          border: 1px solid var(--hairline-strong); background: transparent; font-size: 0.85rem;
          transition: border-color var(--dur-fast) var(--ease), background var(--dur-fast) var(--ease); }
.vc-act:hover { border-color: var(--accent); background: var(--paper-raised); }
.vc-act-star.on { border-color: var(--accent); background: var(--accent-wash); }

.vc-new { display:inline-block; padding:0 5px; border-radius:2px; font-family: var(--mono);
          font-size:0.58rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
          background:transparent; color: var(--accent-hi); border:1px solid var(--accent); }

/* Low-confidence "~ maybe" tag — outlined ochre square (matches the system) */
.vc-maybe { display:inline-block; padding:1px 6px; border-radius:2px; font-family: var(--mono);
            font-size:0.58rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase;
            background:transparent; color: var(--warning); border:1px solid var(--warning);
            white-space:nowrap; }

/* ── Source badges — hue collapsed to a 2px left tick ──────────────────── */
.badge { display: inline-block; padding: 1px 7px; border-radius: 2px; font-family: var(--mono);
         font-size: 0.6rem; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase;
         background: transparent !important; color: var(--ink-lo) !important;
         border: 1px solid var(--hairline-strong) !important; }
.b-cp { border-left: 2px solid #3fb950 !important; }
.b-tt { border-left: 2px solid #22d3ee !important; }
.b-wb { border-left: 2px solid #f87171 !important; }
.b-gh { border-left: 2px solid #4ade80 !important; }
.b-lv { border-left: 2px solid #a78bfa !important; }
.b-lf { border-left: 2px solid #fb923c !important; }
.b-li { border-left: 2px solid #60a5fa !important; }
.b-pp { border-left: 2px solid #d8b4fe !important; }
.b-wt { border-left: 2px solid #2dd4bf !important; }
.b-wd { border-left: 2px solid #fbbf24 !important; }
.b-pn { border-left: 2px solid #a5b4fc !important; }
.b-ts { border-left: 2px solid #f9a8d4 !important; }
.b-ws { border-left: 2px solid #7dd3fc !important; }
.b-sf { border-left: 2px solid #6ee7b7 !important; }
.b-az { border-left: 2px solid #c4b5fd !important; }
.b-df { border-left: 2px solid #9ca3af !important; }

/* ── Misc ──────────────────────────────────────────────────────────────── */
.empty { text-align:center; padding:64px 20px; color: var(--ink-lo); }
.empty .ei  { font-size:2.2rem; margin-bottom:12px; opacity:0.7; }
.empty h3   { font-family: var(--display); color: var(--ink-hi); margin-bottom:4px; }
.result-count { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-lo); margin-bottom: 16px; }
.result-count strong { color: var(--accent); font-weight: 600; }
</style>
"""
