# File: swarmauri/workflows/conditions/state_condition.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.conditions.base import Condition


class StateValueCondition(Condition):
    """
    File: swarmauri/workflows/conditions/state_condition.py
    Class: StateValueCondition

    Compares a state's output against an expected value using the specified comparator.
    """

    def __init__(self, node_name: str, expected: Any, comparator: str = "eq"):
        """
        File: swarmauri/workflows/conditions/state_condition.py
        Class: StateValueCondition
        Method: __init__

        Args:
            node_name: the name of the state whose output will be tested
            expected: the value to compare against
            comparator: comparison operator; one of "eq", "ne", "gt", "lt", "ge", "le"
        """
        self.node_name = node_name
        self.expected = expected
        self.comparator = comparator

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: swarmauri/workflows/conditions/state_condition.py
        Class: StateValueCondition
        Method: evaluate

        Retrieve the stored output for `node_name` and compare it to `expected`.

        Args:
            state: mapping of state names to their outputs

        Returns:
            True if the comparison holds; False otherwise.
        """
        actual = state.get(self.node_name)
        if self.comparator == "eq":
            return actual == self.expected
        if self.comparator == "ne":
            return actual != self.expected
        if self.comparator == "gt":
            return actual > self.expected
        if self.comparator == "lt":
            return actual < self.expected
        if self.comparator == "ge":
            return actual >= self.expected
        if self.comparator == "le":
            return actual <= self.expected
        raise ValueError(f"Unsupported comparator: {self.comparator}")
