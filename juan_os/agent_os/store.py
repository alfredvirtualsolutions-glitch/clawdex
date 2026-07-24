"""Local-first SQLite store for the Agent OS.

Local by default (a single SQLite file), matching the "SQLite / Neon Data API"
integration boundary in the architecture. Seeds realistic sample data on first
run so every frontend surface has content without any external providers.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from . import catalog

DB_PATH = Path(os.environ.get("AGENT_OS_DB", Path(__file__).parent / "agent_os.db"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY, name TEXT, advisor_name TEXT, advisor_license_states TEXT,
  target_state TEXT, target_profession TEXT, target_retirement_system TEXT,
  minimum_signal_score INTEGER, status TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS signals (
  id TEXT PRIMARY KEY, campaign_id TEXT, signal_type TEXT, title TEXT, summary TEXT,
  state TEXT, source_url TEXT, signal_date TEXT, status TEXT, score INTEGER,
  discovered_by TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY, campaign_id TEXT, signal_id TEXT, full_name TEXT, job_title TEXT,
  organization_name TEXT, professional_email TEXT, state TEXT, email_status TEXT,
  identity_status TEXT, score INTEGER, classification TEXT, status TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS outreach (
  id TEXT PRIMARY KEY, campaign_id TEXT, lead_id TEXT, subject TEXT, body TEXT,
  status TEXT, provider TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY, campaign_id TEXT, record_type TEXT, record_id TEXT, title TEXT,
  reason TEXT, requested_by TEXT, status TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY, campaign_id TEXT, agent_key TEXT, division TEXT, action TEXT,
  record_type TEXT, record_id TEXT, status TEXT, detail TEXT, created_at TEXT
);
"""


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        cur = conn.execute("SELECT COUNT(*) AS c FROM campaigns")
        if cur.fetchone()["c"] == 0:
            _seed(conn)
    finally:
        conn.close()


def _seed(conn: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc)
    campaigns = [
        ("California educators — CalSTRS window", "Maria Alvarez", "CA", "California", "K-12 Educator", "CalSTRS", 70, "active"),
        ("Texas district retirements — TRS", "James Whitfield", "TX", "Texas", "School Administrator", "TRS of Texas", 65, "active"),
        ("Nevada business-owner succession", "Dana Cole", "NV", "Nevada", "Business Owner", "NVPERS", 75, "paused"),
    ]
    camp_ids = []
    for name, advisor, lic, state, prof, system, minscore, status in campaigns:
        cid = _uid("camp")
        camp_ids.append((cid, state))
        conn.execute(
            "INSERT INTO campaigns VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cid, name, advisor, lic, state, prof, system, minscore, status, _now()),
        )

    sig_types = ["Retirement announcement", "Pension deadline", "403(b) rollover", "Early-retirement program",
                 "Business succession", "Retirement workshop"]
    orgs = ["Riverside Unified", "Austin ISD", "Sierra Holdings LLC", "Clark County SD", "Reno Family Dentistry", "Valley Charter"]
    names = ["Patricia Nguyen", "Robert Hayes", "Linda Okafor", "Daniel Reyes", "Susan Kim", "Marcus Bell"]
    classes = [("Hot", 88), ("Moderate", 71), ("Nurture", 52), ("Hot", 84), ("Moderate", 66), ("Nurture", 48)]
    email_states = ["valid", "valid", "catch_all", "valid", "risky", "unknown"]
    id_states = ["identity_verified", "identity_verified", "partial_match", "identity_verified", "manual_review", "organization_only"]

    for i in range(12):
        cid, state = camp_ids[i % len(camp_ids)]
        sid = _uid("sig")
        stype = sig_types[i % len(sig_types)]
        status = catalog.SIGNAL_FLOW[min(i % 6, 5)]
        score = 40 + (i * 5) % 55
        conn.execute(
            "INSERT INTO signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (sid, cid, stype, f"{stype} — {orgs[i % len(orgs)]}",
             f"Public {stype.lower()} identified at {orgs[i % len(orgs)]}.", state,
             f"https://example-source.org/news/{sid}", (now - timedelta(days=i)).date().isoformat(),
             status, score, ["nova", "atlas", "echo"][i % 3], _now()),
        )
        # Every other signal has produced a lead
        if i % 2 == 0:
            lid = _uid("lead")
            cls, lscore = classes[i % len(classes)]
            lstatus = catalog.LEAD_FLOW[min(i, len(catalog.LEAD_FLOW) - 1)]
            conn.execute(
                "INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (lid, cid, sid, names[i % len(names)], "Educator / Owner", orgs[i % len(orgs)],
                 f"{names[i % len(names)].split()[0].lower()}@{orgs[i % len(orgs)].split()[0].lower()}.org",
                 state, email_states[i % len(email_states)], id_states[i % len(id_states)],
                 lscore, cls, lstatus, _now()),
            )
            if cls == "Hot":
                aid = _uid("appr")
                conn.execute(
                    "INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?)",
                    (aid, cid, "lead", lid, f"Hot lead: {names[i % len(names)]}",
                     "Hot leads require human review before outreach (Sentinel + Retirement Specialist).",
                     "sentinel", "pending", _now()),
                )

    # A few outreach drafts
    lead_rows = conn.execute("SELECT * FROM leads WHERE classification='Moderate' LIMIT 3").fetchall()
    for lr in lead_rows:
        oid = _uid("out")
        conn.execute(
            "INSERT INTO outreach VALUES (?,?,?,?,?,?,?,?)",
            (oid, lr["campaign_id"], lr["id"], f"A quick note about your recent update",
             "Referencing the verified public signal, a short educational note with a Clarity Review CTA.",
             "personalized", "resend", _now()),
        )

    # Seed run/activity events across divisions
    actions = [
        ("nova", "signal", "discovered", "Ran morning signal search (CA) — 6 candidate URLs"),
        ("delta", "signal", "verified", "Verified pension-deadline signal at Riverside Unified"),
        ("pathfinder", "signal", "url_intelligence_ready", "Mapped 4 staff/contact URLs"),
        ("lens", "lead", "raw", "Extracted 3 contacts with source provenance"),
        ("anchor", "lead", "identity_verified", "Matched signal person to staff directory"),
        ("verity", "lead", "email_validated", "Mailbox validation: valid"),
        ("compass", "lead", "scored", "Scored lead 88 → Hot"),
        ("sentinel", "approval", "manual_review", "Hot lead queued for human review"),
        ("scribe", "outreach", "personalized", "Drafted evidence-backed message"),
        ("critic", "outreach", "quality_checked", "No hallucinated facts; footer present"),
        ("oracle", "campaign", "report", "Daily report generated"),
    ]
    for i, (agent, rtype, status, detail) in enumerate(actions):
        conn.execute(
            "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (_uid("run"), camp_ids[0][0], agent, catalog.AGENTS_BY_KEY[agent].division,
             status, rtype, _uid(rtype), "ok", detail,
             (now - timedelta(minutes=(len(actions) - i) * 7)).isoformat()),
        )
    conn.commit()


