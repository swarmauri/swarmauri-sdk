from __future__ import annotations

from typing import Set

from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue.model import Task, Result, TaskKind




class TaskHandlerBase(ComponentBase):
    """Protocol for pluggable task handlers."""

    KIND: TaskKind
    PROVIDES: Set[str]

    def dispatch(self, task: Task) -> bool:
        raise NotImplementedError

    def handle(self, task: Task) -> Result:
        """Return True if this handler should handle ``task``."""
        raise NotImplementedError

    def handle(self, task: Task) -> Result:
        """Perform domain logic and return a ``Result``."""
        raise NotImplementedError
