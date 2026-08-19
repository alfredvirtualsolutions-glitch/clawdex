"""Daily Runner — the local autonomous agent that executes the daily task.

One command runs the whole daily cycle for an advisor across every active state
campaign (Juan Cabezas → FL/TX/CA), then rolls up a consolidated report. It is
the concrete "agent who runs the daily task": point the model runtime at any
backend (e.g. LLM_BACKEND=pokee → pokee-isaac) and this driver does the rest —
no other agent required.

    python -m juan_os.agent_os daily                 # run once (good for cron)
    python -m juan_os.agent_os daily --loop --interval 14400   # stay resident, every 4h
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable

from . import llm, store
from .orchestrator import Orchestrator


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_daily(*, advisor: str = "Juan Cabezas", cycles_per_campaign: int = 1,
                    step_delay: float = 0.4,
                    on_event: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
    """Run one full daily pass for the advisor's active campaigns."""
    store.init_db()
    camps = store.rows("campaigns", "advisor_name=? AND status=?", (advisor, "active"))
    if not camps and advisor == "Juan Cabezas":
        store.seed_juan_cabezas()
        camps = store.rows("campaigns", "advisor_name=? AND status=?", (advisor, "active"))

    orch = Orchestrator(on_event=on_event)
    summary: dict[str, Any] = {
        "advisor": advisor, "backend": llm.backend(), "model": llm.model_name(),
        "llm_configured": llm.available(), "started_at": _now(), "campaigns": [], "total_steps": 0,
    }
    for c in camps:
        before = store.counts()["runs"]
        for _ in range(max(1, cycles_per_campaign)):
            await orch.run_cycle(c["id"], step_delay=step_delay)
        steps = store.counts()["runs"] - before
        summary["campaigns"].append({"state": c["target_state"], "name": c["name"], "steps": steps})
        summary["total_steps"] += steps

    summary["finished_at"] = _now()
    summary["counts"] = store.counts()
    # Persist a daily-report marker (Oracle) tied to the first campaign.
    if camps:
        store.add_run(camps[0]["id"], "oracle", "daily_report", "campaign", camps[0]["id"],
                      f"Daily Runner complete — {len(camps)} campaigns, {summary['total_steps']} steps "
                      f"(runtime: {summary['backend']}/{summary['model']})")
    return summary


async def daily_loop(interval_seconds: int, **kwargs: Any) -> None:
    """Resident mode: run the daily pass, then sleep, forever."""
    while True:
        s = await run_daily(**kwargs)
        print(f"[{s['finished_at']}] daily pass: {len(s['campaigns'])} campaigns, "
              f"{s['total_steps']} steps · next in {interval_seconds}s")
        await asyncio.sleep(interval_seconds)


def _print_event(e: dict[str, Any]) -> None:
    if e.get("type") == "run":
        print(f"  [{e.get('agent_key','?'):<16}] {e.get('detail','')}")


def run_cli(advisor: str, loop: bool, interval: int) -> int:
    """CLI entrypoint for `python -m juan_os.agent_os daily`."""
    print(f"Daily Runner · advisor={advisor} · model runtime={llm.backend()}/{llm.model_name()} "
          f"({'configured' if llm.available() else 'heuristic fallback'})\n")
    if loop:
        try:
            asyncio.run(daily_loop(interval, advisor=advisor, on_event=_print_event))
        except KeyboardInterrupt:
            print("\nstopped.")
        return 0
    s = asyncio.run(run_daily(advisor=advisor, on_event=_print_event))
    print("\n=== Daily report ===")
    for c in s["campaigns"]:
        print(f"  {c['state']:<3} {c['name']:<40} {c['steps']} steps")
    print(f"\nTotal: {len(s['campaigns'])} campaigns · {s['total_steps']} pipeline steps")
    print(f"Runtime: {s['backend']}/{s['model']}  ·  leads={s['counts']['leads']} "
          f"hot={s['counts']['leads_hot']} approvals_pending={s['counts']['approvals_pending']}")
    return 0
