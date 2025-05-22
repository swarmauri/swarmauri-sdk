# File: swarmauri/workflows/conditions/function_condition.py

from typing import Callable, Dict, Any
from swarmauri_workflow_statedriven.conditions.base import Condition


class FunctionCondition(Condition):
    """
    Wraps a simple Python callable as a workflow condition.
    """

    def __init__(self, fn: Callable[[Dict[str, Any]], bool]):
        """
        File: workflows/conditions/function_condition.py
        Class: FunctionCondition
        Method: __init__

        Args:
            fn: A callable that takes the workflow state dict and returns True/False.
        """
        self.fn = fn

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        File: workflows/conditions/function_condition.py
        Class: FunctionCondition
        Method: evaluate

        Invoke the wrapped function on the current workflow state.

        Args:
            state: Mapping of state names to their outputs.

        Returns:
            The boolean result of fn(state).
        """
        return self.fn(state)
