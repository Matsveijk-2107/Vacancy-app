# Agent scan — Ruflo + Agent-Reach

An agent-driven alternative to the Streamlit app's **Refresh data** button. Instead of
running `scraper.py`, you hand [`scan_prompt.md`](scan_prompt.md) to a Claude agent that
does the same job — scan every club, match data/analytics roles, verify, and write a
report — using two tools:

| Tool | Role in the scan | Repo |
|------|------------------|------|
| **Agent-Reach** | The agent's *web reach*. Its channels (web reader, search, GitHub, **LinkedIn**, social) replace hand-rolled HTTP scraping — and reach each club's LinkedIn, which the raw scraper can't. | <https://github.com/Panniantong/Agent-Reach> |
| **Ruflo** | The *swarm harness*. `swarm_init` / `agent_spawn` fan the 176 clubs out across parallel workers instead of one slow serial pass. | <https://github.com/ruvnet/ruflo> |

This does **not** replace the app — the Streamlit dashboard, `clubs.py`, `keywords.py`
and `scraper.py` are untouched. It's a second way to run the same scan from inside a
Claude agent (Claude Code or claude.ai), and it reuses the app's curated club list so
the two never drift.

---

## One-time setup

### 1. Ruflo (swarm orchestration, via MCP)

```bash
# Register Ruflo's MCP server with Claude Code — exposes swarm_init / agent_spawn etc.
claude mcp add ruflo -- npx ruflo@latest mcp start
```

(Or install the plugins: `/plugin install ruflo-core@ruflo` and
`/plugin install ruflo-swarm@ruflo`.)

### 2. Agent-Reach (web reach skill)

Install per the project's own instructions — point your agent at its install doc:

```text
Install Agent Reach for me: https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md
```

Then verify and configure the channels the scan uses:

```bash
agent-reach doctor                 # which channels work, which need setup
agent-reach configure linkedin     # recommended: the scan checks each club's LinkedIn
agent-reach configure twitter-cookies   # optional: only if you also want X search
```

**LinkedIn coverage.** The scan checks two sources for every club — the club's own
careers site/ATS **and** its LinkedIn (jobs page + role-announcing posts). Reliable
LinkedIn reading needs the LinkedIn channel configured above, because LinkedIn blocks
anonymous automation. Without it, LinkedIn coverage degrades to best-effort web search
for `linkedin.com/jobs/view/` pages — the own-site/ATS layers still work fully. The
zero-config channels (general web via Jina reader, search, GitHub, RSS, YouTube) need
no login.

---

## Run it

**In Claude Code:** use the bundled slash command (see `.claude/commands/scan-jobs.md`):

```text
/scan-jobs
```

**Anywhere else (claude.ai with web search on, etc.):** paste the body of
[`scan_prompt.md`](scan_prompt.md) — from *"You are my job-hunting research agent"*
down — into the chat.

The agent writes its report to `scan-YYYY-MM-DD.md` in this folder. On the next run it
diffs against the previous `scan-*.md` and leads with what's new — that diff replaces
the app's "new since last scan" badge.

---

## Keep the club list in sync

Section 1 of `scan_prompt.md` (the `<CLUBS>` … `</CLUBS>` block) is generated from the
app's `clubs.py`, so both the app and the agent scan the same 176 clubs. After editing
`clubs.py`, regenerate it:

```bash
python football_jobs/agent_scan/build_prompt.py          # rewrite the block in place
python football_jobs/agent_scan/build_prompt.py --print   # or just preview it
```

Don't hand-edit the club list — your edits would be overwritten on the next run.

---

## Recurring runs

- **`/loop 6h`** — repeat the scan every 6 hours in the current session.
- **A scheduled cloud agent** — e.g. Monday 08:00, report written to a file or pushed
  to you.

Both replace the app's **Refresh data** button; the `scan-YYYY-MM-DD.md` diff replaces
its "new since last scan" badge, and a starred list in your notes replaces the
Saved / Done tabs.
