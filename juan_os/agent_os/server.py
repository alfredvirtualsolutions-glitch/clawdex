"""Agent OS backend — FastAPI REST API + WebSocket live activity stream.

Local-first: runs entirely against the SQLite store, no external providers
required. Endpoints back every frontend surface; the WebSocket streams run
events so the UI has real-time run visibility.

    python -m juan_os.agent_os          # serve on 127.0.0.1:8787
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import catalog, llm, providers, store
from .orchestrator import Orchestrator

app = FastAPI(title="Juan OS — VBS Local Agent OS", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

store.init_db()


class Hub:
    """Fan-out of run events to all connected WebSocket clients."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    async def broadcast(self, event: dict[str, Any]) -> None:
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


hub = Hub()
orchestrator = Orchestrator(on_event=lambda e: asyncio.create_task(hub.broadcast(e)))


# --------------------------------------------------------------------------- #
# Architecture / catalog
# --------------------------------------------------------------------------- #
@app.get("/api/catalog")
def get_catalog():
    return catalog.catalog_dict()


@app.get("/api/agents")
def get_agents():
    return {"agents": [a.to_dict() for a in catalog.AGENTS]}


@app.get("/api/agents/{key}")
def get_agent(key: str):
    a = catalog.AGENTS_BY_KEY.get(key)
    return a.to_dict() if a else ({"error": "not found"}, 404)


# --------------------------------------------------------------------------- #
# Entities
# --------------------------------------------------------------------------- #
@app.get("/api/overview")
def overview():
    return {"counts": store.counts(), "recent_runs": store.rows("runs", limit=12),
            "operating_principles": catalog.OPERATING_PRINCIPLES}


@app.get("/api/campaigns")
def campaigns():
    return {"campaigns": store.rows("campaigns")}


@app.get("/api/signals")
def signals(campaign_id: str | None = None):
    where, params = ("campaign_id=?", (campaign_id,)) if campaign_id else ("", ())
    return {"signals": store.rows("signals", where, params)}


@app.get("/api/leads")
def leads(campaign_id: str | None = None, classification: str | None = None):
    clauses, params = [], []
    if campaign_id:
        clauses.append("campaign_id=?"); params.append(campaign_id)
    if classification:
        clauses.append("classification=?"); params.append(classification)
    return {"leads": store.rows("leads", " AND ".join(clauses), tuple(params))}


@app.get("/api/outreach")
def outreach():
    return {"outreach": store.rows("outreach")}


@app.get("/api/approvals")
def approvals(status: str = "pending"):
    return {"approvals": store.rows("approvals", "status=?", (status,))}


@app.post("/api/approvals/{approval_id}/decision")
async def decide(approval_id: str, payload: dict):
    decision = payload.get("decision", "approved")
    appr = store.update_status("approvals", approval_id, decision)
    if appr:
        run = store.add_run(appr["campaign_id"], "retirement_specialist",
                            f"approval_{decision}", "approval", approval_id,
                            f"Human {decision} — {appr['title']}")
        await hub.broadcast({"type": "run", **run})
        if decision == "approved" and appr["record_type"] == "lead":
            store.update_status("leads", appr["record_id"], "outreach_ready")
    return {"approval": appr}


@app.get("/api/runs")
def runs(campaign_id: str | None = None, limit: int = 100):
    where, params = ("campaign_id=?", (campaign_id,)) if campaign_id else ("", ())
    return {"runs": store.rows("runs", where, params, limit=limit)}


# --------------------------------------------------------------------------- #
# Orchestrator control (simulated local run — no external calls)
# --------------------------------------------------------------------------- #
@app.post("/api/orchestrator/run-cycle")
async def run_cycle(payload: dict | None = None):
    campaign_id = (payload or {}).get("campaign_id")
    if not campaign_id:
        camps = store.rows("campaigns", "status=?", ("active",), limit=1)
        campaign_id = camps[0]["id"] if camps else None
    if not campaign_id:
        return {"error": "no active campaign"}
    asyncio.create_task(orchestrator.run_cycle(campaign_id))
    return {"status": "started", "campaign_id": campaign_id}


# --------------------------------------------------------------------------- #
# Providers — real external integrations (Exa, Firecrawl, Apollo, Clearout, …)
# --------------------------------------------------------------------------- #
@app.get("/api/providers")
def providers_status():
    return {"providers": providers.status()}


@app.post("/api/providers/test")
def providers_test(payload: dict):
    """Best-effort live call to verify a provider key. Requires open egress."""
    name = (payload or {}).get("name", "")
    try:
        if name == "exa":
            return {"ok": True, "result": providers.exa_search("retirement planning news", 3)}
        if name == "firecrawl":
            return {"ok": True, "result": providers.firecrawl_scrape("https://example.com")}
        if name == "apollo":
            return {"ok": True, "result": providers.apollo_enrich(domain="apollo.io")}
        if name == "clearout":
            return {"ok": True, "result": providers.clearout_verify("support@clearout.io")}
        if name == "dns":
            return {"ok": True, "result": providers.mx_lookup(payload.get("domain", "gmail.com"))}
        if name == "warmy":
            return {"ok": True, "result": providers.warmy_status()}
        if name == "composio":
            return {"ok": True, "result": providers.composio_apps()}
        return JSONResponse({"ok": False, "error": f"unknown provider '{name}'"}, status_code=400)
    except providers.ProviderUnavailable as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, status_code=502)


