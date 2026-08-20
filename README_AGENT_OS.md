# Juan OS — VBS Local Agent OS

A **local-first, signal-first retirement prospecting operating system**: a
26-agent workforce (6 divisions + a Retirement Specialist orchestrator) with a
FastAPI backend and a React + TypeScript + Vite + Tailwind frontend. Everything
runs on your machine — no external providers required to see it working.

> Compliance stance baked in: signal-first, evidence-backed, public-data only,
> **no guessed emails or wealth, no manufactured urgency, no scrape-to-send, no
> automatic financial recommendation, human-controlled at critical decisions.**

## Architecture (matches the frontend diagram)

```
UI Layer          Command Center · Workflow Canvas · Agent Builder ·
                  Approvals · Leads & Signals · Run History        (React+TS+Vite)
Component Layer   Layout shell, sidebar/topbar, cards, tables, agent nodes (Tailwind)
State/Logic       Zustand stores, live-run log, theme, permission-aware UI
Services Layer    API client, WebSocket client, theme manager, router
──────────────── Backend & Local Runtime Boundary ────────────────
Integration       FastAPI backend · SQLite (local) / Neon · orchestrator ·
                  run-event stream (seams for Ollama / tools / scheduler)
```

### The 26 agents (command hierarchy)

- **Command** — Retirement Specialist (orchestrator, L5)
- **Signal Intelligence** — Nova, Atlas, Echo, Delta
- **URL & Extraction** — Pathfinder, Forge, Lens, Anchor
- **Data Trust** — Ledger, Merge, Scout, MX Guardian, Verity
- **Qualification & Compliance** — Compass, Sentinel, Counsel
- **Outreach** — Scribe, Critic, Courier, Relay
- **Conversion & Operations** — Pulse, Closer, Keeper, Beacon, Oracle

Each agent has a **role, division, authority level (1–5), tasks, and guardrails**,
encoded in `juan_os/agent_os/catalog.py` (the single source of truth the frontend
renders). Records move through the real **status flows** (signal → lead →
outreach) via the **handoff pipeline**, enforced by authority levels.

## Run it locally

**1. Backend** (Python 3.11+):
```bash
pip install -r requirements.txt        # fastapi, uvicorn already included
python -m juan_os.agent_os             # API + WebSocket on http://127.0.0.1:8787
```
On first run it creates a local SQLite DB (`juan_os/agent_os/agent_os.db`) and
seeds realistic sample campaigns, signals, leads, approvals, and run events.

**2. Frontend** (Node 18+):
```bash
cd frontend
npm install
npm run dev                            # http://localhost:5173  (proxies /api + /ws to :8787)
```

Open http://localhost:5173, then click **“Run cycle”** in the top bar: the
Retirement Specialist advances a record through every handoff, nodes light up on
the Workflow Canvas, and events stream live into Command Center and Run History.

### Production build
```bash
cd frontend && npm run build           # outputs frontend/dist (static, deployable)
```

### Share on Cloudflare's edge (local-first)
Keep the OS on your machine and put a live Cloudflare URL in front of it — no code
changes. Start the API, then open a tunnel in a second terminal:
```bash
make serve             # http://127.0.0.1:8787
make tunnel            # prints a live https://<random>.trycloudflare.com URL
```
For your own domain (persistent URL) and optional Cloudflare Access login, see
[`cloudflared/README.md`](cloudflared/README.md).

## What's real vs. what's a seam

**Real & runnable now:** the full architecture, the 26-agent catalog, the
data model + status flows, the SQLite store, the orchestration state machine, the
REST API, the live WebSocket run stream, and the entire frontend (all six
surfaces, workflow graph, approvals with human decisions, dark mode).

**Documented seams (follow-on work, need API keys):** the *external* logic each
agent would call — Firecrawl/Exa/Apollo enrichment, Clearout email validation,
Ollama inference, real email providers (Resend/AgentMail/SMTP). These plug into
`juan_os/agent_os/orchestrator.py` where each pipeline step emits its run event.

