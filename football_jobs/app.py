"""Football Analytics Job Tracker — Streamlit dashboard.

Layout / page logic only. Palette, league metadata, club logos and the
stylesheet live in theme.py; data access in database.py; scraping in scraper.py.

Card actions (✅ replied, ⭐ save, ↩️ undo) use query-param links so the whole
vacancy list renders as a single HTML block — no per-row Streamlit containers,
so filtering stays flicker-free.
"""

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
del _sys, _os

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone

from clubs import CLUBS_BY_LEAGUE as CLUBS
from database import (
    get_last_scraped, get_saved, get_vacancies, init_db,
    mark_as_replied, toggle_star,
)
from keywords import relevance_score
from scraper import scrape_all_clubs
from theme import CSS, LEAGUE_META, badge, league_color, logo_img

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Jobs",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
st.markdown(CSS, unsafe_allow_html=True)

CACHE_TTL = 900  # 15 min — short so the UI reflects fresh scrapes quickly
ALL_LEAGUES = list(CLUBS.keys())


# ── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL)
def _load_vacancies() -> list[dict]:
    return get_vacancies(replied=False)


@st.cache_data(ttl=CACHE_TTL)
def _load_replied() -> list[dict]:
    return get_vacancies(replied=True)


@st.cache_data(ttl=CACHE_TTL)
def _load_saved() -> list[dict]:
    return get_saved()


def _clear_caches() -> None:
    _load_vacancies.clear()
    _load_replied.clear()
    _load_saved.clear()


# ── Query-param actions (flicker-free card buttons) ──────────────────────────
def _handle_actions() -> None:
    qp = st.query_params
    action, key = None, None
    for k in ("reply", "undo", "star"):
        if k in qp:
            action, key = k, qp[k]
            break
    if action is None:
        return
    try:
        vid = int(key)
    except (TypeError, ValueError):
        st.query_params.clear()
        return
    if action == "reply":
        mark_as_replied(vid, True)
    elif action == "undo":
        mark_as_replied(vid, False)
    elif action == "star":
        toggle_star(vid)
    st.query_params.clear()
    _clear_caches()
    st.rerun()


_handle_actions()


def _humanize(iso: str | None) -> str:
    if not iso:
        return "never"
    try:
        ts = datetime.fromisoformat(iso)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - ts
        secs = delta.total_seconds()
        if secs < 90:
            return "just now"
        if secs < 3600:
            return f"{int(secs // 60)} min ago"
        if secs < 86_400:
            return f"{int(secs // 3600)}h ago"
        return f"{int(secs // 86_400)}d ago"
    except ValueError:
        return iso[:16]


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


def _run_scrape(placeholder) -> None:
    _clear_caches()
    with placeholder.container():
        prog = st.progress(0.0, text="Starting scraper…")

        def cb(f: float, msg: str) -> None:
            prog.progress(min(f, 1.0), text=msg)

        result = scrape_all_clubs(progress_callback=cb)
        st.success(
            f"Done — **{result['total']}** vacancies across "
            f"{result['clubs_scraped']} clubs.",
            icon="✅",
        )
        if result["errors"]:
            with st.expander(f"{len(result['errors'])} clubs had errors"):
                for club, msg in result["errors"].items():
                    st.caption(f"• **{club}**: {msg}")
    _clear_caches()
    st.rerun()