@app.post("/api/research/live")
async def research_live(payload: dict):
    """Nova(Exa) → Delta(Firecrawl): real search that seeds verified signals."""
    query = (payload or {}).get("query", "").strip()
    campaign_id = (payload or {}).get("campaign_id") or _first_campaign()
    if not query:
        return JSONResponse({"error": "query required"}, status_code=400)
    try:
        results = providers.exa_search(query, (payload or {}).get("num", 5))
    except providers.ProviderUnavailable as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=502)

    created = []
    for res in results:
        row = _insert_signal(campaign_id, query, res)
        created.append(row)
        run = store.add_run(campaign_id, "nova", "discovered", "signal", row["id"],
                            f"Exa: {res.get('title') or res.get('url')}")
        await hub.broadcast({"type": "run", **run})
    return {"created": len(created), "signals": created}


@app.post("/api/leads/{lead_id}/enrich")
async def enrich_lead(lead_id: str, payload: dict | None = None):
    """Scout(Apollo) + MX Guardian(DNS) + Verity(Clearout) on one lead."""
    lead = store.one("leads", lead_id)
    if not lead:
        return JSONResponse({"error": "lead not found"}, status_code=404)
    out: dict[str, Any] = {}
    email = lead.get("professional_email") or ""
    domain = email.split("@")[-1] if "@" in email else None

    # Scout — Apollo enrichment
    try:
        names = (lead.get("full_name") or "").split(" ", 1)
        out["apollo"] = providers.apollo_enrich(
            first_name=names[0] if names else None,
            last_name=names[1] if len(names) > 1 else None,
            organization_name=lead.get("organization_name"), domain=domain, email=email or None)
        r = store.add_run(lead["campaign_id"], "scout", "enrichment_complete", "lead", lead_id, "Apollo enrichment")
        await hub.broadcast({"type": "run", **r})
    except providers.ProviderError as exc:
        out["apollo_error"] = str(exc)

    # MX Guardian — DNS receiving gate
    if domain:
        try:
            out["dns"] = providers.mx_lookup(domain)
            store.update_status("leads", lead_id, "domain_validated")
            r = store.add_run(lead["campaign_id"], "mx_guardian", "domain_validated", "lead", lead_id,
                             f"MX {out['dns'].get('status')} for {domain}")
            await hub.broadcast({"type": "run", **r})
        except providers.ProviderError as exc:
            out["dns_error"] = str(exc)

    # Verity — Clearout mailbox validation
    if email:
        try:
            v = providers.clearout_verify(email)
            out["clearout"] = v
            mapped = {"valid": "valid", "invalid": "invalid"}.get(v.get("status"), "risky")
            store.set_field("leads", lead_id, "email_status", mapped)
            if mapped == "valid":
                store.update_status("leads", lead_id, "email_validated")
            r = store.add_run(lead["campaign_id"], "verity", "email_validated", "lead", lead_id,
                             f"Clearout: {v.get('status')}")
            await hub.broadcast({"type": "run", **r})
        except providers.ProviderError as exc:
            out["clearout_error"] = str(exc)

    return {"lead_id": lead_id, "results": out, "lead": store.one("leads", lead_id)}


def _first_campaign() -> str | None:
    camps = store.rows("campaigns", "status=?", ("active",), limit=1) or store.rows("campaigns", limit=1)
    return camps[0]["id"] if camps else None


def _insert_signal(campaign_id: str, query: str, res: dict) -> dict:
    import sqlite3
    from datetime import datetime, timezone
    sid = "sig_" + os.urandom(5).hex()
    row = {
        "id": sid, "campaign_id": campaign_id, "signal_type": "Live research",
        "title": (res.get("title") or res.get("url") or "Untitled")[:200],
        "summary": (res.get("snippet") or "")[:500], "state": "",
        "source_url": res.get("url") or "", "signal_date": (res.get("published") or "")[:10],
        "status": "discovered", "score": 0, "discovered_by": "nova",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = store.connect()
    try:
        conn.execute("INSERT INTO signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
        conn.commit()
    finally:
        conn.close()
    return row


# --------------------------------------------------------------------------- #
# LLM / model runtime — swappable backend (Ollama / OpenAI-compatible / Claude)
# --------------------------------------------------------------------------- #
@app.get("/api/llm/status")
def llm_status():
    return llm.status()


@app.post("/api/agents/scribe/draft")
async def scribe_draft(payload: dict):
    """Scribe drafts an evidence-backed message from a signal via the configured LLM."""
    signal_id = (payload or {}).get("signal_id")
    advisor = (payload or {}).get("advisor_name", "Your advisor")
    sig = store.one("signals", signal_id) if signal_id else None
    if not sig:
        sigs = store.rows("signals", limit=1)
        sig = sigs[0] if sigs else None
    if not sig:
        return JSONResponse({"error": "no signal available"}, status_code=404)
    result = llm.scribe_draft(sig["title"], sig.get("summary") or "", advisor)
    run = store.add_run(sig["campaign_id"], "scribe", "personalized", "signal", sig["id"],
                        f"Drafted message ({result.get('backend', 'fallback')})")
    await hub.broadcast({"type": "run", **run})
    return {"signal": {"id": sig["id"], "title": sig["title"]}, **result}


@app.post("/api/agents/pulse/classify")
def pulse_classify(payload: dict):
    """Pulse classifies a reply's intent via the configured LLM (or heuristic fallback)."""
    text = (payload or {}).get("text", "").strip()
    if not text:
        return JSONResponse({"error": "text required"}, status_code=400)
    return llm.pulse_classify(text)


@app.get("/healthz")
def healthz():
    return {"ok": True, "db": str(store.DB_PATH), "counts": store.counts()}


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await hub.connect(ws)
    try:
        await ws.send_text(json.dumps({"type": "hello", "counts": store.counts()}))
        while True:
            await ws.receive_text()  # keepalive / ignore inbound
    except WebSocketDisconnect:
        hub.disconnect(ws)
    except Exception:  # noqa: BLE001
        hub.disconnect(ws)
