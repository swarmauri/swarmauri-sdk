from __future__ import annotations

from typing import Iterable
from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue.model import Result, TaskKind



class ResultBackendBase(ComponentBase):
    def save(self, result: Result) -> None:
        raise NotImplementedError

    def get(self, task_id: str) -> Result | None:
        raise NotImplementedError

    def iter(self, kind: TaskKind | None = None) -> Iterable[Result]:
        raise NotImplementedError
