# File: swarmauri/workflows/join_strategies/per_arrival_join.py

from typing import Any, List
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class PerArrivalJoinStrategy(JoinStrategy):
    """
    Fires for each buffered arrival that meets its transition condition,
    allowing the converged state to execute on every new branch result.
    """

    def __init__(self):
        """
        File: per_arrival_join.py
        Class: PerArrivalJoinStrategy
        Method: __init__

        No internal state required; each buffer arrival triggers execution.
        """
        pass

    def mark_complete(self, branch: str) -> None:
        """
        File: per_arrival_join.py
        Class: PerArrivalJoinStrategy
        Method: mark_complete

        No-op: we rely solely on the buffer contents.
        """
        pass

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: per_arrival_join.py
        Class: PerArrivalJoinStrategy
        Method: is_satisfied

        Return True if there is at least one new buffered input,
        so each arrival will trigger.
        """
        return len(buffer) > 0

    def reset(self) -> None:
        """
        File: per_arrival_join.py
        Class: PerArrivalJoinStrategy
        Method: reset

        No internal state to reset.
        """
        pass
