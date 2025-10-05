from __future__ import annotations

from typing import Any, Mapping, Tuple
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker

def _pg_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    if dsn:
        return dsn
    if not mapping:
        raise ValueError("postgres_wal requires either a DSN or a mapping.")
    host = str(mapping.get("host") or "localhost")
    port = int(mapping.get("port") or 5432)
    user = quote_plus(str(mapping.get("user") or ""))
    pwd  = quote_plus(str(mapping.get("pwd") or ""))
    db   = quote_plus(str(mapping.get("db") or ""))
    params = []
    app = mapping.get("application_name")
    if app:
        params.append(f"application_name={quote_plus(str(app))}")
    options = mapping.get("options")
    if options:
        params.append(f"options={quote_plus(str(options))}")
    q = f"?{'&'.join(params)}" if params else ""
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}{q}"

def build_postgres_wal_engine(*, mapping: Mapping[str, Any] | None = None, spec: Any | None = None,
                              dsn: str | None = None, **_) -> Tuple[Any, SessionFactory]:
    url = _pg_url(mapping, dsn)
    pool_size    = int((mapping or {}).get("pool_size")    or getattr(spec, "pool_size", 10) or 10)
    max_overflow = int((mapping or {}).get("max_overflow") or getattr(spec, "max", 20)       or 20)

    eng = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        # psycopg3 supports keepalive via libpq; these defaults are reasonable for server-side WAL setups
        connect_args={"options": "-c idle_in_transaction_session_timeout=60000"},
    )

    # Optional: set session characteristics on first connection (no server restarts)
    from sqlalchemy import event
    @event.listens_for(eng, "connect")
    def _configure_postgres(dbapi_conn, conn_record):
        # These are safe per-connection tweaks; WAL is a server config, not set here.
        with dbapi_conn.cursor() as cur:
            cur.execute("SET statement_timeout = 0")
            cur.execute("SET lock_timeout = 0")
            cur.execute("SET synchronous_commit = 'on'")

    return eng, sessionmaker(bind=eng, expire_on_commit=False)

def postgres_wal_capabilities() -> dict[str, Any]:
    return {
        "dialect": "postgresql",
        "supports_transactions": True,
        "async": False,
        "notes": "Uses psycopg3; WAL is server-managed. Connection tuned for OLTP/OLAP-safe defaults.",
    }
