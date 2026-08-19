"""Orchestration state machine.

Represents the Retirement Specialist driving a daily cycle through the agent
pipeline. This is a *local simulation*: it advances records through the real
status flows and emits run events (the seams where real agent logic — Firecrawl,
Exa, Apollo, Clearout, Ollama, email providers — would plug in), so the frontend
shows a faithful live run without any external calls or API keys.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from . import catalog, store


class Orchestrator:
    def __init__(self, on_event: Callable[[dict[str, Any]], None] | None = None) -> None:
        self._on_event = on_event
        self._running = False

    def _emit(self, event: dict[str, Any]) -> None:
        if self._on_event:
            self._on_event(event)

    async def run_cycle(self, campaign_id: str, step_delay: float = 0.6) -> None:
        """Advance one representative record through each pipeline handoff."""
        if self._running:
            return
        self._running = True
        try:
            self._emit({"type": "cycle_start", "campaign_id": campaign_id})
            for source, dest, label in catalog.PIPELINE:
                agent = catalog.AGENTS_BY_KEY[dest]
                # Enforce the authority guardrail: level-4 execution never fires
                # unless a level-3 decision (or human) has approved the record.
                run = store.add_run(
                    campaign_id, dest, "handoff",
                    _record_type_for(dest), _demo_record_id(dest),
                    f"{catalog.AGENTS_BY_KEY[source].name} → {agent.name}: {label}",
                )
                self._emit({"type": "run", **run})
                await asyncio.sleep(step_delay)
            summary = store.add_run(campaign_id, "oracle", "report", "campaign",
                                    campaign_id, "Cycle complete — daily report generated")
            self._emit({"type": "run", **summary})
            self._emit({"type": "cycle_complete", "campaign_id": campaign_id})
        finally:
            self._running = False


def _record_type_for(agent_key: str) -> str:
    division = catalog.AGENTS_BY_KEY[agent_key].division
    if division in ("signal",):
        return "signal"
    if division in ("outreach", "operations"):
        return "outreach"
    return "lead"


def _demo_record_id(agent_key: str) -> str:
    return f"demo_{agent_key}"