## Settings & appearance

The **Settings** surface offers COSMIC-style **accent presets** (teal, indigo, purple,
pink, orange, green) and **corner-roundness presets** (round / default / square), applied
live via CSS variables and persisted locally (`frontend/src/lib/theme.ts`). Theme (light/
dark) follows your OS and is toggleable.

## Providers (real agent integrations)

Agents call real providers when their key is present in `.env`, and fall back to local
simulation otherwise. Nothing is hard-coded — see `juan_os/agent_os/providers.py` and
`.env.example`.

| Provider | Agent(s) | Env var | Purpose |
| --- | --- | --- | --- |
| Exa | Nova / Echo | `EXA_API_KEY` | Signal & public research |
| Firecrawl | Delta / Forge | `FIRECRAWL_API_KEY` | Verify + scrape public pages |
| Apollo | Scout | `APOLLO_API_KEY` | Professional enrichment |
| Clearout | Verity | `CLEAROUT_API_KEY` | Mailbox validation |
| DNS (dnspython) | MX Guardian | — | DNS receiving gate (no key) |
| Warmy | Deliverability | `WARMY_API_KEY` | Inbox warmup |
| Composio | Tool Gateway | `COMPOSIO_API_KEY` | Connected external actions |

Endpoints: `GET /api/providers` (status), `POST /api/providers/test` (live key check),
`POST /api/research/live` (Nova→Exa then Delta→Firecrawl seeds real signals),
`POST /api/leads/{id}/enrich` (Scout→Apollo, MX Guardian→DNS, Verity→Clearout).

> Security: put keys only in `.env` (gitignored). Never commit keys. MX Guardian (DNS)
> works with no key; the HTTP providers require open outbound network access.

## Model runtime (swappable LLM)

The reasoning agents (Scribe personalization, Pulse reply classification, Compass) call a
**pluggable LLM runtime** — swap providers with one env var, no code change
(`juan_os/agent_os/llm.py`):

```
LLM_BACKEND=ollama      # local-first (default) — http://localhost:11434
LLM_BACKEND=openai      # any OpenAI-compatible API (OpenAI, Groq, Together, OpenRouter,
                        # LM Studio, vLLM) via OPENAI_BASE_URL / OPENAI_MODEL
LLM_BACKEND=anthropic   # Claude via the official anthropic SDK (ANTHROPIC_MODEL, e.g. claude-opus-5)
```

When the selected backend isn't configured/reachable, agents fall back to safe deterministic
heuristics (e.g. keyword-based reply classification) so the system keeps working offline.

Endpoints: `GET /api/llm/status`, `POST /api/agents/scribe/draft` (draft a message from a
signal), `POST /api/agents/pulse/classify` (classify a reply). Anthropic backend needs
`pip install anthropic`.

## Backend API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/catalog` | Agents, divisions, authority levels, pipeline, status flows |
| `GET /api/overview` | KPI counts + recent runs + operating principles |
| `GET /api/campaigns` `…/signals` `…/leads` `…/outreach` | Entity lists (filterable) |
| `GET /api/approvals` · `POST /api/approvals/{id}/decision` | Human-in-the-loop queue |
| `GET /api/runs` | Audit timeline |
| `POST /api/orchestrator/run-cycle` | Trigger one simulated pipeline cycle |
| `WS /ws` | Live run-event stream |
| `GET /healthz` | Liveness + DB path + counts |

## Layout

```
juan_os/agent_os/       catalog.py · models/store.py · orchestrator.py · server.py · __main__.py
frontend/               Vite + React + TS + Tailwind
  src/lib/              api.ts (API client) · ws.ts (WebSocket) · types.ts
  src/store/            useAppStore.ts (Zustand)
  src/components/       LayoutShell.tsx · ui.tsx
  src/pages/            CommandCenter · WorkflowCanvas · AgentBuilder ·
                        Approvals · LeadsSignals · RunHistory
```
