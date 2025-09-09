# tigrbl/v2/bootstrap_dbschema.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Mapping, Optional, Set, Dict

from sqlalchemy import event, text
from sqlalchemy.engine import Engine

from .tables import Base

__all__ = ["ensure_schemas", "register_sqlite_attach", "bootstrap_dbschema"]


def _infer_schemas_from_metadata() -> Set[str]:
    md = Base.metadata
    return {t.schema for t in md.tables.values() if getattr(t, "schema", None)}


def _sqlite_default_attach_map(engine: Engine, schemas: Set[str]) -> Mapping[str, str]:
    """
    Derive deterministic sidecar file paths per schema.
    main.db -> main__<schema>.db (same directory).
    For in-memory DBs, attach additional :memory: databases.
    """
    db = engine.url.database or ":memory:"
    if db == ":memory:" or str(db).startswith("file::memory:"):
        return {s: ":memory:" for s in schemas}

    p = Path(db)
    suffix = p.suffix if p.suffix else ".db"
    return {s: str(p.with_name(f"{p.stem}__{s}{suffix}")) for s in schemas}


def register_sqlite_attach(engine: Engine, attach_map: Mapping[str, str]) -> None:
    """
    Register a 'connect' listener that ATTACH-es per-schema databases for SQLite.

    Compatible with SQLAlchemy 1.4 and 2.x, sync and async engines.
    We store state on a private attribute of the **sync** engine and allow
    multiple calls by merging maps.
    """
    import re

    # For AsyncEngine, use its underlying sync engine
    sync_engine: Engine = getattr(
        engine, "sync_engine", engine
    )  # AsyncEngine -> Engine

    ident_ok = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    # Create/merge state on the engine
    state_attr = "_tigrbl_sqlite_attach_state"
    state: Dict[str, object] = getattr(sync_engine, state_attr, None) or {}
    current_map: Dict[str, str] = dict(state.get("map", {}))  # type: ignore[assignment]
    for alias, path in dict(attach_map).items():
        if not ident_ok.match(alias):
            raise ValueError(f"Invalid SQLite alias: {alias!r}")
        current_map[alias] = path
    state["map"] = current_map
    already_registered = bool(state.get("registered", False))
    setattr(sync_engine, state_attr, state)

    if already_registered:
        # Listener already in place; we just updated the map it reads from.
        return

    state["registered"] = True

    @event.listens_for(sync_engine, "connect")
    def _attach(dbapi_conn, _):
        # Read latest map each time a connection is created
        st = getattr(sync_engine, state_attr, {})
        amap: Dict[str, str] = dict(st.get("map", {}))  # type: ignore[assignment]
        if not amap:
            return
        cur = dbapi_conn.cursor()
        try:
            # Attach each schema DB; escape single quotes in paths
            for alias, path in amap.items():
                # Optional: skip if already attached
                # (SQLite allows querying PRAGMA database_list)
                # But ATTACH-ing an already attached name raises,
                # so we conservatively check.
                try:
                    cur.execute("PRAGMA database_list;")
                    attached = {row[1] for row in cur.fetchall()}  # name column
                except Exception:
                    attached = set()
                if alias in attached:
                    continue

                safe_path = str(path).replace("'", "''")
                cur.execute(f"ATTACH DATABASE '{safe_path}' AS {alias}")
        finally:
            cur.close()


def ensure_schemas(engine: Engine, *, extra: Iterable[str] = ()) -> Set[str]:
    """
    Create/prepare all schemas referenced by mapped tables.
    - PostgreSQL (and friends): CREATE SCHEMA IF NOT EXISTS
    - SQLite: auto-ATTACH per-schema sidecar DBs based on engine URL
    """
    schemas = _infer_schemas_from_metadata().union(set(extra))
    if not schemas:
        return set()

    # For AsyncEngine, use its sync_engine for inspection
    sync_engine: Engine = getattr(engine, "sync_engine", engine)

    if sync_engine.dialect.name == "sqlite":
        attach_map = _sqlite_default_attach_map(sync_engine, schemas)
        register_sqlite_attach(sync_engine, attach_map)
        return schemas

    # PostgreSQL / other schema-aware engines
    stmt_tpl = 'CREATE SCHEMA IF NOT EXISTS "{}"'
    # Use engine.begin() on the same (sync) engine
    with sync_engine.begin() as conn:
        for s in sorted(schemas):
            conn.execute(text(stmt_tpl.format(s)))
    return schemas


def bootstrap_dbschema(
    engine: Engine,
    *,
    create_all: bool = False,
    sqlite_attach: Optional[Mapping[str, str]] = None,
):
    """
    Optionally register custom SQLite ATTACH map, ensure schemas, and (optionally) create tables.
    """
    sync_engine: Engine = getattr(engine, "sync_engine", engine)

    if sqlite_attach and sync_engine.dialect.name == "sqlite":
        register_sqlite_attach(sync_engine, sqlite_attach)

    ensure_schemas(sync_engine)

    if create_all:
        Base.metadata.create_all(sync_engine)
