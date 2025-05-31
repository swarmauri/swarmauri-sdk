from __future__ import annotations

import os
import signal
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Set

from peagen.queue import make_queue
from peagen.queue.model import Result, Task, TaskKind
from peagen.plugin_registry import registry
from peagen.handlers.base import can_handle, ITaskHandler




@dataclass
class WorkerConfig:
    queue_url: str
    caps: Set[str]
    plugins: Set[str] | None = None
    concurrency: int = 1
    idle_exit: int = 600
    max_uptime: int = 3600

    @classmethod
    def from_env(cls) -> "WorkerConfig":
        return cls(
            queue_url=os.environ.get("QUEUE_URL", "stub://"),
            caps=set(filter(None, os.environ.get("WORKER_CAPS", "").split(","))),
            plugins=set(filter(None, os.environ.get("WORKER_PLUGINS", "").split(","))) or None,
            concurrency=int(os.environ.get("WORKER_CONCURRENCY", "1")),
            idle_exit=int(os.environ.get("WORKER_IDLE_EXIT", "600")),
            max_uptime=int(os.environ.get("WORKER_MAX_UPTIME", "3600")),
        )


class OneShotWorker:
    """Simplified one-shot worker as described in the technical brief."""

    def __init__(self, cfg: WorkerConfig) -> None:
        self.cfg = cfg
        provider = "redis" if cfg.queue_url.startswith("redis") else "stub"
        self.queue = make_queue(provider, url=cfg.queue_url)
        self.id = uuid.uuid4().hex
        self.start_ts = time.time()
        self.last_task_ts = time.time()
        self._shutdown = False
        signal.signal(signal.SIGTERM, self._sigterm)

    # ------------------------------------------------------------ lifecycle
    def _sigterm(self, *_: Any) -> None:
        self._shutdown = True

    def _select_handler(self, task: Task) -> ITaskHandler | None:
        handlers: Iterable[type] = registry.get("task_handlers", {}).values()
        for cls in handlers:
            if self.cfg.plugins and cls.__name__ not in self.cfg.plugins:
                continue
            if can_handle(task, cls, self.cfg.caps):
                inst = cls()  # type: ignore[call-arg]
                if inst.dispatch(task):
                    return inst
        return None

    # ------------------------------------------------------------ main loop
    def run(self) -> str:
        """Run until a single task is processed or exit condition met."""
        exit_reason = "idle"
        while True:
            if self._shutdown:
                exit_reason = "signal"
                break
            if time.time() - self.start_ts > self.cfg.max_uptime:
                exit_reason = "timeout"
                break

            task = self.queue.pop(timeout=1)
            if task is None:
                if time.time() - self.last_task_ts > self.cfg.idle_exit:
                    exit_reason = "idle"
                    break
                continue

            self.last_task_ts = time.time()
            if not task.requires <= self.cfg.caps:
                # put it back for someone else
                self.queue.enqueue(task)
                self.queue.ack(task.id)
                continue

            handler = self._select_handler(task)
            if handler is None:
                self.queue.enqueue(task)
                self.queue.ack(task.id)
                continue

            try:
                t0 = time.time()
                result = handler.handle(task)
                runtime = time.time() - t0
                self.queue.push_result(result)
                self.queue.ack(task.id)
                exit_reason = result.status
            except Exception as exc:  # pragma: no cover - simple log
                result = Result(task.id, "error", {"msg": str(exc)})
                self.queue.push_result(result)
                self.queue.ack(task.id)
                exit_reason = "error"
            break

        return exit_reason


__all__ = ["OneShotWorker", "WorkerConfig", "ITaskHandler"]
