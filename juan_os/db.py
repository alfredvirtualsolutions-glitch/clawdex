"""Neon Postgres connection layer.

Mirrors the connection pattern in ``lib/db/neon.js`` (SSL required, pooled),
but for Python via psycopg 3. The app requires a live Neon connection: if
``NEON_DATABASE_URL`` is not set, callers get a clear, actionable error.
"""

from __future__ import annotations

import os
from typing import Any, Sequence

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

# Load .env once at import time so `NEON_DATABASE_URL` is available everywhere.
load_dotenv()


class ConfigError(RuntimeError):
    """Raised when the Neon connection is not configured."""


_pool: ConnectionPool | None = None


def database_url() -> str:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise ConfigError(
            "NEON_DATABASE_URL is not configured. Copy .env.example to .env and "
            "set NEON_DATABASE_URL to your Neon Postgres connection string."
        )
    return url


def get_pool() -> ConnectionPool:
    """Return a lazily-created connection pool (matches neon.js pooling)."""
    global _pool
    if _pool is None:
        conninfo = database_url()
        # Neon requires SSL. Respect an sslmode already in the URL, else force it.
        kwargs: dict[str, Any] = {}
        if "sslmode=" not in conninfo:
            kwargs["sslmode"] = "require"
        _pool = ConnectionPool(
            conninfo=conninfo,
            min_size=1,
            max_size=10,
            timeout=10,
            max_idle=30,
            kwargs=kwargs,
            open=True,
        )
    return _pool


def query(sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    """Run a read query and return rows as a list of dicts."""
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def check() -> dict[str, Any]:
    """Verify connectivity and return per-table row counts (used by CLI/health).

    Raises ConfigError if NEON_DATABASE_URL is not set so callers can report an
    unconfigured state distinctly from a connection/query error.
    """
    database_url()  # raise ConfigError early if unconfigured
    tables = [
        "search_jobs",
        "retirement_signal_searches",
        "extracted_leads",
        "outreach_queue",
    ]
    counts: dict[str, Any] = {}
    for table in tables:
        try:
            rows = query(f"SELECT COUNT(*) AS count FROM {table}")
            counts[table] = int(rows[0]["count"])
        except Exception as exc:  # noqa: BLE001 - report per-table, keep going
            counts[table] = f"error: {exc}"
    return counts


def close() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
