from __future__ import annotations

from typing import Any, Mapping, Tuple
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker


def _sqlite_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    if dsn:
        return dsn
    if not mapping:
        raise ValueError("sqlite_wal requires either a DSN or a mapping.")
    path = str(mapping.get("path") or "").strip()
    if not path:
        raise ValueError(
            "sqlite_wal mapping requires 'path' to a file-backed database for WAL."
        )
    # Ensure parent directory exists (does not create the DB yet)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite+pysqlite:///{path}"


def build_sqlite_wal_engine(
    *,
    mapping: Mapping[str, Any] | None = None,
    spec: Any | None = None,
    dsn: str | None = None,
    **_,
) -> Tuple[Any, SessionFactory]:
    url = _sqlite_url(mapping, dsn)
    # For SQLite, SQLAlchemy ignores pool_size for pysqlite's default NullPool; keep simple defaults.
    eng = create_engine(
        url,
        connect_args={"check_same_thread": False},  # allow use across threads if needed
        future=True,
    )

    @event.listens_for(eng, "connect")
    def _enable_wal(dbapi_conn, conn_record):
        cur = dbapi_conn.cursor()
        try:
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("PRAGMA synchronous=NORMAL;")
            cur.execute("PRAGMA wal_autocheckpoint=1000;")
            cur.execute("PRAGMA foreign_keys=ON;")
        finally:
            cur.close()

    return eng, sessionmaker(bind=eng, expire_on_commit=False)


def sqlite_wal_capabilities() -> dict[str, Any]:
    return {
        "dialect": "sqlite",
        "supports_transactions": True,
        "async": False,
        "notes": "Enables WAL mode via PRAGMA on connect; file-based DB required.",
    }
