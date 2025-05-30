"""Simple worker that executes callables in the local Python process."""

from typing import Any, Callable

from .base import WorkerBase


class LocalWorker(WorkerBase):
    """Execute tasks by calling them directly."""

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
