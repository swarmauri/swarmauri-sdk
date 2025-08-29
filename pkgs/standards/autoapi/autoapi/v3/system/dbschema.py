# autoapi/v3/system/dbschema.py
"""
DB bootstrap helpers for AutoAPI v3.

This module centralizes a few infra utilities that are useful regardless of
your transport/bindings:

  • register_sqlite_attach(engine, attachments)
      Register a SQLAlchemy 'connect' listener that ensures the given SQLite
      databases are ATTACHed under the provided schema aliases for every new
      connection.

  • ensure_schemas(engine, schemas)
      Best-effort creation of SQL schemas/namespaces for engines that support
      them (PostgreSQL, SQL Server, …). Silently no-ops on SQLite. Uses
      SQLAlchemy DDL where available and ignores "already exists" errors.

  • bootstrap_dbschema(engine, *, schemas=None, sqlite_attachments=None, immediate=True)
      Convenience wrapper that calls ensure_schemas(...) and registers the
      ATTACH listener for SQLite. When `immediate=True`, it also opens a
      connection to apply ATTACH on the spot so the current process can use it
      right away.

All helpers are **framework-agnostic** and rely only on SQLAlchemy.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
)

try:
    from sqlalchemy import event, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import CreateSchema  # type: ignore
except Exception:  # pragma: no cover
    # Soft shims so the module can be imported without SQLAlchemy during tooling.
    event = text = CreateSchema = None  # type: ignore
    Engine = object  # type: ignore


__all__ = [
    "register_sqlite_attach",
    "ensure_schemas",
    "bootstrap_dbschema",
    "sqlite_default_attach_map",
]


# ───────────────────────────────────────────────────────────────────────────────
# SQLite ATTACH helpers
# ───────────────────────────────────────────────────────────────────────────────

_SAFE_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_ident_sqlite(name: str) -> str:
    """
    Very small, defensive identifier quoting for SQLite.
    We accept only [A-Za-z_][A-Za-z0-9_]* by default; otherwise wrap in double quotes.
    """
    if _SAFE_IDENT.match(name or ""):
        return name
    # escape embedded quotes
    return '"' + (name or "").replace('"', '""') + '"'


def _attached_names_sqlite(dbapi_conn: Any) -> set[str]:
    """
    Return the set of currently ATTACHed database names (e.g. {"main", "temp", "logs", ...}).
    """
    names: set[str] = set()
    cur = None
    try:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA database_list")
        for row in cur.fetchall():
            # row: (seq, name, file)
            names.add(str(row[1]))
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass
    return names


def _attach_sqlite_dbapi(dbapi_conn: Any, attachments: Mapping[str, str]) -> None:
    """
    Perform ATTACH for each {schema: filepath} entry on a raw DB-API connection.
    Idempotent: skips schemas already present in PRAGMA database_list.
    """
    cur = None
    try:
        existing = _attached_names_sqlite(dbapi_conn)
        cur = dbapi_conn.cursor()
        for schema, path in (attachments or {}).items():
            if not path:
                continue
            if schema in existing:
                continue
            # ATTACH DATABASE '<path>' AS <schema>
            ident = _quote_ident_sqlite(schema)
            try:
                cur.execute(f"ATTACH DATABASE ? AS {ident}", (path,))
            except Exception:
                # Some drivers don’t allow parameterizing the filename; fall back to literal
                cur.execute(f"ATTACH DATABASE '{path}' AS {ident}")  # nosec: paths are application-provided
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass


def sqlite_default_attach_map(engine: Engine, schemas: Iterable[str]) -> Dict[str, str]:
    """Return a deterministic SQLite ATTACH map for ``schemas``.

    ``main.db`` → ``main__<schema>.db`` (same directory). ``:memory:`` stays
    in-memory.
    """
    db = getattr(getattr(engine, "url", None), "database", None) or ":memory:"
    if db == ":memory:" or str(db).startswith("file::memory:"):
        return {s: ":memory:" for s in schemas}

    p = Path(db)
    suffix = p.suffix if p.suffix else ".db"
    return {s: str(p.with_name(f"{p.stem}__{s}{suffix}")) for s in schemas}


def register_sqlite_attach(engine: Engine, attachments: Mapping[str, str]) -> Any:
    """
    Register a 'connect' listener on *engine* that ATTACHes the given databases
    for every new SQLite connection.

    Args:
        engine: SQLAlchemy Engine bound to a SQLite URL.
        attachments: mapping of {schema_alias: file_path}. Example:
            {"logs": "/var/db/logs.sqlite", "analytics": "/var/db/analytics.sqlite"}

    Returns:
        The listener handle (the function object) so callers can later
        `event.remove(engine, "connect", handle)` if desired.

    Notes:
        - No-op for non-SQLite engines.
        - Idempotent per connection; already-attached schemas are skipped.
    """
    if (
        not hasattr(engine, "dialect")
        or getattr(engine.dialect, "name", "") != "sqlite"
    ):
        # Not SQLite; nothing to do.
        def _noop(*args, **kwargs):
            return None

        return _noop

    if event is None:  # pragma: no cover
        raise RuntimeError("SQLAlchemy is required for register_sqlite_attach")

    def _on_connect(dbapi_connection, connection_record):  # noqa: ANN001 - raw DB-API signature
        try:
            _attach_sqlite_dbapi(dbapi_connection, attachments)
        except Exception:
            # Do not prevent pool checkout if attach fails; caller can inspect later.
            pass

    event.listen(engine, "connect", _on_connect)
    # Keep the attachments visible on the engine for observability
    try:
        engine.info.setdefault("autoapi_sqlite_attachments", dict(attachments))
    except Exception:
        pass
    return _on_connect


# ───────────────────────────────────────────────────────────────────────────────
# Schema creation helpers
# ───────────────────────────────────────────────────────────────────────────────


def ensure_schemas(engine: Engine, schemas: Iterable[str]) -> Tuple[str, ...]:
    """
    Best-effort creation of database schemas/namespaces.

    • PostgreSQL / Redshift / SQL Server: attempts CREATE SCHEMA (ignores "already exists").
    • MySQL/MariaDB: CREATE SCHEMA is an alias for CREATE DATABASE. Use with care.
    • SQLite: no-op.

    Returns:
        A tuple of schema names for which a CREATE was attempted (not a guarantee of success).

    This function intentionally swallows DDL errors to avoid failing application
    startup in environments where the DB principal lacks CREATE privileges.
    """
    if not schemas:
        return tuple()

    if not hasattr(engine, "dialect"):
        return tuple(schemas)

    dialect = getattr(engine.dialect, "name", "")
    attempted: list[str] = []

    if dialect == "sqlite":
        # SQLite doesn’t support CREATE SCHEMA; nothing to do.
        return tuple()

    if text is None:  # pragma: no cover
        raise RuntimeError("SQLAlchemy is required for ensure_schemas")

    # We attempt DDL inside a connection (autocommit as needed by the dialect)
    try:
        with engine.begin() as conn:
            for name in dict.fromkeys(schemas).keys():  # de-dup while preserving order
                if not name:
                    continue
                attempted.append(name)
                try:
                    # First try portable SQLAlchemy DDL (will fail if exists on many dialects)
                    conn.execute(CreateSchema(name))  # type: ignore[arg-type]
                except Exception:
                    # Fallback to IF NOT EXISTS where supported
                    try:
                        if dialect in ("postgresql", "redshift"):
                            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{name}"'))
                        elif dialect in ("mysql", "mariadb"):
                            # MySQL "CREATE SCHEMA" == "CREATE DATABASE"; leave quoting simple
                            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS `{name}`"))
                        elif dialect in ("mssql", "sqlserver"):
                            conn.execute(
                                text(
                                    "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = :n) "
                                    "EXEC('CREATE SCHEMA ' + QUOTENAME(:n))"
                                ),
                                {"n": name},
                            )
                        else:
                            # Generic attempt; many dialects accept IF NOT EXISTS today
                            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {name}"))
                    except Exception:
                        # Ignore lack of privilege or unsupported IF NOT EXISTS
                        pass
    except Exception:
        # Opening/closing connection failures are not fatal here.
        pass

    return tuple(attempted)


# ───────────────────────────────────────────────────────────────────────────────
# Bootstrap convenience
# ───────────────────────────────────────────────────────────────────────────────


def bootstrap_dbschema(
    engine: Engine,
    *,
    schemas: Optional[Iterable[str]] = None,
    sqlite_attachments: Optional[Mapping[str, str]] = None,
    immediate: bool = True,
) -> Dict[str, Any]:
    """
    Convenience bootstrap for process startup:

        bootstrap_dbschema(
            engine,
            schemas=("app", "audit"),
            sqlite_attachments={"logs": "/var/db/logs.sqlite"},
        )

    - Ensures the given schemas exist (best-effort).
    - Registers a SQLite ATTACH handler when appropriate.
    - Optionally performs an immediate ATTACH on a fresh connection so the
      current process can begin using the attached databases without waiting
      for the next pool checkout.

    Returns:
        dict with keys:
          • "attempted_schemas": tuple[str, ...]
          • "sqlite_attachments": dict[str, str]
          • "listener": the event handler object (or None for non-SQLite/no-op)
    """
    attempted = tuple()
    if schemas:
        attempted = ensure_schemas(engine, schemas)

    listener = None
    if sqlite_attachments:
        listener = register_sqlite_attach(engine, sqlite_attachments)

        if immediate and getattr(engine.dialect, "name", "") == "sqlite":
            # Create one connection and apply ATTACH immediately
            try:
                with engine.connect() as conn:
                    # SA Connection has .connection (DB-API)
                    dbapi = getattr(conn, "connection", None)
                    if dbapi is not None:
                        _attach_sqlite_dbapi(dbapi, sqlite_attachments)
            except Exception:
                # Non-fatal – the connect listener will handle future checkouts
                pass

    return {
        "attempted_schemas": attempted,
        "sqlite_attachments": dict(sqlite_attachments or {}),
        "listener": listener,
    }
