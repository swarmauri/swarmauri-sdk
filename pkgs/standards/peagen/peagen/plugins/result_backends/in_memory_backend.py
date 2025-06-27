from __future__ import annotations

from peagen.models.task import TaskRun
from .base import ResultBackendBase


class InMemoryResultBackend(ResultBackendBase):
    """Store TaskRun objects in memory for testing."""

    def __init__(self, **_: object) -> None:
        self.tasks: dict[str, TaskRun] = {}

    async def store(self, task_run: TaskRun) -> None:
        self.tasks[str(task_run.id)] = task_run
