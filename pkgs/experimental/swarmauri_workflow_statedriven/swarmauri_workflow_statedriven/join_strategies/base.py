# File: swarmauri/workflows/join_strategies/base.py

from abc import ABC, abstractmethod
from typing import Any, List


class JoinStrategy(ABC):
    """
    Base class for join strategies determining when a converging state
    should fire based on buffered branch outputs.
    """

    @abstractmethod
    def mark_complete(self, branch: str) -> None:
        """
        Record that the branch identified by 'branch' has completed.

        Args:
            branch: the name of the branch/state that just completed.
        """
        ...

    @abstractmethod
    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        Check if the join condition is met given the list of buffered inputs.

        Args:
            buffer: list of values buffered for the converging state.
        Returns:
            True if the join condition is satisfied; False otherwise.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """
        Reset any internal state to allow reuse of this strategy for subsequent joins.
        """
        ...
