# File: swarmauri/workflows/join_strategies/n_of_m_join.py

from typing import Any, List
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class NofMJoinStrategy(JoinStrategy):
    """
    File: join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    """

    def __init__(self, n: int):
        """
        File: join_strategies/n_of_m_join.py
        Class: NofMJoinStrategy
        Method: __init__

        Args:
            n: number of branch outputs required before firing.
        """
        self.n = n

    def mark_complete(self, branch: str) -> None:
        """
        File: join_strategies/n_of_m_join.py
        Class: NofMJoinStrategy
        Method: mark_complete

        No-op for NofMJoinStrategy: satisfaction is based solely on buffer length.
        """
        pass

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: join_strategies/n_of_m_join.py
        Class: NofMJoinStrategy
        Method: is_satisfied

        Returns True if at least n values are buffered.
        """
        return len(buffer) >= self.n

    def reset(self) -> None:
        """
        File: join_strategies/n_of_m_join.py
        Class: NofMJoinStrategy
        Method: reset

        No internal state to reset for NofMJoinStrategy.
        """
        pass
