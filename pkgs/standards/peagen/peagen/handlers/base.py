from __future__ import annotations

from typing import Protocol, Set

from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue.model import Task, Result, TaskKind


class TaskHandler(ComponentBase, Protocol):
    """Protocol for pluggable task handlers."""

    KIND: TaskKind
    PROVIDES: Set[str]

    def dispatch(self, task: Task) -> bool:
        """Return True if this handler should handle ``task``."""

    def handle(self, task: Task) -> Result:
        """Perform domain logic and return a ``Result``."""