# ── Card rendering (single HTML block) ───────────────────────────────────────
def _card(row: dict, *, mode: str) -> str:
    """One vacancy card. mode ∈ {open, saved, done} picks the action links."""
    color   = league_color(row["league"])
    src     = badge(row["source"])
    vid     = row["id"]
    starred = bool(row.get("starred"))
    is_new  = bool(row.get("is_new"))
    logo    = logo_img(row["club_name"], 38)
    kw      = row.get("keywords_matched", "")
    url     = row.get("url", "#")
    date    = f'<span class="vc-dot">·</span><span>📅 {row["posted_date"]}</span>' if row.get("posted_date") else ""
    new_tag = '<span class="vc-new">new</span> ' if is_new and mode == "open" else ""
    chips   = "".join(f'<span class="vc-chip">{k.strip()}</span>'
                      for k in kw.split(",") if k.strip())[:600]
    kw_tag  = f'<div class="vc-kw">{chips}</div>' if chips else ""
    faded   = " opacity:0.7;" if mode == "done" else ""

    if mode == "done":
        src += '<span style="color:#3fb950;font-weight:600;margin-left:8px;">✅ Replied</span>'
        actions = f'<a class="vc-act" href="?undo={vid}" target="_self" title="Move back to vacancies">↩️</a>'
    else:
        star_cls = "vc-act vc-act-star" + (" on" if starred else "")
        actions = (
            f'<a class="vc-act" href="?reply={vid}" target="_self" title="Mark as replied">✅</a>'
            f'<a class="{star_cls}" href="?star={vid}" target="_self" '
            f'title="{"Unsave" if starred else "Save to shortlist"}">⭐</a>'
        )

    return (
        f'<div class="vc" style="border-left-color:{color};{faded}display:flex;align-items:flex-start;gap:12px;">'
        f'<div style="flex-shrink:0;padding-top:2px;">{logo}</div>'
        f'<div style="flex:1;min-width:0;">'
        f'<div class="vc-title">{new_tag} {row["job_title"]}</div>'
        f'<div class="vc-meta">'
        f'<span class="vc-club" style="color:{color};">{row["club_name"]}</span>'
        f'<span class="vc-dot">·</span><span>{row["league"]}</span>{src}{date}</div>'
        f'{kw_tag}'
        f'<a class="vc-link" href="{url}" target="_blank">Open posting ↗</a>'
        f'</div>'
        f'<div class="vc-actions">{actions}</div>'
        f'</div>'
    )


