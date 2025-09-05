# File: swarmauri/workflows/join_strategies/conditional_join.py

from typing import Any, List, Callable
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class ConditionalJoinStrategy(JoinStrategy):
    """
    File: join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy

    Fires when a user‑provided predicate over the list of buffered inputs returns True.
    """

    def __init__(self, predicate: Callable[[List[Any]], bool]):
        """
        File: conditional_join.py
        Class: ConditionalJoinStrategy
        Method: __init__

        Args:
            predicate: a function that takes the list of buffered inputs and returns a bool.
        """
        self.predicate = predicate

    def mark_complete(self, branch: str) -> None:
        """
        File: conditional_join.py
        Class: ConditionalJoinStrategy
        Method: mark_complete

        No-op for ConditionalJoinStrategy: evaluation solely in is_satisfied.
        """
        pass

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: conditional_join.py
        Class: ConditionalJoinStrategy
        Method: is_satisfied

        Returns True if the predicate over the buffered inputs is True.
        """
        return self.predicate(buffer)

    def reset(self) -> None:
        """
        File: conditional_join.py
        Class: ConditionalJoinStrategy
        Method: reset

        No internal state to reset.
        """
        pass
