"""DB-independent smoke tests for the Juan OS renderers.

These feed sample data dicts straight into the chart + template layer, so they
verify the neon dashboard and the static export render correctly without needing
a live Neon connection.
"""

from __future__ import annotations

from juan_os import charts, render

SAMPLE = {
    "stats": {
        "agentsOnline": 24,
        "workflowsRunning": 18,
        "signalsToday": 1842,
        "successRate": 98.6,
        "systemHealth": "Excellent",
    },
    "workflows": [
        {"id": "j1", "name": "Company Research - c1", "type": "Search",
         "status": "running", "progress": 65, "createdAt": None, "completedAt": None},
        {"id": "j2", "name": "Lead Enrichment - c2", "type": "Enrich",
         "status": "completed", "progress": 100, "createdAt": None, "completedAt": None},
    ],
    "signals": [
        {"id": 1, "type": "funding", "title": "Acme · Datacore",
         "campaign": "Funding", "timeAgo": "2m ago", "score": "Hot", "createdAt": None},
        {"id": 2, "type": "hiring", "title": "Jane Doe · Growth",
         "campaign": "Hiring", "timeAgo": "5m ago", "score": "Moderate", "createdAt": None},
    ],
    "analytics": {
        "signalsByCampaign": [
            {"campaign": "Funding", "count": 42},
            {"campaign": "Hiring", "count": 30},
            {"campaign": "Intent", "count": 18},
        ],
        "signalClassification": [
            {"category": "Hot", "count": 12},
            {"category": "Moderate", "count": 24},
            {"category": "Nurture", "count": 36},
        ],
        "leadsPipeline": {"signals": 1842, "named": 900, "enriched": 400,
                          "valid_email": 220, "contacted": 80},
        "dailyTrend": [
            {"date": "2026-07-17", "count": 120},
            {"date": "2026-07-18", "count": 180},
            {"date": "2026-07-19", "count": 90},
        ],
    },
}


def test_bar_chart_renders_svg():
    svg = charts.bar_chart(SAMPLE["analytics"]["signalsByCampaign"], "campaign", "count")
    assert svg.startswith("<svg")
    assert "Funding" in svg


def test_doughnut_and_line_render():
    doughnut = charts.doughnut_chart(SAMPLE["analytics"]["signalClassification"], "category", "count")
    line = charts.line_chart(SAMPLE["analytics"]["dailyTrend"], "date", "count")
    assert "<svg" in doughnut and "Hot" in doughnut
    assert "<polyline" in line


def test_charts_handle_empty_data():
    assert "No data" in charts.bar_chart([], "campaign", "count")
    assert "No data" in charts.line_chart([], "date", "count")


def test_dashboard_html():
    html = render.build_dashboard_html(SAMPLE, refresh_seconds=30)
    assert "Juan Operating System" in html
    assert "Active Workflows" in html
    assert "Live Signal Feed" in html
    assert "98.6%" in html
    assert 'http-equiv="refresh"' in html  # live page auto-refreshes


def test_report_html_is_self_contained():
    html = render.build_report_html(SAMPLE)
    assert "Static analytics snapshot" in html
    assert "http" not in html.split("<style>")[0].lower() or "DOCTYPE" in html
    # no external resource references (fully offline)
    assert "src=" not in html
    assert "<link" not in html
    assert "cdn" not in html.lower()
