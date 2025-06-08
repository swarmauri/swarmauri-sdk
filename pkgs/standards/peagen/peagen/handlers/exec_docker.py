from __future__ import annotations

from peagen.queue.model import Task, Result, TaskKind
from .base import TaskHandler


class ExecuteDockerHandler(TaskHandler):
    KIND = TaskKind.EXECUTE
    PROVIDES = {"docker", "cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        try:
            metrics = {"speed_ms": 1.0, "peak_kb": 1.0}
            return Result(task.id, "ok", metrics)
        except Exception as e:
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
