from __future__ import annotations

from typing import Any


def sqlite_capabilities(*, async_: bool, memory: bool) -> dict[str, Any]:
    return {
        "transactional": True,
        "async_native": async_,
        "isolation_levels": {"read_committed", "serializable"},
        "read_only_enforced": False,
        "supports_timeouts": True,
        "supports_ddl": True,
        "engine": "sqlite",
        "memory": bool(memory),
    }


def postgres_capabilities(*, async_: bool) -> dict[str, Any]:
    return {
        "transactional": True,
        "async_native": async_,
        "isolation_levels": {"read_committed", "repeatable_read", "serializable"},
        "read_only_enforced": True,
        "supports_timeouts": True,
        "supports_ddl": True,
        "engine": "postgres",
    }
