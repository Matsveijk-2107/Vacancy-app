---
description: Scan European football clubs for open data / analytics / performance-analysis roles (Ruflo swarm + Agent-Reach).
---

Run the football analytics job scan.

Use the **Agent-Reach** skill for every web lookup, and spawn **Ruflo** swarm agents
(`swarm_init` / `agent_spawn`) so batches of clubs are scanned in parallel. Follow the
instructions in the prompt below exactly — the club list, the L1→L4 search strategy,
the match rules, the verify-before-reporting step, and the output format are all
defined there. Save the report to `football_jobs/agent_scan/scan-YYYY-MM-DD.md` and, if
a previous scan file exists, lead with what's new since it.

If Ruflo's MCP tools or the Agent-Reach skill aren't available, say so and stop rather
than guessing — see `football_jobs/agent_scan/README.md` for the one-time setup.

@football_jobs/agent_scan/scan_prompt.md
