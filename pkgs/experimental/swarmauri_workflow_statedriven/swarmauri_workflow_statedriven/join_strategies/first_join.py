# File: swarmauri/workflows/join_strategies/first_join.py

from typing import Any, List
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class FirstJoinStrategy(JoinStrategy):
    """
    File: join_strategies/first_join.py
    Class: FirstJoinStrategy

    Fires as soon as the first branch completes.
    """

    def __init__(self):
        """
        File: join_strategies/first_join.py
        Class: FirstJoinStrategy
        Method: __init__

        Initialize internal flag to track first completion.
        """
        self._completed = False

    def mark_complete(self, branch: str) -> None:
        """
        File: join_strategies/first_join.py
        Class: FirstJoinStrategy
        Method: mark_complete

        Record that a branch has completed; only the first matters.
        """
        if not self._completed:
            self._completed = True

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: join_strategies/first_join.py
        Class: FirstJoinStrategy
        Method: is_satisfied

        Return True as soon as at least one branch has been buffered.
        """
        return self._completed or len(buffer) >= 1

    def reset(self) -> None:
        """
        File: join_strategies/first_join.py
        Class: FirstJoinStrategy
        Method: reset

        Reset internal state for reuse.
        """
        self._completed = False
