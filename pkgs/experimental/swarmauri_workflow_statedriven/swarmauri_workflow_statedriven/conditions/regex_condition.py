# File: swarmauri/workflows/conditions/regex_condition.py

import re
from typing import Any, Dict
from swarmauri_workflow_statedriven.conditions.base import Condition


class RegexCondition(Condition):
    """
    File: regex_condition.py
    Class: RegexCondition

    A Condition that applies a regular expression against the output
    of a specified state and fires if the pattern is found.
    """

    def __init__(self, node_name: str, pattern: str):
        """
        File: regex_condition.py
        Class: RegexCondition
        Method: __init__

        Args:
            node_name: the name of the state whose output will be tested
            pattern: the regular expression pattern to search for
        """
        self.node_name = node_name
        self.regex = re.compile(pattern)

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: regex_condition.py
        Class: RegexCondition
        Method: evaluate

        Check if the compiled regex matches the output of `node_name` in the workflow state.

        Args:
            state: mapping of state names to their outputs

        Returns:
            True if the regex finds a match in the node's output; False otherwise.
        """
        output = state.get(self.node_name)
        if not isinstance(output, str):
            return False
        return bool(self.regex.search(output))
