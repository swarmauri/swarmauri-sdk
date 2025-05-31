from __future__ import annotations

from peagen.queue.model import Task, Result, TaskKind
from .base import TaskHandlerBase


class EvaluateHandler(TaskHandlerBase):
    KIND = TaskKind.EVALUATE
    PROVIDES = {"cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        try:
            score = float(task.payload.get("score", 0))
            return Result(task.id, "ok", {"score": score})
        except Exception as e:
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
