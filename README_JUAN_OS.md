# Juan Operating System — Python (local)

A self-contained **Python** build of the Juan OS command dashboard. It runs
locally with FastAPI, reads live analytics from your **Neon Postgres** database,
renders the neon dashboard as a single self-contained HTML page, and can
**export the analytics as a static HTML report you can share** (opens offline,
no server or internet needed).

No Node.js required — this is the Python counterpart to the existing Next.js app.
It reuses the exact same SQL and JSON contract, so both stay in sync.

## What you get

- **Live dashboard** at `http://127.0.0.1:8000` — stat cards, active workflows,
  live signal feed, terminal, and four analytics charts (all rendered server-side
  as inline SVG, so there are no external scripts). Auto-refreshes every 30s.
- **JSON API** — `/api/dashboard/{stats,workflows,signals,analytics}` (same field
  names as the Next.js routes; validated by `backend_test.py`).
- **Static report export** — one command produces a shareable `.html` snapshot.

## Setup

```bash
# 1. (recommended) create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure your Neon connection
cp .env.example .env
#    then edit .env and set NEON_DATABASE_URL to your Neon Postgres string
```

Your `NEON_DATABASE_URL` looks like:

```
postgresql://user:password@ep-xxxx.region.aws.neon.tech/dbname?sslmode=require
```

`.env` is gitignored — your credentials are never committed.

## Usage

```bash
# verify the database connection and see row counts
python -m juan_os check

# run the live dashboard (default). Open http://127.0.0.1:8000
python -m juan_os
python -m juan_os serve --port 8000            # explicit
python -m juan_os serve --host 0.0.0.0 --port 8000   # expose on your LAN

# export a static, shareable analytics report
python -m juan_os export --out juan_analytics.html
```

The exported `juan_analytics.html` is **fully self-contained**: charts are inline
SVG, there are no external scripts or fonts, so you can email it or open it on any
machine offline.

## Sharing your frontend analytics

- **Static snapshot (recommended):** `python -m juan_os export` → send the
  `juan_analytics.html` file. It reflects the data at export time.
- **Live link:** run `python -m juan_os serve --host 0.0.0.0 --port 8000` and
  share your machine's address on the same network (`http://<your-ip>:8000`). For
  the public internet, put a tunnel (e.g. ngrok/Cloudflare Tunnel) in front of it.

## Data source

Tables read (same as the Next.js app): `search_jobs`,
`retirement_signal_searches`, `extracted_leads`, `outreach_queue`. If
`NEON_DATABASE_URL` is not set, the dashboard shows a setup page and the API
returns `503` with a clear message — there is no mock/demo fallback (live Neon by
design).

## Tests

```bash
# rendering tests — no database required
pytest tests/test_render.py

# full API contract test against the running local app
python -m juan_os serve --port 8000 &
BASE_URL=http://127.0.0.1:8000/api python backend_test.py
```

## Project layout

```
juan_os/
  __main__.py        # CLI: serve (default) | export | check
  app.py             # FastAPI routes (HTML dashboard + JSON API + /healthz)
  db.py              # Neon Postgres connection (psycopg 3, pooled, SSL)
  queries.py         # analytics queries — 1:1 port of the Next.js routes
  charts.py          # inline-SVG chart renderers (no JS/CDN)
  render.py          # Jinja2 rendering for dashboard + report
  templates/         # base.html, dashboard.html, report.html
```
