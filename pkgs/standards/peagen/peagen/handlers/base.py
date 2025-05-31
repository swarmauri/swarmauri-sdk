from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Set, Type

from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue.model import Task, Result, TaskKind


class ITaskHandler(ABC):
    """Interface for pluggable task handlers."""

    KIND: TaskKind
    PROVIDES: Set[str]

    @abstractmethod
    def dispatch(self, task: Task) -> bool:
        """Quick pre-check for ``task``."""

    @abstractmethod
    def handle(self, task: Task) -> Result:
        """Perform domain work and return a :class:`Result`."""


class TaskHandlerBase(ComponentBase, ITaskHandler):
    """Convenience base class implementing :class:`ITaskHandler`."""

    KIND: TaskKind
    PROVIDES: Set[str]

    def dispatch(self, task: Task) -> bool:  # pragma: no cover - trivial
        return task.kind == self.KIND


def can_handle(
    task: Task, handler_cls: Type[ITaskHandler], worker_caps: Set[str]
) -> bool:
    """Return ``True`` if ``handler_cls`` can service ``task`` under ``worker_caps``."""
    provides = getattr(handler_cls, "PROVIDES", set())
    if task.kind != getattr(handler_cls, "KIND", None):
        return False
    if not task.requires.issubset(provides):
        return False
    if not provides.issubset(worker_caps):
        return False
    return True


TaskHandler = TaskHandlerBase

__all__ = ["ITaskHandler", "TaskHandlerBase", "TaskHandler", "can_handle"]
