from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Tuple
import time
import threading

from .base import TaskQueueBase
from .model import Task, Result


class StubQueue(TaskQueueBase):
    """In-memory queue used for development and CI."""

    def __init__(self) -> None:
        self._todo: Deque[Task] = deque()
        self._inflight: Dict[str, Tuple[Task, float]] = {}
        self._done: Dict[str, Result] = {}
        self._lock = threading.Lock()

    def pending_count(self) -> int:
        with self._lock:
            return len(self._todo) + len(self._inflight)

    # ------------------------------------------------------------------ producer
    def enqueue(self, task: Task) -> None:
        with self._lock:
            self._todo.append(task)

    # ------------------------------------------------------------------ consumer
    def pop(self, block: bool = True, timeout: int = 1) -> Task | None:
        end = time.time() + timeout if block else 0
        while True:
            with self._lock:
                if self._todo:
                    task = self._todo.popleft()
                    self._inflight[task.id] = (task, time.time() * 1000)
                    return task
            if not block or time.time() >= end:
                return None
            time.sleep(0.01)

    def ack(self, task_id: str) -> None:
        with self._lock:
            self._inflight.pop(task_id, None)

    # ------------------------------------------------------------------ admin
    def push_result(self, result: Result) -> None:
        with self._lock:
            self._done[result.task_id] = result

    def wait_for_result(self, task_id: str, timeout: int) -> Result | None:
        end = time.time() + timeout
        while True:
            with self._lock:
                res = self._done.get(task_id)
                if res:
                    return res
            if time.time() >= end:
                return None
            time.sleep(0.05)

    def requeue_orphans(self, idle_ms: int = 60000, max_batch: int = 50) -> int:
        now = time.time() * 1000
        moved = 0
        with self._lock:
            for tid, (task, ts) in list(self._inflight.items()):
                if now - ts > idle_ms and moved < max_batch:
                    self._todo.appendleft(task)
                    del self._inflight[tid]
                    moved += 1
        return moved
