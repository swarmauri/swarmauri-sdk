from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence
from types import SimpleNamespace

from ..engine import resolver as _resolver

try:  # pragma: no cover
    from sqlalchemy import event, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import CreateSchema  # type: ignore
except Exception:  # pragma: no cover
    event = text = CreateSchema = None  # type: ignore
    Engine = object  # type: ignore

from ..config.constants import __SAFE_IDENT__

__all__ = [
    "register_sqlite_attach",
    "ensure_schemas",
    "bootstrap_dbschema",
    "sqlite_default_attach_map",
    "initialize",
]


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------


def _quote_ident_sqlite(name: str) -> str:
    if __SAFE_IDENT__.match(name or ""):
        return name
    return '"' + (name or "").replace('"', '""') + '"'


def _attached_names_sqlite(dbapi_conn: Any) -> set[str]:
    names: set[str] = set()
    cur = None
    try:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA database_list")
        for row in cur.fetchall():
            names.add(str(row[1]))
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass
    return names


def _attach_sqlite_dbapi(dbapi_conn: Any, attachments: Mapping[str, str]) -> None:
    cur = None
    try:
        existing = _attached_names_sqlite(dbapi_conn)
        cur = dbapi_conn.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        for schema, path in (attachments or {}).items():
            if not path or schema in existing:
                continue
            ident = _quote_ident_sqlite(schema)
            try:
                cur.execute(f"ATTACH DATABASE ? AS {ident}", (path,))
            except Exception:
                cur.execute(f"ATTACH DATABASE '{path}' AS {ident}")  # nosec: application-provided paths
    finally:
        try:
            cur and cur.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def sqlite_default_attach_map(engine: Engine, schemas: Iterable[str]) -> Dict[str, str]:
    """Return a deterministic SQLite ATTACH map for ``schemas``."""
    db = getattr(getattr(engine, "url", None), "database", None) or ":memory:"
    if db == ":memory:" or str(db).startswith("file::memory:"):
        return {s: ":memory:" for s in schemas}
    p = Path(db)
    suffix = p.suffix if p.suffix else ".db"
    return {s: str(p.with_name(f"{p.stem}__{s}{suffix}")) for s in schemas}


def register_sqlite_attach(engine: Engine, attachments: Mapping[str, str]) -> Any:
    if (
        not hasattr(engine, "dialect")
        or getattr(engine.dialect, "name", "") != "sqlite"
    ):
        return None

    def _connect_listener(dbapi_conn, _):  # type: ignore[override]
        try:
            _attach_sqlite_dbapi(dbapi_conn, attachments)
        except Exception:
            pass

    event.listen(engine, "connect", _connect_listener)
    return _connect_listener


def ensure_schemas(engine: Engine, schemas: Iterable[str]) -> Sequence[str]:
    if not schemas:
        return tuple()
    if not hasattr(engine, "dialect"):
        return tuple(schemas)

    dialect = getattr(engine.dialect, "name", "")
    attempted: list[str] = []

    if dialect == "sqlite":
        return tuple()

    if text is None:  # pragma: no cover
        raise RuntimeError("SQLAlchemy is required for ensure_schemas")

    try:
        with engine.begin() as conn:
            for name in dict.fromkeys(schemas).keys():
                if not name:
                    continue
                attempted.append(name)
                try:
                    conn.execute(CreateSchema(name))  # type: ignore[arg-type]
                except Exception:
                    try:
                        if dialect in ("postgresql", "redshift"):
                            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{name}"'))
                        elif dialect in ("mysql", "mariadb"):
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
                            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {name}"))
                    except Exception:
                        pass
    except Exception:
        pass

    return tuple(attempted)


def bootstrap_dbschema(
    engine: Engine,
    *,
    schemas: Optional[Iterable[str]] = None,
    sqlite_attachments: Optional[Mapping[str, str]] = None,
    immediate: bool = True,
) -> Dict[str, Any]:
    attempted = tuple()
    if schemas:
        attempted = ensure_schemas(engine, schemas)

    listener = None
    if sqlite_attachments:
        listener = register_sqlite_attach(engine, sqlite_attachments)
        if immediate and getattr(engine.dialect, "name", "") == "sqlite":
            try:
                with engine.connect() as conn:
                    dbapi = getattr(conn, "connection", None)
                    if dbapi is not None:
                        _attach_sqlite_dbapi(dbapi, sqlite_attachments)
            except Exception:
                pass

    return {
        "attempted_schemas": attempted,
        "sqlite_attachments": dict(sqlite_attachments or {}),
        "listener": listener,
    }


