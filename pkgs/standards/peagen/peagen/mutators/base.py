from __future__ import annotations

from peagen.handlers.base import TaskHandlerBase


class Mutator(TaskHandlerBase):
    """Base class for handlers that mutate source code."""

    def mutate(self) -> None:
        """Optional helper used by subclasses."""
        raise NotImplementedError