def _render_cards(rows: list[dict], *, mode: str) -> None:
    cards = "".join(_card(r, mode=mode) for r in rows)
    st.markdown(f'<div class="vc-grid">{cards}</div>', unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
last     = get_last_scraped()
stale    = _stale(last)
pill_cls = "hdr-pill-stale" if stale else "hdr-pill-fresh"
pill_txt = "⚠ stale" if stale else "✓ live"

hcol1, hcol2 = st.columns([4, 1])
with hcol1:
    st.markdown(
        f'<div class="hdr"><div>'
        f'<div class="hdr-title">⚽ Football Analytics <span>Jobs</span></div>'
        f'<div class="hdr-sub">Data science, analytics &amp; performance roles across European clubs'
        f'&nbsp;·&nbsp; Last scan: <code>{_humanize(last)}</code>'
        f'<span class="hdr-pill {pill_cls}">{pill_txt}</span></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
with hcol2:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    refresh_clicked = st.button("🔄 Refresh data", type="primary", use_container_width=True)

scrape_placeholder = st.empty()
if refresh_clicked:
    _run_scrape(scrape_placeholder)

# ── Load data ─────────────────────────────────────────────────────────────────
raw_vacancies     = _load_vacancies()
replied_vacancies = _load_replied()
saved_vacancies   = _load_saved()
clubs_with_jobs   = {v["club_name"] for v in raw_vacancies}
total_clubs       = sum(len(c) for c in CLUBS.values())
leagues_active    = len({v["league"] for v in raw_vacancies})
new_count         = sum(1 for v in raw_vacancies if v.get("is_new"))

# ── KPI row ───────────────────────────────────────────────────────────────────
new_kpi = (
    f'<div class="kpi kpi-green"><div class="num">{new_count}</div>'
    f'<div class="lbl">New since last scan</div></div>'
    if new_count else
    f'<div class="kpi kpi-green"><div class="num">{len(clubs_with_jobs)}</div>'
    f'<div class="lbl">Clubs hiring</div></div>'
)
st.markdown(
    f'<div class="kpi-row">'
    f'<div class="kpi kpi-blue"><div class="num">{len(raw_vacancies)}</div>'
    f'<div class="lbl">Open vacancies</div></div>'
    f'{new_kpi}'
    f'<div class="kpi kpi-amber"><div class="num">{len(saved_vacancies)}</div>'
    f'<div class="lbl">Saved shortlist</div></div>'
    f'<div class="kpi kpi-purple"><div class="num">{leagues_active}</div>'
    f'<div class="lbl">Leagues with roles</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
saved_label = f"⭐  Saved ({len(saved_vacancies)})" if saved_vacancies else "⭐  Saved"
done_label  = f"✅  Done ({len(replied_vacancies)})" if replied_vacancies else "✅  Done"
tab_vac, tab_saved, tab_overview, tab_done = st.tabs(
    ["💼  Vacancies", saved_label, "🗺️  League Overview", done_label]
)


def _sort_df(df: pd.DataFrame, how: str) -> pd.DataFrame:
    if how == "Most relevant":
        df = df.assign(_rel=[relevance_score(t, d) for t, d in
                             zip(df["job_title"], df.get("description_snippet", ""))])
        return df.sort_values(["_rel", "scraped_at"], ascending=[False, False])
    if how == "Newest":
        return df.sort_values(["posted_date", "first_seen"], ascending=[False, False],
                              na_position="last")
    if how == "Club":
        return df.sort_values("club_name")
    return df


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – Vacancies
# ════════════════════════════════════════════════════════════════════════════
with tab_vac:
    if not raw_vacancies:
        st.markdown(
            '<div class="empty"><div class="ei">💼</div><h3>No vacancies yet</h3>'
            '<p>Click <strong>Refresh data</strong> to start scraping.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        # Real container (keyed → .st-key-filterbar) so the panel styling in
        # theme.py actually wraps the widgets. The old open/close <div> markdown
        # trick rendered an empty box with the filters floating outside it.
        with st.container(key="filterbar"):
            fc1, fc2, fc3, fc4 = st.columns([1.6, 1.6, 1.3, 1.5])
            with fc1:
                sel_leagues = st.multiselect("League", options=ALL_LEAGUES, default=[],
                                             placeholder="All leagues")
            with fc2:
                avail_clubs = sorted({c["name"] for lg in (sel_leagues or ALL_LEAGUES)
                                      for c in CLUBS.get(lg, [])})
                sel_clubs = st.multiselect("Club", options=avail_clubs, default=[],
                                           placeholder="All clubs")
            with fc3:
                all_sources = sorted({v["source"] for v in raw_vacancies})
                sel_source = st.selectbox("Source", ["All"] + all_sources)
            with fc4:
                kw = st.text_input("Search", placeholder="title, keyword or club…")

            fc5, fc6, fc7, fc8 = st.columns([1.4, 1.2, 1, 1])
            with fc5:
                sort_by = st.selectbox("Sort by", ["Most relevant", "Newest", "Club"])
            with fc6:
                view = st.radio("View", ["Cards", "Table"], horizontal=True)
            with fc7:
                new_only = st.toggle("New only", value=False)
            with fc8:
                recent = st.toggle("Last 30 days", value=False)

        # ── Filter ────────────────────────────────────────────────────────
        df = pd.DataFrame(raw_vacancies)
        if sel_leagues:
            df = df[df["league"].isin(sel_leagues)]
        if sel_clubs:
            df = df[df["club_name"].isin(sel_clubs)]
        if sel_source != "All":
            df = df[df["source"] == sel_source]
        if new_only:
            df = df[df["is_new"] == 1]
        if kw.strip():
            mask = (
                df["job_title"].str.contains(kw, case=False, na=False)
                | df["keywords_matched"].str.contains(kw, case=False, na=False)
                | df["club_name"].str.contains(kw, case=False, na=False)
            )
            df = df[mask]
        if recent:
            cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            df = df[df["posted_date"].notna() & (df["posted_date"] >= cutoff)]

        df = _sort_df(df, sort_by)

        st.markdown(
            f'<div class="result-count">Showing <strong>{len(df)}</strong> '
            f'of {len(raw_vacancies)} vacancies'
            + (f' · <strong>{new_count}</strong> new' if new_count else '')
            + '</div>',
            unsafe_allow_html=True,
        )

        if df.empty:
            st.markdown(
                '<div class="empty"><div class="ei">🎯</div><h3>No results</h3>'
                '<p>Try widening your filters.</p></div>',
                unsafe_allow_html=True,
            )
        elif view == "Table":
            cols_map = {
                "job_title": "Job Title", "club_name": "Club", "league": "League",
                "source": "Source", "posted_date": "Posted",
                "keywords_matched": "Keywords", "url": "Link",
            }
            disp = df[list(cols_map)].rename(columns=cols_map).copy()

            def _row_bg(r: pd.Series) -> list[str]:
                h = league_color(r["League"]).lstrip("#")
                rr, gg, bb = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                return [f"background-color:rgba({rr},{gg},{bb},0.07)"] * len(r)

            st.dataframe(
                disp.style.apply(_row_bg, axis=1),
                column_config={
                    "Link": st.column_config.LinkColumn("Link", display_text="Open ↗"),
                    "Job Title": st.column_config.TextColumn("Job Title", width="large"),
                    "Keywords":  st.column_config.TextColumn("Keywords",  width="medium"),
                    "Club":      st.column_config.TextColumn("Club",       width="medium"),
                },
                use_container_width=True, hide_index=True,
                height=min(60 + 38 * len(disp), 700),
            )
        else:
            _render_cards(df.to_dict("records"), mode="open")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – Saved shortlist
# ════════════════════════════════════════════════════════════════════════════
with tab_saved:
    if not saved_vacancies:
        st.markdown(
            '<div class="empty"><div class="ei">⭐</div><h3>No saved roles</h3>'
            '<p>Click ⭐ on a vacancy to add it to your shortlist.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"{len(saved_vacancies)} roles on your shortlist")
        _render_cards(saved_vacancies, mode="saved")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – League Overview
# ════════════════════════════════════════════════════════════════════════════
def _league_card(league: str, clubs: list[dict]) -> str:
    meta  = LEAGUE_META.get(league, {"flag": "🌍", "color": "#58a6ff"})
    color, flag = meta["color"], meta["flag"]
    found = sum(1 for c in clubs if c["name"] in clubs_with_jobs)
    total = len(clubs)
    pct   = int(found / total * 100) if total else 0
    short = league.replace("England - ", "").replace("Spain - ", "").replace("Italy - ", "")
    pills = "".join(
        f'<span class="pill {"pill-on" if c["name"] in clubs_with_jobs else "pill-off"}">'
        f'{logo_img(c["name"], 14)}{c["name"]}</span>' for c in clubs
    )
    return (
        f'<div class="lg-card" style="border-top:3px solid {color};">'
        f'<div class="lg-hdr"><span class="lg-flag">{flag}</span>'
        f'<span class="lg-name" style="color:{color};">{short}</span>'
        f'<span style="margin-left:auto;font-size:0.72rem;color:#6e7681;">{found}/{total}</span></div>'
        f'<div class="pg-wrap"><div class="pg-fill" style="width:{pct}%;background:{color};"></div></div>'
        f'<div class="pg-lbl">{pct}% of clubs have open roles</div>'
        f'<div class="pills">{pills}</div></div>'
    )


with tab_overview:
    if not raw_vacancies:
        st.markdown(
            '<div class="empty"><div class="ei">🔍</div><h3>No data yet</h3>'
            '<p>Click <strong>Refresh data</strong> above to start scraping.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("Green pills = club has at least one open analytics role")
        r1 = st.columns(4)
        for col, lg in zip(r1, ["Scotland", "England - Premier League",
                                 "England - Championship", "Denmark"]):
            with col:
                st.markdown(_league_card(lg, CLUBS[lg]), unsafe_allow_html=True)
        r2 = st.columns([1, 2, 1])
        with r2[0]:
            st.markdown(_league_card("Netherlands", CLUBS["Netherlands"]), unsafe_allow_html=True)
        with r2[1]:
            st.markdown(_league_card("Germany", CLUBS["Germany"]), unsafe_allow_html=True)
        with r2[2]:
            st.markdown(_league_card("Belgium", CLUBS["Belgium"]), unsafe_allow_html=True)
        r3 = st.columns([2, 1])
        with r3[0]:
            st.markdown(_league_card("France", CLUBS["France"]), unsafe_allow_html=True)
        with r3[1]:
            st.markdown(_league_card("Portugal", CLUBS["Portugal"]), unsafe_allow_html=True)
        r4 = st.columns(4)
        for col, lg in zip(r4, ["Spain - La Liga", "Spain - La Liga 2",
                                 "Italy - Serie A", "Italy - Serie B"]):
            with col:
                st.markdown(_league_card(lg, CLUBS[lg]), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 – Done (replied)
# ════════════════════════════════════════════════════════════════════════════
with tab_done:
    if not replied_vacancies:
        st.markdown(
            '<div class="empty"><div class="ei">📭</div><h3>Nothing here yet</h3>'
            '<p>Click ✅ on a vacancy to mark it as replied.</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="font-size:0.8rem;color:#8b949e;margin-bottom:16px;">'
            f'<strong style="color:#3fb950;">{len(replied_vacancies)}</strong> '
            f'vacancies marked as replied</div>',
            unsafe_allow_html=True,
        )
        _render_cards(replied_vacancies, mode="done")
