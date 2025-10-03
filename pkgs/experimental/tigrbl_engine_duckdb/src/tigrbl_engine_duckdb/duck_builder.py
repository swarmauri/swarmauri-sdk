from __future__ import annotations
from typing import Any, Callable, Optional, Tuple, Mapping

import duckdb

from tigrbl.session.spec import SessionSpec
from .duck_session import DuckDBSession

SessionFactory = Callable[[], Any]

def duckdb_engine(
    *,
    path: Optional[str] = None,                 # None or ":memory:" → in-memory
    read_only: bool = False,
    threads: Optional[int] = None,
    pragmas: Optional[Mapping[str, Any]] = None,
    mapping: Optional[Mapping[str, Any]] = None,  # accepted but not required
    spec: Optional[Any] = None,                   # accepted for signature parity
    dsn: Optional[str] = None,                    # accepted for signature parity
) -> Tuple[Any, SessionFactory]:
    """
    Build a DuckDB 'engine' and a session factory that yields DuckDBSession.
    No SQLAlchemy; pure duckdb bindings.
    Returns:
        (engine_handle, sessionmaker)
    """
    db_path = path or ":memory:"

    def mk_session(spec_in: Optional[SessionSpec] = None) -> DuckDBSession:
        conn = duckdb.connect(db_path, read_only=read_only)
        # Pragmas per-session for determinism.
        if threads is not None:
            conn.execute(f"PRAGMA threads={int(threads)}")
        if pragmas:
            for k, v in pragmas.items():
                if isinstance(v, bool):
                    v = "true" if v else "false"
                conn.execute(f"PRAGMA {k}={v}")
        return DuckDBSession(conn, spec_in)

    engine_handle = {"kind": "duckdb", "path": db_path, "read_only": read_only}
    return engine_handle, mk_session

def duckdb_capabilities() -> dict[str, Any]:
    """
    Capability advertisement for session_ctx validation.
    DuckDB provides MVCC snapshot-style isolation.
    """
    return {
        "transactional": True,
        "isolation_levels": {"snapshot", "repeatable_read"},
        "read_only_enforced": False,
        "async_native": False,
    }
