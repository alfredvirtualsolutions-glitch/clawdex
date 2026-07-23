"""FastAPI application for Juan OS.

Serves the neon dashboard as self-contained HTML plus JSON analytics endpoints
that match the original Next.js contract (see ``backend_test.py``).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from . import db, queries, render

app = FastAPI(title="Juan Operating System", version="1.0.0")


def _error(exc: Exception, status: int = 500) -> JSONResponse:
    detail = str(exc)
    if isinstance(exc, db.ConfigError):
        status = 503
    return JSONResponse({"error": "Failed to fetch data", "details": detail}, status_code=status)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    try:
        data = queries.get_all()
    except db.ConfigError as exc:
        return HTMLResponse(_config_page(str(exc)), status_code=503)
    return HTMLResponse(render.build_dashboard_html(data))


@app.get("/api/dashboard/stats")
def stats():
    try:
        return queries.get_stats()
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@app.get("/api/dashboard/workflows")
def workflows():
    try:
        return queries.get_workflows()
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@app.get("/api/dashboard/signals")
def signals():
    try:
        return queries.get_signals()
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@app.get("/api/dashboard/analytics")
def analytics():
    try:
        return queries.get_analytics()
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@app.get("/healthz")
def healthz():
    try:
        counts = db.check()
        db_ok = all(not isinstance(v, str) for v in counts.values())
        return {"ok": db_ok, "db": "connected" if db_ok else "error", "tables": counts}
    except db.ConfigError as exc:
        return JSONResponse({"ok": False, "db": "unconfigured", "details": str(exc)}, status_code=503)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "db": "error", "details": str(exc)}, status_code=503)


def _config_page(message: str) -> str:
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Juan OS — setup</title></head>'
        '<body style="background:#0a0a1a;color:#e5e7eb;font-family:system-ui;padding:48px;line-height:1.6">'
        '<h1 style="background:linear-gradient(135deg,#a855f7,#06b6d4);-webkit-background-clip:text;'
        '-webkit-text-fill-color:transparent">Juan OS needs a database connection</h1>'
        f'<p style="color:#f97316">{message}</p>'
        '<pre style="background:rgba(0,0,0,.4);padding:16px;border-radius:10px">'
        'cp .env.example .env\n# then edit .env and set:\nNEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require'
        '</pre></body></html>'
    )
