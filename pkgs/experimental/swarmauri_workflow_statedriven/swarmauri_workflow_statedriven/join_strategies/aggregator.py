# File: swarmauri/workflows/join_strategies/aggregator.py

from typing import Any, List
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy


class AggregatorStrategy(JoinStrategy):
    """
    File: join_strategies/aggregator.py
    Class: AggregatorStrategy

    Fires for every incoming branch and buffers inputs until consumed.
    """

    def __init__(self):
        """
        File: aggregator.py
        Class: AggregatorStrategy
        Method: __init__

        No initialization required beyond handling buffer via StateManager.
        """
        pass

    def mark_complete(self, branch: str) -> None:
        """
        File: aggregator.py
        Class: AggregatorStrategy
        Method: mark_complete

        No-op: buffering is handled by StateManager.
        """
        pass

    def is_satisfied(self, buffer: List[Any]) -> bool:
        """
        File: aggregator.py
        Class: AggregatorStrategy
        Method: is_satisfied

        Return True if there is at least one buffered input.
        """
        return len(buffer) > 0

    def aggregate(self, buffer: List[Any]) -> List[Any]:
        """
        File: aggregator.py
        Class: AggregatorStrategy
        Method: aggregate

        Return all buffered inputs as a list.
        """
        return buffer.copy()

    def reset(self) -> None:
        """
        File: aggregator.py
        Class: AggregatorStrategy
        Method: reset

        No internal state to reset for AggregatorStrategy.
        """
        pass
