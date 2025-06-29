"""Selector base classes and data structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ParentRef:
    """Reference to a parent commit with its fitness."""

    commit_sha: str
    fitness: float


class Selector:
    """Abstract selector interface."""

    name = "base"

    def select(self) -> List[ParentRef]:
        """Return a list of parent references."""
        raise NotImplementedError
