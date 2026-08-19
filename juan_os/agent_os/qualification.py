"""First-party qualification: score voluntary form answers and create a lead.

Implements the Qualification Score (0-40) from juan_cabezas_kb.md — computed
ONLY from what the prospect voluntarily submits. No scraped or inferred data.
The public-signal score (0-60) is separate; a form submission is itself a
first-party 'hot' signal with explicit contact permission.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from . import store

# --- scoring maps (from the knowledgebase) -------------------------------- #
_AGE_10 = {"55-59", "60-64", "65-69", "70-75", "Already retired"}
_AGE_5 = {"50-54"}
_ASSETS = {
    "$1 million+": 15, "$500,000-$999,999": 15, "$250,000-$499,999": 12,
    "$100,000-$249,999": 8, "$50,000-$99,999": 3, "Under $50,000": 0,
    "Prefer not to answer": 0,
}
_TIMING_TIMELINE = {"Already retired": 5, "Within 12 months": 5, "1-3 years": 3,
                    "4-7 years": 1, "More than 7 years": 0, "Not sure": 0}


def score_qualification(form: dict[str, Any]) -> dict[str, Any]:
    """Return the 0-40 qualification score with a per-factor breakdown."""
    age = form.get("age_range", "")
    age_pts = 10 if age in _AGE_10 else (5 if age in _AGE_5 else 0)

    assets_pts = _ASSETS.get(form.get("planning_amount", ""), 0)

    concern = form.get("biggest_concern", "")
    risk_pts = 5 if concern == "Market losses" else (3 if concern in ("Low returns", "Inflation") else 0)
    income_pts = 5 if concern in ("Running out of money", "Creating dependable income") else \
                 (3 if concern in ("Understanding pension options", "Consolidating retirement accounts") else 0)

    timeline_pts = _TIMING_TIMELINE.get(form.get("retirement_timing", ""), 0)

    total = age_pts + assets_pts + risk_pts + income_pts + timeline_pts
    return {"qualification_score": total, "breakdown": {
        "age_or_stage": age_pts, "assets_or_capacity": assets_pts,
        "risk_protection": risk_pts, "income_or_care": income_pts, "timeline": timeline_pts}}


def _band(total: int) -> str:
    if total >= 80:
        return "Hot"
    if total >= 65:
        return "Hot"
    if total >= 50:
        return "Moderate"
    if total >= 35:
        return "Nurture"
    return "Reject"


def submit(form: dict[str, Any]) -> dict[str, Any]:
    """Handle a first-party form submission: score, route to the state campaign,
    create a lead with explicit consent, and return the disposition."""
    state = (form.get("state") or "").upper()[:2]
    email = (form.get("email") or "").strip()
    first_name = (form.get("first_name") or "").strip()
    consent = bool(form.get("consent"))
    track = form.get("track", "annuity")

    # Route to Juan's campaign for this state (public-signal score baseline = 55:
    # a first-party form is a strong, consented intent signal).
    camps = store.rows("campaigns", "advisor_name=? AND target_state=?", ("Juan Cabezas", state), limit=1)
    campaign_id = camps[0]["id"] if camps else (store.rows("campaigns", limit=1) or [{"id": None}])[0]["id"]

    q = score_qualification(form)
    public_signal = 55  # consented first-party intent
    total = min(100, public_signal - 15 + q["qualification_score"])  # blend: public(0-60 scaled) + qual(0-40)
    classification = _band(q["qualification_score"] * 2 + 20)  # emphasize voluntary qual for routing

    lead_id = "lead_" + uuid.uuid4().hex[:10]
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "id": lead_id, "campaign_id": campaign_id, "signal_id": None,
        "full_name": first_name or "First-party lead", "job_title": "",
        "organization_name": f"Self-submitted ({track})", "professional_email": email,
        "state": state, "email_status": "valid" if consent and "@" in email else "unknown",
        "identity_status": "self_declared", "score": total, "classification": classification,
        "status": "outreach_review", "created_at": now,
    }
    conn = store.connect()
    try:
        conn.execute("INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
        # Every Hot first-party lead needs human review before outreach.
        if classification == "Hot":
            conn.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?)",
                         ("appr_" + uuid.uuid4().hex[:10], campaign_id, "lead", lead_id,
                          f"First-party qualified: {first_name or email}",
                          "Consent-based form submission requesting a review — human suitability check required.",
                          "sentinel", "pending", now))
        conn.commit()
    finally:
        conn.close()

    store.add_run(campaign_id, "sentinel", "first_party_form", "lead", lead_id,
                  f"Qualification form: {classification} (qual {q['qualification_score']}/40) — "
                  f"{'wants review' if form.get('want_review') == 'Yes' else 'info only'}")
    return {"lead_id": lead_id, "state": state, "track": track, "consent": consent,
            "classification": classification, "total_score": total, **q}
