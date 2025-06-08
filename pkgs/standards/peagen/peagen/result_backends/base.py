from __future__ import annotations

from typing import Protocol, Iterable
from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue.model import Result, TaskKind


class ResultBackend(ComponentBase, Protocol):
    def save(self, result: Result) -> None:
        ...

    def get(self, task_id: str) -> Result | None:
        ...

    def iter(self, kind: TaskKind | None = None) -> Iterable[Result]:
        ...
