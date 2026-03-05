from __future__ import annotations
from typing import Any, Dict


def sqlite_capabilities(*, async_: bool, memory: bool) -> Dict[str, Any]:
    # SQLite supports transactional semantics; isolation semantics differ from server DBs.
    # We expose a conservative set that higher layers can reason about.
    return {
        "transactional": True,
        "async_native": async_,  # async layer is provided by aiosqlite/SQLAlchemy AsyncEngine
        "isolation_levels": {"read_committed", "serializable"},
        "read_only_enforced": False,  # app layer should enforce; file-open RO may be used externally
        "supports_timeouts": True,
        "supports_ddl": True,
        "engine": "sqlite",
        "memory": bool(memory),
    }


def postgres_capabilities(*, async_: bool) -> Dict[str, Any]:
    return {
        "transactional": True,
        "async_native": async_,
        "isolation_levels": {"read_committed", "repeatable_read", "serializable"},
        "read_only_enforced": True,
        "supports_timeouts": True,
        "supports_ddl": True,
        "engine": "postgres",
    }
