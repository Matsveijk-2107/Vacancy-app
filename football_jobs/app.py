"""Football Analytics Job Tracker — dashboard redesign."""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone

from clubs import CLUBS
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

# ── Hide sidebar entirely ────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117;
    color: #e6edf3;
}
[data-testid="stMain"] { padding-top: 0 !important; }
.block-container { padding: 2rem 2.5rem 2rem !important; max-width: 100% !important; }

/* Top bar */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 0 22px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 24px;
}
.topbar-left h1 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    color: #e6edf3;
    letter-spacing: -0.4px;
}
.topbar-left p { margin: 2px 0 0; font-size: 0.82rem; color: #8b949e; }
.accent { color: #58a6ff; }
.topbar-right { display: flex; align-items: center; gap: 16px; font-size: 0.8rem; color: #8b949e; }

/* KPI row */
.kpi-row { display: flex; gap: 14px; margin-bottom: 28px; }
.kpi-card {
    flex: 1; background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 18px 20px; text-align: center;
}
.kpi-card .val { font-size: 2.2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.kpi-card .lbl { font-size: 0.72rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.07em; }
.kpi-blue  .val { color: #58a6ff; }
.kpi-green .val { color: #3fb950; }
.kpi-amber .val { color: #d29922; }
.kpi-grey  .val { color: #8b949e; }

/* League cards */
.league-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
    height: 100%;
}
.league-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}
.league-card-header .flag { font-size: 1.3rem; }
.league-card-header .league-name {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.progress-wrap {
    background: #21262d;
    border-radius: 4px;
    height: 5px;
    margin-bottom: 6px;
    overflow: hidden;
}
.progress-fill { height: 100%; border-radius: 4px; }
.progress-label { font-size: 0.7rem; color: #8b949e; margin-bottom: 10px; }
.club-pills { display: flex; flex-wrap: wrap; gap: 5px; }
.cp {
    font-size: 0.68rem; font-weight: 600;
    padding: 3px 8px; border-radius: 20px; border: 1px solid;
    white-space: nowrap;
}
.cp-green { background: rgba(63,185,80,0.12); border-color: #3fb950; color: #3fb950; }
.cp-grey  { background: rgba(139,148,158,0.06); border-color: #30363d; color: #6e7681; }

/* Vacancy cards */
.v-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.v-card .v-title { font-size: 0.98rem; font-weight: 700; color: #e6edf3; margin-bottom: 5px; }
.v-card .v-meta {
    display: flex; flex-wrap: wrap; gap: 14px;
    font-size: 0.78rem; color: #8b949e; margin-bottom: 5px;
}
.v-card .v-kw { font-size: 0.7rem; color: #58a6ff; margin-bottom: 5px; }
.v-card .v-snippet { font-size: 0.76rem; color: #8b949e; margin-bottom: 6px; }
.v-card .v-link { font-size: 0.78rem; color: #58a6ff; text-decoration: none; }

/* Badges */
.badge {
    display: inline-block; padding: 2px 7px;
    border-radius: 20px; font-size: 0.68rem; font-weight: 600;
}
.b-li { background:#0a66c2; color:#fff; }
.b-cp { background:#238636; color:#fff; }
.b-tt { background:#0e7490; color:#fff; }
.b-wb { background:#e74c3c; color:#fff; }
.b-gh { background:#3fb950; color:#000; }
.b-lv { background:#6e40c9; color:#fff; }
.b-lf { background:#b45309; color:#fff; }

/* Filter bar */
.filter-bar {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 16px 20px; margin-bottom: 20px;
}

/* Empty state */
.empty-state { text-align:center; padding: 60px 20px; color: #8b949e; }
.empty-state .ei { font-size: 2.8rem; margin-bottom: 12px; }
.empty-state h3 { color: #e6edf3; font-size: 1.1rem; margin-bottom: 6px; }

/* Section label */
.section-label {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #8b949e; margin-bottom: 14px;
}

/* Tab styling */
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 0.9rem; font-weight: 600; padding: 10px 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
CACHE_TTL = 21_600

LEAGUE_META: dict[str, dict] = {
    "Netherlands":            {"flag": "🇳🇱", "color": "#FF6B35"},
    "Belgium":                {"flag": "🇧🇪", "color": "#F4C430"},
    "Germany":                {"flag": "🇩🇪", "color": "#E63946"},
    "France":                 {"flag": "🇫🇷", "color": "#4361EE"},
    "Spain - La Liga":        {"flag": "🇪🇸", "color": "#F72585"},
    "Spain - La Liga 2":      {"flag": "🇪🇸", "color": "#C77DFF"},
    "England - Premier League": {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#7209B7"},
    "England - Championship": {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#9B5DE5"},
    "Italy - Serie A":        {"flag": "🇮🇹", "color": "#3A86FF"},
    "Italy - Serie B":        {"flag": "🇮🇹", "color": "#4CC9F0"},
    "Scotland":               {"flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "color": "#06D6A0"},
    "Portugal":               {"flag": "🇵🇹", "color": "#118AB2"},
    "Denmark":                {"flag": "🇩🇰", "color": "#EF476F"},
}

SOURCE_BADGE = {
    "LinkedIn":         "b-li",
    "Careers Page":     "b-cp",
    "Teamtailor":       "b-tt",
    "Workable":         "b-wb",
    "Greenhouse":       "b-gh",
    "Lever":            "b-lv",
    "LiveFootballJobs": "b-lf",
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
    css = SOURCE_BADGE.get(source, "b-ws")
    return f'<span class="badge {css}">{source}</span>'


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


def _league_card_html(league: str, clubs: list[dict], clubs_with_jobs: set[str]) -> str:
    meta  = LEAGUE_META.get(league, {"flag": "🌍", "color": "#58a6ff"})
    color = meta["color"]
    flag  = meta["flag"]

    found = sum(1 for c in clubs if c["name"] in clubs_with_jobs)
    total = len(clubs)
    pct   = int(found / total * 100) if total else 0

    pills = "".join(
        f'<span class="cp {"cp-green" if c["name"] in clubs_with_jobs else "cp-grey"}">{c["name"]}</span>'
        for c in clubs
    )

    short_name = league.replace("England - ", "").replace("Spain - ", "").replace("Italy - ", "")

    return f"""
    <div class="league-card" style="border-top: 3px solid {color};">
      <div class="league-card-header">
        <span class="flag">{flag}</span>
        <span class="league-name" style="color:{color};">{short_name}</span>
      </div>
      <div class="progress-wrap">
        <div class="progress-fill" style="width:{pct}%; background:{color};"></div>
      </div>
      <div class="progress-label">{found} / {total} clubs with openings</div>
      <div class="club-pills">{pills}</div>
    </div>
    """


# ── Header ───────────────────────────────────────────────────────────────────
last     = get_last_scraped()
last_str = last[:16] if last else "never"
stale    = _stale(last)
stale_badge = "⚠️ stale" if stale else "✓ fresh"

hcol1, hcol2 = st.columns([3, 1])
with hcol1:
    st.markdown(f"""
    <div style="padding: 18px 0 10px;">
      <h1 style="font-size:1.6rem; font-weight:800; margin:0; color:#e6edf3; letter-spacing:-0.4px;">
        ⚽ Football Analytics <span style="color:#58a6ff;">Job Tracker</span>
      </h1>
      <p style="margin:4px 0 0; font-size:0.82rem; color:#8b949e;">
        Open data science, analytics &amp; performance analysis roles across European clubs
        &nbsp;·&nbsp; Last scraped: <code style="color:#8b949e;">{last_str} UTC</code>
        &nbsp;<span style="color:{'#d29922' if stale else '#3fb950'}; font-size:0.75rem;">{stale_badge}</span>
      </p>
    </div>
    """, unsafe_allow_html=True)

with hcol2:
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    refresh_clicked = st.button("🔄 Refresh data", type="primary", use_container_width=True)

# Progress placeholder (shown during scrape)
scrape_placeholder = st.empty()
if refresh_clicked:
    _run_scrape(scrape_placeholder)

st.markdown("<div style='border-bottom:1px solid #21262d; margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
raw_vacancies    = _load_vacancies()
clubs_with_jobs  = {v["club_name"] for v in raw_vacancies}
total_clubs      = sum(len(c) for c in CLUBS.values())

# ── KPI row ──────────────────────────────────────────────────────────────────
leagues_active = len({v["league"] for v in raw_vacancies})
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card kpi-blue">
    <div class="val">{len(raw_vacancies)}</div>
    <div class="lbl">Open vacancies</div>
  </div>
  <div class="kpi-card kpi-green">
    <div class="val">{len(clubs_with_jobs)}</div>
    <div class="lbl">Clubs hiring</div>
  </div>
  <div class="kpi-card kpi-amber">
    <div class="val">{total_clubs - len(clubs_with_jobs)}</div>
    <div class="lbl">Clubs — no openings</div>
  </div>
  <div class="kpi-card kpi-grey">
    <div class="val">{leagues_active}</div>
    <div class="lbl">Leagues covered</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_vacancies = st.tabs(["🗺️  League Overview", "💼  Vacancies"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – Geographic league overview
# ════════════════════════════════════════════════════════════════════════════
with tab_overview:
    if not raw_vacancies:
        st.markdown("""
        <div class="empty-state">
          <div class="ei">🔍</div>
          <h3>No data yet</h3>
          <p>Click <strong>Refresh data</strong> above to start scraping all clubs.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-label">Clubs coloured green have at least one open analytics role</div>',
                    unsafe_allow_html=True)

        # ── Row 1: Scotland | England PL | England Championship | Denmark ──
        r1 = st.columns(4)
        for col, league in zip(r1, ["Scotland", "England - Premier League",
                                     "England - Championship", "Denmark"]):
            with col:
                st.markdown(_league_card_html(league, CLUBS[league], clubs_with_jobs),
                            unsafe_allow_html=True)

        # ── Row 2: Netherlands | Germany | (empty x2) ──────────────────────
        r2 = st.columns([1, 2, 1])
        with r2[0]:
            st.markdown(_league_card_html("Netherlands", CLUBS["Netherlands"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r2[1]:
            st.markdown(_league_card_html("Germany", CLUBS["Germany"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r2[2]:
            st.markdown(_league_card_html("Belgium", CLUBS["Belgium"], clubs_with_jobs),
                        unsafe_allow_html=True)

        # ── Row 3: France | Portugal | (empty x2) ──────────────────────────
        r3 = st.columns([2, 1, 1])
        with r3[0]:
            st.markdown(_league_card_html("France", CLUBS["France"], clubs_with_jobs),
                        unsafe_allow_html=True)
        with r3[1]:
            st.markdown(_league_card_html("Portugal", CLUBS["Portugal"], clubs_with_jobs),
                        unsafe_allow_html=True)

        # ── Row 4: Spain La Liga | Spain La Liga 2 | Italy SA | Italy SB ───
        r4 = st.columns(4)
        for col, league in zip(r4, ["Spain - La Liga", "Spain - La Liga 2",
                                     "Italy - Serie A", "Italy - Serie B"]):
            with col:
                st.markdown(_league_card_html(league, CLUBS[league], clubs_with_jobs),
                            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – Vacancies
# ════════════════════════════════════════════════════════════════════════════
with tab_vacancies:
    if not raw_vacancies:
        st.markdown("""
        <div class="empty-state">
          <div class="ei">💼</div>
          <h3>No vacancies yet</h3>
          <p>Click <strong>Refresh data</strong> above to start scraping.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Inline filter bar ────────────────────────────────────────────
        with st.container():
            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
            fc1, fc2, fc3, fc4, fc5 = st.columns([1.4, 1.4, 1, 1, 1])

            with fc1:
                sel_leagues = st.multiselect(
                    "League", options=ALL_LEAGUES, default=[],
                    placeholder="All leagues",
                    label_visibility="collapsed",
                )
                st.caption("League")

            with fc2:
                avail_clubs = [c["name"] for lg in (sel_leagues or ALL_LEAGUES)
                               for c in CLUBS.get(lg, [])]
                sel_clubs = st.multiselect(
                    "Club", options=avail_clubs, default=[],
                    placeholder="All clubs",
                    label_visibility="collapsed",
                )
                st.caption("Club")

            with fc3:
                sel_source = st.selectbox(
                    "Source",
                    ["All", "Careers Page", "LinkedIn", "Teamtailor",
                     "Workable", "Greenhouse", "Lever", "LiveFootballJobs"],
                    label_visibility="collapsed",
                )
                st.caption("Source")

            with fc4:
                kw = st.text_input(
                    "Keyword", placeholder="python, SQL…",
                    label_visibility="collapsed",
                )
                st.caption("Keyword filter")

            with fc5:
                recent = st.toggle("< 30 days only", value=False)
                view   = st.radio("View", ["Cards", "Table"], horizontal=True,
                                  label_visibility="collapsed")

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Apply filters ────────────────────────────────────────────────
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
                | df["description_snippet"].str.contains(kw, case=False, na=False)
                | df["keywords_matched"].str.contains(kw, case=False, na=False)
            )
            df = df[mask]
        if recent:
            cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            df = df[df["posted_date"].notna() & (df["posted_date"] >= cutoff)]

        st.markdown(
            f'<div style="font-size:0.8rem;color:#8b949e;margin-bottom:12px;">'
            f'Showing <strong style="color:#e6edf3;">{len(df)}</strong> vacancies</div>',
            unsafe_allow_html=True,
        )

        if df.empty:
            st.markdown("""
            <div class="empty-state">
              <div class="ei">🎯</div>
              <h3>No results</h3>
              <p>Try widening your filters.</p>
            </div>""", unsafe_allow_html=True)

        elif view == "Cards":
            for _, row in df.iterrows():
                color   = LEAGUE_META.get(row["league"], {}).get("color", "#58a6ff")
                badge   = _badge(row["source"])
                date    = f"📅 {row['posted_date']}" if row.get("posted_date") else ""
                kw_str  = row.get("keywords_matched", "")
                snippet = (row.get("description_snippet") or "")[:200]
                url     = row.get("url", "#")
                st.markdown(f"""
                <div class="v-card" style="border-left-color:{color};">
                  <div class="v-title">{row['job_title']}</div>
                  <div class="v-meta">
                    <span style="color:{color};font-weight:700;">⚽ {row['club_name']}</span>
                    <span>{row['league']}</span>
                    {badge}
                    <span>{date}</span>
                  </div>
                  {"<div class='v-kw'>🏷 " + kw_str + "</div>" if kw_str else ""}
                  {"<div class='v-snippet'>" + snippet + "…</div>" if snippet else ""}
                  <a class="v-link" href="{url}" target="_blank">Open posting ↗</a>
                </div>
                """, unsafe_allow_html=True)

        else:
            cols_map = {
                "club_name": "Club", "league": "League", "job_title": "Job Title",
                "source": "Source", "posted_date": "Posted",
                "keywords_matched": "Keywords", "url": "Link",
            }
            disp = df[list(cols_map)].rename(columns=cols_map).copy()

            def _row_bg(row: pd.Series) -> list[str]:
                c = LEAGUE_META.get(row["League"], {}).get("color", "#333")
                h = c.lstrip("#")
                r2, g2, b2 = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                return [f"background-color:rgba({r2},{g2},{b2},0.09)"] * len(row)

            st.dataframe(
                disp.style.apply(_row_bg, axis=1),
                column_config={
                    "Link": st.column_config.LinkColumn("Link", display_text="Open ↗"),
                    "Job Title": st.column_config.TextColumn("Job Title", width="large"),
                    "Keywords": st.column_config.TextColumn("Keywords", width="medium"),
                },
                use_container_width=True,
                hide_index=True,
                height=min(60 + 38 * len(disp), 680),
            )
