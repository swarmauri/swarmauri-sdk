from __future__ import annotations

from typing import Any, Mapping, Tuple
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker

def _build_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    """Build a Snowflake SQLAlchemy URL.
    If `dsn` is provided and already begins with 'snowflake://', return it unchanged.
    Otherwise construct from mapping keys: account, user, pwd, db, schema, warehouse, role.
    """
    if dsn:
        return dsn if dsn.startswith("snowflake://") else dsn

    if not mapping:
        raise ValueError("snowflake_engine requires either a DSN or a mapping.")

    account  = str(mapping.get("account") or "").strip()
    user     = str(mapping.get("user") or "").strip()
    pwd      = str(mapping.get("pwd") or "").strip()
    database = str(mapping.get("db") or "").strip()
    schema   = str(mapping.get("schema") or "").strip()
    wh       = str(mapping.get("warehouse") or "").strip()
    role     = str(mapping.get("role") or "").strip()

    if not (account and user and pwd and database and schema):
        missing = [k for k, v in [("account", account), ("user", user), ("pwd", pwd),
                                  ("db", database), ("schema", schema)] if not v]
        raise ValueError(f"Missing required Snowflake mapping keys: {', '.join(missing)}")

    qp = []
    if wh:   qp.append(f"warehouse={quote_plus(wh)}")
    if role: qp.append(f"role={quote_plus(role)}")
    params = f"?{'&'.join(qp)}" if qp else ""

    return (
        f"snowflake://{quote_plus(user)}:{quote_plus(pwd)}@{account}/"
        f"{quote_plus(database)}/{quote_plus(schema)}{params}"
    )

def snowflake_engine(*, mapping: Mapping[str, Any] | None = None,
                     spec: Any | None = None,
                     dsn: str | None = None,
                     **_) -> Tuple[Any, SessionFactory]:
    """Tigrbl engine builder for Snowflake.
    Returns a (sqlalchemy.Engine, sessionmaker) tuple.
    Signature accepts (mapping, spec, dsn) to match Tigrbl's registry call-site.
    """
    url = _build_url(mapping, dsn)

    # Pool knobs: prefer values from mapping, then from spec, else defaults.
    pool_size    = int((mapping or {}).get("pool_size")    or getattr(spec, "pool_size", 10) or 10)
    max_overflow = int((mapping or {}).get("max_overflow") or getattr(spec, "max", 20)       or 20)

    eng = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        connect_args={"client_session_keep_alive": True},
    )
    return eng, sessionmaker(bind=eng, expire_on_commit=False)

def snowflake_capabilities() -> dict[str, Any]:
    return {
        "dialect": "snowflake",
        "supports_transactions": True,
        "async": False,
        "notes": "Requires snowflake-sqlalchemy; returns blocking SQLAlchemy sessions.",
    }
