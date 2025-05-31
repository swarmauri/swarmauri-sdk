from __future__ import annotations

import os
import signal
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Protocol, Set, List

from peagen.queue import make_queue
from peagen.queue.model import Result, Task, TaskKind
from peagen.plugin_registry import registry
from peagen.handlers.base import TaskHandlerBase
from swarmauri_base.ComponentBase import ComponentBase


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

    def _select_handler(self, task: Task) -> TaskHandlerBase | None:
        handlers: Iterable[type] = registry.get("task_handlers", {}).values()
        for cls in handlers:
            if self.cfg.plugins and cls.__name__ not in self.cfg.plugins:
                continue
            provides = getattr(cls, "PROVIDES", set())
            if task.requires <= provides <= self.cfg.caps:
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

class InlineWorker(ComponentBase):
    """Simple in-process worker for tests and local runs."""

    def __init__(self, queue: make_queue.__annotations__["return"], caps: Set[str] | None = None) -> None:
        super().__init__()
        self.queue = queue
        self.caps = caps or _env_caps()
        self.plugins = _env_plugins()
        self.handlers: List[TaskHandlerBase] = []
        for cls in registry.get("task_handlers", {}).values():
            if self.plugins and cls.__name__ not in self.plugins:
                continue
            inst = cls()  # type: ignore[call-arg]
            if getattr(inst, "PROVIDES", set()).issubset(self.caps):
                self.handlers.append(inst)

    def pick_handler(self, task: Task) -> TaskHandlerBase | None:
        for handler in self.handlers:
            if task.requires.issubset(getattr(handler, "PROVIDES", set())) and handler.dispatch(task):
                return handler
        return None

    def run_once(self) -> Result | None:
        task = self.queue.pop(block=False)
        if not task:
            return None
        handler = self.pick_handler(task)
        if not handler:
            return None
        try:
            result = handler.handle(task)
        except Exception as e:  # safety net
            result = Result(task.id, "error", {"msg": str(e), "retryable": False})
        if result.status != "skip":
            self.queue.push_result(result)
            self.queue.ack(task.id)
        return result


def _env_caps() -> Set[str]:
    caps = os.getenv("WORKER_CAPS", "cpu").split(",")
    return {c.strip() for c in caps if c.strip()}


def _env_plugins() -> Set[str]:
    val = os.getenv("WORKER_PLUGINS", "")
    return {p.strip() for p in val.split(",") if p.strip()}


__all__ = ["OneShotWorker", "WorkerConfig", "TaskHandlerBase", "InlineWorker"]