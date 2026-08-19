"""Analytics queries — a 1:1 Python port of the four Next.js dashboard routes.

Field names and shapes match ``app/api/dashboard/*/route.js`` exactly so the
JSON contract (and ``backend_test.py``) is preserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import db


# --------------------------------------------------------------------------- #
# stats  (mirrors app/api/dashboard/stats/route.js)
# --------------------------------------------------------------------------- #
def get_stats() -> dict[str, Any]:
    agents = db.query(
        "SELECT COUNT(DISTINCT job_id) AS count FROM search_jobs "
        "WHERE DATE(created_at) = CURRENT_DATE"
    )
    workflows = db.query(
        "SELECT COUNT(*) AS count FROM search_jobs WHERE status = 'running'"
    )
    signals = db.query(
        "SELECT COUNT(*) AS count FROM retirement_signal_searches "
        "WHERE created_at >= NOW() - INTERVAL '24 hours'"
    )
    success = db.query(
        "SELECT COUNT(*) FILTER (WHERE verification_status = 'verified') AS verified, "
        "COUNT(*) AS total FROM retirement_signal_searches"
    )

    verified = int(success[0].get("verified") or 0)
    total = int(success[0].get("total") or 0)
    success_rate = round((verified / total) * 100, 1) if total > 0 else 0
    system_health = "Excellent" if float(success_rate) > 80 else "Degraded"

    return {
        "agentsOnline": int(agents[0].get("count") or 0),
        "workflowsRunning": int(workflows[0].get("count") or 0),
        "signalsToday": int(signals[0].get("count") or 0),
        "successRate": float(success_rate),
        "systemHealth": system_health,
    }


# --------------------------------------------------------------------------- #
# workflows  (mirrors app/api/dashboard/workflows/route.js)
# --------------------------------------------------------------------------- #
def _determine_workflow_type(row: dict[str, Any]) -> str:
    if (row.get("signals_verified") or 0) > 0:
        return "Enrich"
    if (row.get("results_collected") or 0) > 0:
        return "Search"
    return "Outreach"


def _calculate_progress(verified: Any, collected: Any) -> int:
    collected = collected or 0
    if not collected:
        return 0
    return min(round(((verified or 0) / collected) * 100), 100)


def get_workflows() -> dict[str, Any]:
    rows = db.query(
        "SELECT job_id, campaign_id, run_cycle, status, signals_verified, "
        "results_collected, created_at, completed_at FROM search_jobs "
        "ORDER BY created_at DESC LIMIT 10"
    )
    workflows = [
        {
            "id": row.get("job_id"),
            "name": f"{row.get('campaign_id') or 'Campaign'} - {row.get('run_cycle') or 'Cycle'}",
            "type": _determine_workflow_type(row),
            "status": row.get("status") or "pending",
            "progress": _calculate_progress(
                row.get("signals_verified"), row.get("results_collected")
            ),
            "createdAt": _iso(row.get("created_at")),
            "completedAt": _iso(row.get("completed_at")),
        }
        for row in rows
    ]
    return {"workflows": workflows}


# --------------------------------------------------------------------------- #
# signals  (mirrors app/api/dashboard/signals/route.js)
# --------------------------------------------------------------------------- #
def _format_signal_title(row: dict[str, Any]) -> str:
    name = row.get("person_name") or "Unknown"
    org = (
        row.get("organization_name")
        or row.get("business_name")
        or row.get("signal_type")
        or ""
    )
    return f"{name} · {org}" if org else name


def _format_time_ago(timestamp: Any) -> str:
    if not timestamp:
        return "just now"
    then = timestamp if isinstance(timestamp, datetime) else _parse(timestamp)
    if then is None:
        return "just now"
    now = datetime.now(then.tzinfo or timezone.utc)
    diff = now - then
    mins = int(diff.total_seconds() // 60)
    hours = int(diff.total_seconds() // 3600)
    days = int(diff.total_seconds() // 86400)
    if mins < 60:
        return f"{mins}m ago"
    if hours < 24:
        return f"{hours}h ago"
    return f"{days}d ago"


def _categorize_score(score: Any) -> str:
    if not score:
        return "Nurture"
    if score >= 0.8:
        return "Hot"
    if score >= 0.5:
        return "Moderate"
    return "Nurture"


def get_signals() -> dict[str, Any]:
    rows = db.query(
        "SELECT id, signal_type, person_name, organization_name, business_name, "
        "campaign_id, confidence_score, created_at FROM retirement_signal_searches "
        "ORDER BY created_at DESC LIMIT 10"
    )
    signals = [
        {
            "id": row.get("id"),
            "type": row.get("signal_type") or "unknown",
            "title": _format_signal_title(row),
            "campaign": row.get("campaign_id") or "General",
            "timeAgo": _format_time_ago(row.get("created_at")),
            "score": _categorize_score(row.get("confidence_score")),
            "createdAt": _iso(row.get("created_at")),
        }
        for row in rows
    ]
    return {"signals": signals}


# --------------------------------------------------------------------------- #
# analytics  (mirrors app/api/dashboard/analytics/route.js)
# --------------------------------------------------------------------------- #
def get_analytics() -> dict[str, Any]:
    campaigns = db.query(
        "SELECT campaign_id, COUNT(*) AS count FROM retirement_signal_searches "
        "WHERE campaign_id IS NOT NULL GROUP BY campaign_id ORDER BY count DESC LIMIT 5"
    )
    classification = db.query(
        "SELECT CASE "
        "WHEN confidence_score >= 0.8 THEN 'Hot' "
        "WHEN confidence_score >= 0.5 THEN 'Moderate' "
        "ELSE 'Nurture' END AS category, COUNT(*) AS count "
        "FROM retirement_signal_searches GROUP BY category"
    )
    pipeline = db.query(
        "SELECT "
        "(SELECT COUNT(*) FROM retirement_signal_searches) AS signals, "
        "(SELECT COUNT(*) FROM retirement_signal_searches WHERE person_name IS NOT NULL) AS named, "
        "(SELECT COUNT(*) FROM extracted_leads) AS enriched, "
        "(SELECT COUNT(*) FROM extracted_leads WHERE professional_email IS NOT NULL) AS valid_email, "
        "(SELECT COUNT(*) FROM outreach_queue) AS contacted"
    )
    trend = db.query(
        "SELECT DATE(created_at) AS date, COUNT(*) AS count "
        "FROM retirement_signal_searches "
        "WHERE created_at >= NOW() - INTERVAL '7 days' "
        "GROUP BY DATE(created_at) ORDER BY date ASC"
    )

    pipeline_row = pipeline[0] if pipeline else {}
    return {
        "signalsByCampaign": [
            {"campaign": r.get("campaign_id"), "count": int(r.get("count") or 0)}
            for r in campaigns
        ],
        "signalClassification": [
            {"category": r.get("category"), "count": int(r.get("count") or 0)}
            for r in classification
        ],
        "leadsPipeline": {k: int(v or 0) for k, v in pipeline_row.items()},
        "dailyTrend": [
            {"date": _date(r.get("date")), "count": int(r.get("count") or 0)}
            for r in trend
        ],
    }


def get_all() -> dict[str, Any]:
    """Fetch every dataset in one call (used by the dashboard + export renderer)."""
    return {
        "stats": get_stats(),
        "workflows": get_workflows()["workflows"],
        "signals": get_signals()["signals"],
        "analytics": get_analytics(),
    }


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _parse(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)
