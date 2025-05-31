from __future__ import annotations

from typing import Protocol
from swarmauri_core.ComponentBase import ComponentBase

from .model import Task, Result


class TaskQueueBase(ComponentBase):
    def enqueue(self, task: Task) -> None:
        ...

    def pop(self, block: bool = True, timeout: int = 1) -> Task | None:
        ...

    def ack(self, task_id: str) -> None:
        ...

    def push_result(self, result: Result) -> None:
        ...

    def wait_for_result(self, task_id: str, timeout: int) -> Result | None:
        ...

    def requeue_orphans(self, idle_ms: int, max_batch: int) -> int:
        ...
