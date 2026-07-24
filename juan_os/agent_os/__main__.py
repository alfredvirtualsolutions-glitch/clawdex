"""Run the Agent OS backend:  python -m juan_os.agent_os"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="juan_os.agent_os", description="VBS Local Agent OS backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    import uvicorn

    print(f"Agent OS API → http://{args.host}:{args.port}  (WebSocket at /ws)")
    uvicorn.run("juan_os.agent_os.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
