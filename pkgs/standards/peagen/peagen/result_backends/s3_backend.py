from __future__ import annotations

from .base import ResultBackendBase
from peagen.queue.model import Result, TaskKind


class S3Backend(ResultBackendBase):
    """Placeholder for an S3/MinIO backend."""

    def __init__(self, bucket: str) -> None:  # pragma: no cover - sketch
        self.bucket = bucket

    def save(self, result: Result) -> None:  # pragma: no cover - sketch
        raise NotImplementedError

    def get(self, task_id: str) -> Result | None:  # pragma: no cover - sketch
        raise NotImplementedError

    def iter(self, kind: TaskKind | None = None):  # pragma: no cover - sketch
        raise NotImplementedError
