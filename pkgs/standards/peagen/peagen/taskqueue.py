"""Generic task queue leveraging pluggable workers."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from typing import Any, Callable, Optional

from peagen.plugin_registry import registry

from .workers.base import WorkerBase


class TaskQueue:
    """Queue that delegates task execution to a configurable worker."""

    def __init__(self, worker: str = "local", max_workers: int = 1) -> None:
        self.queue: Queue[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]] = Queue()
        worker_cls = registry.get("workers", {}).get(worker)
        if worker_cls is None:
            raise ValueError(f"No worker registered for '{worker}'")
        if not issubclass(worker_cls, WorkerBase):
            raise TypeError(f"Worker '{worker}' must inherit from WorkerBase")
        self.worker: WorkerBase = worker_cls()
        self.max_workers = max_workers

    def add_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Enqueue a callable to be executed."""
        self.queue.put((func, args, kwargs))

    def process(self) -> None:
        """Process tasks until the queue is empty."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            while True:
                try:
                    func, args, kwargs = self.queue.get_nowait()
                except Empty:
                    break
                futures.append(executor.submit(self.worker.execute, func, *args, **kwargs))
            for fut in futures:
                fut.result()
