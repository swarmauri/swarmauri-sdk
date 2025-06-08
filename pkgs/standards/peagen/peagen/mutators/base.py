from __future__ import annotations

from typing import Protocol

from peagen.handlers.base import TaskHandler


class Mutator(TaskHandler, Protocol):
    """Protocol for handlers that mutate source code."""

    def mutate(self) -> None:
        """Optional helper used by subclasses."""
        ...
