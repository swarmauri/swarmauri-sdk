from __future__ import annotations

from typing import Protocol
from swarmauri_base.ComponentBase import ComponentBase

from .model import Task, Result


class TaskQueueBase(ComponentBase):
    def enqueue(self, task: Task) -> None:
        raise NotImplementedError

    def pop(self, block: bool = True, timeout: int = 1) -> Task | None:
        raise NotImplementedError

    def ack(self, task_id: str) -> None:
        raise NotImplementedError

    def push_result(self, result: Result) -> None:
        raise NotImplementedError

    def wait_for_result(self, task_id: str, timeout: int) -> Result | None:
        raise NotImplementedError

    def requeue_orphans(self, idle_ms: int, max_batch: int) -> int:
        raise NotImplementedError
