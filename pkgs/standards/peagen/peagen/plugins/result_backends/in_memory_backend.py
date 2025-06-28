from __future__ import annotations

from peagen.orm import TaskRunModel
from .base import ResultBackendBase


class InMemoryResultBackend(ResultBackendBase):
    """Store TaskRun objects in memory for testing."""

    def __init__(self, **_: object) -> None:
        self.tasks: dict[str, TaskRunModel] = {}

    async def store(self, task_run: TaskRunModel) -> None:
        self.tasks[str(task_run.id)] = task_run
