from __future__ import annotations

from typing import Protocol, Set

from swarmauri_core.ComponentBase import ComponentBase
from peagen.queue.model import Task, Result, TaskKind


class TaskHandler(ComponentBase, Protocol):
    KIND: TaskKind
    PROVIDES: Set[str]

    def dispatch(self, task: Task) -> bool:
        ...

    def handle(self, task: Task) -> Result:
        ...
