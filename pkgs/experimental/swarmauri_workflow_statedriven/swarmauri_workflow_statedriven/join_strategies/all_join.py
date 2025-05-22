# File: swarmauri/workflows/join_strategies/all_join.py

from typing import Any, List
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class AllJoinStrategy(JoinStrategy):
    """
    File: join_strategies/all_join.py
    Class: AllJoinStrategy

    Fires only when *all* incoming branches have completed.
    The Workflow engine will call `configure()` with the
    true in‑degree of the target state, so you never set it by hand.
    """

    def __init__(self):
        """
        File: join_strategies/all_join.py
        Class: AllJoinStrategy
        Method: __init__

        `expected_count` starts at 0 and is set by the engine.
        """
        self.expected_count: int = 0

    def configure(self, expected_count: int) -> None:
        """
        File: join_strategies/all_join.py
        Class: AllJoinStrategy
        Method: configure

        Args:
            expected_count: the number of incoming transitions
                            into the converged state.
        """
        self.expected_count = expected_count

    def mark_complete(self, branch: str) -> None:
        """
        File: join_strategies/all_join.py
        Class: AllJoinStrategy
        Method: mark_complete

        No internal per-branch state needed; only buffer length matters.
        """
        pass

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: join_strategies/all_join.py
        Class: AllJoinStrategy
        Method: is_satisfied

        Returns True when the buffer has at least as many entries
        as the configured in‑degree.
        """
        return len(buffer) >= self.expected_count

    def reset(self) -> None:
        """
        File: join_strategies/all_join.py
        Class: AllJoinStrategy
        Method: reset

        No internal state to reset beyond clearing the buffer
        in StateManager.
        """
        pass
