# autoapi/v2/bootstrap_dbschema.py
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Mapping, Optional, Set
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
    if db == ":memory:" or db.startswith("file::memory:"):
        return {s: ":memory:" for s in schemas}
    p = Path(db)
    suffix = p.suffix if p.suffix else ".db"
    return {s: str(p.with_name(f"{p.stem}__{s}{suffix}")) for s in schemas}

def register_sqlite_attach(engine: Engine, attach_map: Mapping[str, str]) -> None:
    import re
    ident_ok = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    # Avoid double registration if initialize_* runs twice (dev reloaders, tests).
    if engine.info.get("autoapi_sqlite_attach_registered"):
        return
    engine.info["autoapi_sqlite_attach_registered"] = True
    engine.info["autoapi_sqlite_attach_map"] = dict(attach_map)

    @event.listens_for(engine, "connect")
    def _attach(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        try:
            for alias, path in engine.info["autoapi_sqlite_attach_map"].items():
                if not ident_ok.match(alias):
                    raise ValueError(f"Invalid SQLite alias: {alias!r}")
                cur.execute(f"ATTACH DATABASE '{path}' AS {alias}")
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

    if engine.dialect.name == "sqlite":
        attach_map = _sqlite_default_attach_map(engine, schemas)
        register_sqlite_attach(engine, attach_map)
        return schemas

    # PostgreSQL / other schema-aware engines
    stmt_tpl = 'CREATE SCHEMA IF NOT EXISTS "{}"'
    with engine.begin() as conn:
        for s in sorted(schemas):
            conn.execute(text(stmt_tpl.format(s)))
    return schemas

def bootstrap_dbschema(engine: Engine, *, create_all: bool = False, sqlite_attach: Optional[Mapping[str, str]] = None):
    if sqlite_attach and engine.dialect.name == "sqlite":
        register_sqlite_attach(engine, sqlite_attach)

    ensure_schemas(engine)

    if create_all:
        Base.metadata.create_all(engine)
