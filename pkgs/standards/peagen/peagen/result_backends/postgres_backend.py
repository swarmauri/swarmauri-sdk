from __future__ import annotations

from .base import ResultBackendBase
from peagen.queue.model import Result, TaskKind


class PostgresBackend(ResultBackendBase):
    """Placeholder for a Postgres JSONB backend."""

    def __init__(self, dsn: str) -> None:  # pragma: no cover - sketch
        self.dsn = dsn

    def save(self, result: Result) -> None:  # pragma: no cover - sketch
        raise NotImplementedError

    def get(self, task_id: str) -> Result | None:  # pragma: no cover - sketch
        raise NotImplementedError

    def iter(self, kind: TaskKind | None = None):  # pragma: no cover - sketch
        raise NotImplementedError
