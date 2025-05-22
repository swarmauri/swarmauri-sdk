# File: swarmauri/workflows/merge_strategies/custom_merge.py

from typing import Any, Callable, List
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class CustomMergeStrategy(MergeStrategy):
    """
    File: merge_strategies/custom_merge.py
    Class: CustomMergeStrategy

    Wraps a user‑provided function to merge buffered inputs.
    """

    def __init__(self, fn: Callable[[List[Any]], Any]):
        """
        File: merge_strategies/custom_merge.py
        Class: CustomMergeStrategy
        Method: __init__

        Args:
            fn: a callable that takes a list of inputs and returns a merged value.
        """
        self.fn = fn

    def merge(self, inputs: List[Any]) -> Any:
        """
        File: merge_strategies/custom_merge.py
        Class: CustomMergeStrategy
        Method: merge

        Invoke the user‑provided function on the buffered inputs.

        Args:
            inputs: list of values buffered for the converged state.

        Returns:
            The result of applying fn to inputs.
        """
        return self.fn(inputs)
