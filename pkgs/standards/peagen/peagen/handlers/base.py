from __future__ import annotations

from typing import Set

from swarmauri_base.ComponentBase import ComponentBase

from peagen.queue.model import Task, Result, TaskKind

class TaskHandlerBase(ComponentBase):
    """Protocol for pluggable task handlers."""

    KIND: TaskKind
    PROVIDES: Set[str]

    def dispatch(self, task: Task) -> bool:
        raise NotImplementedError

    def should_handle(self, task: Task) -> bool:
        """Return ``True`` if this handler should process ``task``."""
        raise NotImplementedError

    def handle(self, task: Task) -> Result:
        """Perform domain logic and return a ``Result``."""
        raise NotImplementedError
