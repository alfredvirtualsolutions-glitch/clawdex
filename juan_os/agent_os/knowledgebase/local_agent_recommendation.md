# Local AI Agent — recommendation (runs on your computer, minimal support)

You asked for an AI agent that runs **locally** and can execute the daily campaign
**on its own**. You already have most of it — this is the recommended local stack,
all open-source / self-hosted, no cloud dependency required.

## The single "agent" = Juan OS Agent OS (this repo)
From your point of view there is **one** agent: the **Retirement Specialist**
orchestrator. It internally drives the whole pipeline (search → verify → extract →
validate → score → gate → draft → send → convert), so you don't juggle multiple
agents. It runs as a local FastAPI process against a local SQLite database — no
external service required to operate the loop.

```bash
pip install -r requirements.txt
python -m juan_os.agent_os seed-juan        # load Juan's FL/TX/CA campaigns (once)
python -m juan_os.agent_os                  # start the local agent + dashboard API
# UI: cd frontend && npm install && npm run dev  → http://localhost:5173
```

## The brain = Ollama (local LLM, free & private)
Run the reasoning agents (Scribe drafting, Pulse reply classification) on a **local
model** so nothing leaves your machine and there are no per-token costs:

```bash
# install Ollama (ollama.com), then:
ollama pull llama3.1          # or qwen2.5:7b / mistral — 8B models run on ~8GB RAM / Apple Silicon
# in .env:
LLM_BACKEND=ollama
OLLAMA_MODEL=llama3.1
```
If the model isn't running, the agents fall back to safe deterministic heuristics —
so the system never stalls.

## The hands (public-web search) — pick one, all local-friendly
- **browser-use** (open-source): a single local agent that drives a real browser to
  run the public searches itself — best fit for "minimal support from other agents".
  Install locally and point it at the approved query packs in the knowledgebase.
- **Firecrawl / Exa API keys** (you have these): fastest path; the agents call them
  during the Search/Verify steps. Works today once keys are in `.env`.
- **Self-hosted Firecrawl** if you want zero external calls.

## Autonomy (unattended daily runs)
Fire the daily cycle 3×/day with your OS scheduler — no babysitting:

```bash
# macOS/Linux cron — 08:00, 12:30, 17:00 local, per state campaign
0 8,17 * * *  curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}'
30 12  * * *  curl -s -X POST localhost:8787/api/orchestrator/run-cycle -H 'content-type: application/json' -d '{}'
```
On Windows use **Task Scheduler** to run the same `curl`/PowerShell call. Optional:
**n8n** (self-hosted, local) if you prefer a visual scheduler + glue.

## Recommended local stack (summary)
| Role | Local tool | Notes |
| --- | --- | --- |
| Agent / orchestrator | **Juan OS Agent OS** (this repo) | one agent, runs the whole pipeline |
| LLM runtime | **Ollama** (`llama3.1` / `qwen2.5`) | free, private, `LLM_BACKEND=ollama` |
| Web search/scrape | **browser-use** or Firecrawl/Exa keys | browser-use = fully self-driven |
| Data store | **SQLite** (built in) | local file; optional Neon later |
| Scheduler | **cron / Task Scheduler / n8n** | 3 unattended runs/day |
| Email (when live) | Resend / AgentMail / SMTP | only for approved sends |

## Human touch points (by design — compliance)
The agent runs unattended **except** two steps that must stay human:
1. **Approve each Hot lead** before outreach (suitability + state licensing).
2. **Take the discovery call** and complete the voluntary qualification + suitability review.

## Hardware note
Ollama 7–8B models run comfortably on Apple Silicon or a machine with ~8–16GB RAM
(a GPU helps but isn't required). For heavier drafting quality, use `OPENAI_BASE_URL`
to point at a hosted OpenAI-compatible model, or `LLM_BACKEND=anthropic` for Claude —
same code, one env var.
