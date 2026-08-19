1. Knowledgebase — juan_cabezas_kb.md

A compliance-first engine covering both product tracks you sent:

Track A — Annuity / Retirement-Income (4 intent layers) and Track B — Long-Term Care (high-intent / research / caregiver tiers).
Per-state query packs for FL / TX / CA, each anchored to real pension systems — FRS + DROP (FL), TRS + ERS of Texas (TX), CalSTRS + CalPERS (CA).
Negative keywords (with the "don't over-exclude" list), Hot/Moderate/Nurture/Rejected classification, the 0–60 public + 0–40 voluntary scoring model, the neutral qualification form, output schema, lead magnets, the agent system prompt, and FINRA/FCC/state-insurance notes.
Hard guardrails throughout: public data only, no wealth-guessing, consent-based qualification, opt-out honored, licensed-advisor review.
2. Daily-task workflow — juan_cabezas_daily.md

A repeatable 13-step daily cycle (run 3×/day) mapped onto the agents, with per-state limits, the ~10-min human checklist (approve Hot leads + take discovery calls), and the "never do unattended" rules.

3. Local autonomous agent — local_agent_recommendation.md

The one-agent, runs-on-your-computer stack: Juan OS Agent OS orchestrator (this repo) as the single agent + Ollama (free, private local LLM via LLM_BACKEND=ollama) + browser-use / Firecrawl for the web search + cron / Task Scheduler for unattended runs. Only two steps stay human by design (Hot-lead approval, discovery call).

Wired & verified