# --------------------------------------------------------------------------- #
# Generic helpers
# --------------------------------------------------------------------------- #
def rows(table: str, where: str = "", params: tuple = (), order: str = "created_at DESC",
         limit: int | None = None) -> list[dict[str, Any]]:
    conn = connect()
    try:
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        if order:
            sql += f" ORDER BY {order}"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def one(table: str, rid: str) -> dict[str, Any] | None:
    conn = connect()
    try:
        r = conn.execute(f"SELECT * FROM {table} WHERE id=?", (rid,)).fetchone()
        return dict(r) if r else None
    finally:
        conn.close()


def update_status(table: str, rid: str, status: str) -> dict[str, Any] | None:
    conn = connect()
    try:
        conn.execute(f"UPDATE {table} SET status=? WHERE id=?", (status, rid))
        conn.commit()
    finally:
        conn.close()
    return one(table, rid)


def set_field(table: str, rid: str, field: str, value: Any) -> dict[str, Any] | None:
    conn = connect()
    try:
        conn.execute(f"UPDATE {table} SET {field}=? WHERE id=?", (value, rid))
        conn.commit()
    finally:
        conn.close()
    return one(table, rid)


def add_run(campaign_id: str, agent_key: str, action: str, record_type: str,
            record_id: str, detail: str, status: str = "ok") -> dict[str, Any]:
    agent = catalog.AGENTS_BY_KEY.get(agent_key)
    row = {
        "id": _uid("run"), "campaign_id": campaign_id, "agent_key": agent_key,
        "division": agent.division if agent else "", "action": action,
        "record_type": record_type, "record_id": record_id, "status": status,
        "detail": detail, "created_at": _now(),
    }
    conn = connect()
    try:
        conn.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
        conn.commit()
    finally:
        conn.close()
    return row


def counts() -> dict[str, int]:
    conn = connect()
    try:
        def c(sql: str, p: tuple = ()) -> int:
            return conn.execute(sql, p).fetchone()[0]
        return {
            "campaigns": c("SELECT COUNT(*) FROM campaigns"),
            "campaigns_active": c("SELECT COUNT(*) FROM campaigns WHERE status='active'"),
            "signals": c("SELECT COUNT(*) FROM signals"),
            "signals_verified": c("SELECT COUNT(*) FROM signals WHERE status NOT IN ('discovered','pending_verification')"),
            "leads": c("SELECT COUNT(*) FROM leads"),
            "leads_hot": c("SELECT COUNT(*) FROM leads WHERE classification='Hot'"),
            "outreach": c("SELECT COUNT(*) FROM outreach"),
            "approvals_pending": c("SELECT COUNT(*) FROM approvals WHERE status='pending'"),
            "runs": c("SELECT COUNT(*) FROM runs"),
        }
    finally:
        conn.close()
