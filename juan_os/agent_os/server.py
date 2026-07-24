"""Agent OS backend — FastAPI REST API + WebSocket live activity stream.

Local-first: runs entirely against the SQLite store, no external providers
required. Endpoints back every frontend surface; the WebSocket streams run
events so the UI has real-time run visibility.

    python -m juan_os.agent_os          # serve on 127.0.0.1:8787
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from . import catalog, store
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
