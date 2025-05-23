# File: swarmauri/workflows/merge_strategies/list_merge.py

from typing import Any, List
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class ListMergeStrategy(MergeStrategy):
    """
    File: merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge

    Returns the buffered inputs exactly as a list, preserving order and identity.
    """

    def merge(self, inputs: List[Any]) -> Any:
        """
        File: merge_strategies/list_merge.py
        Class: ListMergeStrategy
        Method: merge

        Args:
            inputs: List of values buffered from incoming branches.

        Returns:
            The same list instance, allowing batch processing of the inputs.
        """
        return inputs
