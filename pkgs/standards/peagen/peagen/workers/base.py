"""Base class for task execution workers."""

from typing import Any, Callable


class WorkerBase:
    """Execute tasks in a specific environment."""

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute *func* with provided arguments."""
        raise NotImplementedError("Worker subclasses must implement execute()")