# ---------------------------------------------------------------------------
# Internal creation helper
# ---------------------------------------------------------------------------


def _create_all_on_bind(
    bind,
    *,
    schemas: Iterable[str] | None = None,
    sqlite_attachments: Mapping[str, str] | None = None,
    tables: Iterable[Any] | None = None,
) -> None:
    engine = getattr(bind, "engine", bind)
    tables = list(tables or [])

    schema_names = set(schemas or [])
    for t in tables:
        if getattr(t, "schema", None):
            schema_names.add(t.schema)

    attachments = sqlite_attachments
    if attachments is None and getattr(engine.dialect, "name", "") == "sqlite":
        if schema_names:
            attachments = sqlite_default_attach_map(engine, schema_names)

    if attachments:
        bootstrap_dbschema(
            engine,
            schemas=schema_names,
            sqlite_attachments=attachments,
            immediate=True,
        )
    else:
        ensure_schemas(engine, schema_names)

    by_meta: dict[Any, list[Any]] = {}
    for t in tables:
        by_meta.setdefault(t.metadata, []).append(t)
    for md, group in by_meta.items():
        md.create_all(bind=bind, checkfirst=True, tables=group)


# ---------------------------------------------------------------------------
# Public initialize
# ---------------------------------------------------------------------------


def initialize(
    obj: Any,
    *,
    schemas: Iterable[str] | None = None,
    sqlite_attachments: Mapping[str, str] | None = None,
    tables: Iterable[Any] | None = None,
):
    if getattr(obj, "_ddl_executed", False):
        return

    ts = list(tables or [])
    if not ts:
        if hasattr(obj, "_collect_tables"):
            ts = list(obj._collect_tables())  # type: ignore[attr-defined]
        elif hasattr(obj, "__table__"):
            ts = [obj.__table__]  # type: ignore[attr-defined]

    kwargs: Dict[str, Any] = {}
    if hasattr(obj, "_collect_tables"):
        kwargs["api"] = obj
    elif hasattr(obj, "__table__"):
        kwargs["model"] = obj

    prov = _resolver.resolve_provider(**kwargs)
    if prov is None:
        raise ValueError("Engine provider is not configured")

    def _bootstrap(db):
        bind = db.get_bind() if hasattr(db, "get_bind") else db
        _create_all_on_bind(
            bind,
            schemas=schemas,
            sqlite_attachments=sqlite_attachments,
            tables=ts,
        )

        if hasattr(obj, "models"):
            tables_map = {
                name: getattr(m, "__table__", None)
                for name, m in getattr(obj, "models").items()
                if hasattr(m, "__table__")
            }
            existing = getattr(obj, "tables", None)
            if isinstance(existing, dict):
                existing.update(tables_map)
            elif existing is not None:
                for k, v in tables_map.items():
                    setattr(existing, k, v)
            else:
                setattr(obj, "tables", SimpleNamespace(**tables_map))

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running event loop; fall back to fully synchronous bootstrap
        with next(prov.get_db()) as db:
            _bootstrap(db)
        setattr(obj, "_ddl_executed", True)
        return
    else:
        # If we're already inside an event loop but the provider is synchronous
        # (i.e. ``get_db`` is neither coroutine nor async generator), we can
        # bootstrap synchronously as well. This mirrors previous "initialize_sync"
        # behaviour and allows ``initialize()`` to be invoked without ``await``
        # from async contexts when using sync engines.
        if not inspect.iscoroutinefunction(
            prov.get_db
        ) and not inspect.isasyncgenfunction(prov.get_db):
            with next(prov.get_db()) as db:
                _bootstrap(db)
            setattr(obj, "_ddl_executed", True)

            class _Completed:
                def __await__(self):  # pragma: no cover - trivial
                    if False:
                        yield None
                    return None

            return _Completed()

        async def _inner():
            if inspect.isasyncgenfunction(prov.get_db):
                async for adb in prov.get_db():
                    await adb.run_sync(_bootstrap)
                    break
            else:
                gen = prov.get_db()
                db = next(gen)
                try:
                    if hasattr(db, "run_sync"):
                        await db.run_sync(_bootstrap)
                    else:
                        bind = db.get_bind()
                        await asyncio.to_thread(
                            _create_all_on_bind,
                            bind,
                            schemas=schemas,
                            sqlite_attachments=sqlite_attachments,
                            tables=ts,
                        )
                finally:
                    try:
                        next(gen)
                    except StopIteration:
                        pass
            setattr(obj, "_ddl_executed", True)

        return _inner()
