"""Juan OS command-line interface.

    python -m juan_os                 # serve the live dashboard (default)
    python -m juan_os serve --port 8000
    python -m juan_os export --out juan_analytics.html
    python -m juan_os check           # verify Neon connectivity + row counts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import db, queries, render


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    print(f"Juan OS → http://{args.host}:{args.port}  (Ctrl+C to stop)")
    uvicorn.run("juan_os.app:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    try:
        data = queries.get_all()
    except db.ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    html = render.build_report_html(data)
    out = Path(args.out)
    out.write_text(html, encoding="utf-8")
    print(f"Exported analytics report → {out.resolve()}")
    print("This file is self-contained (no network) — share it or open it offline.")
    return 0


def _cmd_check(_args: argparse.Namespace) -> int:
    try:
        counts = db.check()
    except db.ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("DB connected. Table row counts:")
    for table, count in counts.items():
        print(f"  {table:<28} {count}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="juan_os", description="Juan Operating System (local)")
    sub = parser.add_subparsers(dest="command")

    serve = sub.add_parser("serve", help="Run the live dashboard server (default)")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true", help="Auto-reload on code changes (dev)")
    serve.set_defaults(func=_cmd_serve)

    export = sub.add_parser("export", help="Write a static, shareable HTML analytics report")
    export.add_argument("--out", default="juan_analytics.html", help="Output file path")
    export.set_defaults(func=_cmd_export)

    check = sub.add_parser("check", help="Verify Neon connectivity and print row counts")
    check.set_defaults(func=_cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        # default to `serve` with defaults
        args = parser.parse_args(["serve"])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
