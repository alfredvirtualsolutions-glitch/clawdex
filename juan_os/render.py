"""Jinja2 rendering: live dashboard page and static exportable report.

Both surfaces share the same neon look. Charts are pre-rendered to inline SVG
(see ``charts.py``) so the output is fully self-contained — no JS, no CDN.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import charts

_TEMPLATES = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES)),
    autoescape=select_autoescape(["html"]),
)


def _charts_for(data: dict[str, Any]) -> dict[str, Markup]:
    analytics = data["analytics"]
    return {
        "campaign_chart": Markup(
            charts.bar_chart(analytics["signalsByCampaign"], "campaign", "count", charts.COLORS["purple"])
        ),
        "classification_chart": Markup(
            charts.doughnut_chart(analytics["signalClassification"], "category", "count")
        ),
        "trend_chart": Markup(
            charts.line_chart(analytics["dailyTrend"], "date", "count", charts.COLORS["orange"])
        ),
    }


def _context(data: dict[str, Any], *, refresh_seconds: int | None) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "stats": data["stats"],
        "workflows": data["workflows"],
        "signals": data["signals"],
        "analytics": data["analytics"],
        "pipeline": data["analytics"].get("leadsPipeline", {}),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "refresh_seconds": refresh_seconds,
    }
    ctx.update(_charts_for(data))
    return ctx


def build_dashboard_html(data: dict[str, Any], *, refresh_seconds: int | None = 30) -> str:
    """Render the live dashboard (auto-refreshes to stay current)."""
    return _env.get_template("dashboard.html").render(**_context(data, refresh_seconds=refresh_seconds))


def build_report_html(data: dict[str, Any]) -> str:
    """Render the static, shareable analytics report (no refresh, no network)."""
    return _env.get_template("report.html").render(**_context(data, refresh_seconds=None))
