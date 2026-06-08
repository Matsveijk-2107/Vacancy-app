# ⚽ Football Analytics Job Tracker

A Streamlit dashboard that scrapes the careers pages and ATS platforms of **176 European
football clubs** and surfaces open **data, analytics and performance-analysis** roles —
the jobs a football data scientist actually wants — in one filterable view.

Built accuracy-first: every listing comes from a club's own domain or a known, trusted
recruitment host, and titles are matched against a multilingual role model
(EN · NL · DE · FR · ES · IT · PT · DK) that deliberately filters out coaching,
medical, sports-science and commercial roles.

---

## Features

- **176 clubs, 13 leagues** — Eredivisie, Jupiler Pro League, Bundesliga, Ligue 1,
  La Liga 1 & 2, Premier League, Championship, Serie A & B, Scottish Premiership,
  Primeira Liga and the Danish Superliga.
- **Layered scraping** that adapts to whatever platform a club uses (see below).
- **Precise role matching** — a data/analytics *topic* only counts when paired with a
  real *role noun*, so nav links ("CLUB DATA"), skill-list JDs ("Python, SQL") and
  non-data roles (physio, scout, coach) are dropped.
- **Dashboard** — KPI cards, league overview, card/table views, full-text + league +
  club + source filters, a "new since last scan" badge, plus save / mark-replied lists.
- **Self-contained data** — SQLite, regenerated on demand from the **Refresh** button.

## How the scraper works

Each club is scraped through up to four layers; the first that yields results wins.

| Layer | Source | Examples |
|-------|--------|----------|
| **L1** | Club careers page (HTML + embedded JSON) | static pages, **Jobtoolz** `jobComponent` JSON |
| **L2** | ATS public APIs | Teamtailor · Workday · Personio · Greenhouse · Lever · Workable · Pinpoint · webitrent · Posting Panda · Talos · SuccessFactors · Recruitee · HRworks · softgarden · CoreHR · HiBob · Hellowork |
| **L3** | Job aggregator (fallback) | **Adzuna** API, then a keyless **DuckDuckGo** search — only for clubs with no scrapable careers page |
| **L4** | Football job boards | LiveFootballJobs (UK / NL / BE) |

LinkedIn is intentionally **not** scraped — it blocks automated access. Adzuna is the
legitimate, structured replacement for the clubs that post nowhere else.

## Quick start

```bash
cd football_jobs
python -m venv .venv && source .venv/bin/activate    # optional
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (default <http://localhost:8501>) and click
**Refresh data** to run the first scrape.

## Configuration

All API keys are **optional** — the app scrapes club careers pages and ATS APIs with no
key at all. The keys only power the L3 search layer that reaches clubs with no careers
page of their own (much of Italy and parts of Spain/France).

```bash
cp .env.example .env       # then edit .env
```

| Variable | Purpose |
|----------|---------|
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Free [Adzuna](https://developer.adzuna.com/) job-aggregator API (recommended). Covers GB/IT/ES/FR/DE/NL/BE. |
| `SERPAPI_KEY` | Legacy/optional. Unused by default. |

## Project structure

```
football_jobs/
├── app.py           # Streamlit dashboard (layout & page logic)
├── theme.py         # palette, league metadata, club logos, CSS
├── scraper.py       # 4-layer scraping engine + ATS handlers
├── clubs.py         # the 176-club master list (careers URLs, ATS flags)
├── keywords.py      # multilingual role/topic matcher
├── database.py      # SQLite persistence (sync, prune, save/replied)
├── utils.py         # HTTP headers, robots.txt, dedup, date parsing
├── test_matching.py # matcher unit tests
├── static/logos/    # club crests (embedded as data URIs at runtime)
└── requirements.txt
```

## Tests

```bash
cd football_jobs
pytest
```

## License

[MIT](LICENSE) © Mats van Eijk
