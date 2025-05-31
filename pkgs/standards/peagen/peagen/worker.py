from __future__ import annotations

import os
from typing import List, Set

from swarmauri_core.ComponentBase import ComponentBase

from peagen.queue import TaskQueue
from peagen.queue.model import Task, Result
from peagen.plugin_registry import registry
from peagen.handlers import TaskHandlerBase
from peagen.handlers.base import can_handle, ITaskHandler


class InlineWorker(ComponentBase):
    """Simple in-process worker for tests and local runs."""

    def __init__(self, queue: TaskQueue, caps: Set[str] | None = None) -> None:
        super().__init__()
        self.queue = queue
        self.caps = caps or _env_caps()
        self.plugins = _env_plugins()
        self.handlers: List[TaskHandlerBase] = []
        for cls in registry.get("task_handlers", {}).values():
            if self.plugins and cls.__name__ not in self.plugins:
                continue
            inst = cls()  # type: ignore[call-arg]
            if inst.PROVIDES.issubset(self.caps):
                self.handlers.append(inst)

    def pick_handler(self, task: Task) -> ITaskHandler | None:
        for handler in self.handlers:
            if can_handle(task, type(handler), self.caps) and handler.dispatch(task):
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
