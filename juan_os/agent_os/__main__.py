"""Run the Agent OS backend:  python -m juan_os.agent_os"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="juan_os.agent_os", description="VBS Local Agent OS backend")
    parser.add_argument("command", nargs="?", default="serve",
                        choices=["serve", "seed-juan", "daily"],
                        help="serve (default) | seed-juan (load campaigns) | daily (run the daily task)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--advisor", default="Juan Cabezas")
    parser.add_argument("--loop", action="store_true", help="daily: stay resident and repeat")
    parser.add_argument("--interval", type=int, default=14400, help="daily --loop: seconds between passes")
    args = parser.parse_args()

    if args.command == "seed-juan":
        from . import store
        store.init_db()
        camps = store.seed_juan_cabezas()
        print(f"Juan Cabezas campaigns loaded ({len(camps)}):")
        for c in camps:
            print(f"  [{c['target_state']}] {c['name']}  · systems: {c['target_retirement_system']}  · min score {c['minimum_signal_score']}")
        return 0

    if args.command == "daily":
        from . import daily_runner
        return daily_runner.run_cli(args.advisor, args.loop, args.interval)

    import uvicorn

    print(f"Agent OS API → http://{args.host}:{args.port}  (WebSocket at /ws)")
    uvicorn.run("juan_os.agent_os.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
