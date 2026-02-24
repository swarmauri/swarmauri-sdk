from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any


@dataclass
class TableState:
    pk: str
    rows: dict[Any, dict[str, Any]] = field(default_factory=dict)
    next_id: int = 1


@dataclass
class DatabaseState:
    tables: dict[str, TableState] = field(default_factory=dict)


class InMemoryEngine:
    def __init__(
        self, *, namespace: str = "default", enforce_schema: bool = False
    ) -> None:
        self.namespace = namespace
        self.enforce_schema = enforce_schema
        self._lock = RLock()
        self._state = DatabaseState()

    def _get_state(self) -> DatabaseState:
        return self._state

    def _commit(self, new_state: DatabaseState) -> None:
        with self._lock:
            self._state = new_state

    def _with_lock(self) -> RLock:
        return self._lock
