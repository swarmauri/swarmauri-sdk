# File: swarmauri/workflows/conditions/string_condition.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.conditions.base import Condition


class StringCondition(Condition):
    """
    File: string_condition.py
    Class: StringCondition
    Methods: __init__, evaluate

    Checks string properties: contains, startswith, endswith.
    """

    def __init__(self, node_name: str, operator: str, substring: str):
        """
        File: string_condition.py
        Class: StringCondition
        Method: __init__

        Args:
            node_name: name of the state whose output is tested
            operator: one of "contains","startswith","endswith"
            substring: string to test for
        """
        self.node_name = node_name
        self.operator = operator
        self.substring = substring

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: string_condition.py
        Class: StringCondition
        Method: evaluate

        Returns True if the operator test passes on the node’s output.
        """
        value = state.get(self.node_name, "")
        if not isinstance(value, str):
            return False

        if self.operator == "contains":
            return self.substring in value
        if self.operator == "startswith":
            return value.startswith(self.substring)
        if self.operator == "endswith":
            return value.endswith(self.substring)

        raise ValueError(f"Unsupported operator: {self.operator}")
