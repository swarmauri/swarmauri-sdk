# File: swarmauri/workflows/merge_strategies/concat_merge.py

from typing import Any, List
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class ConcatMergeStrategy(MergeStrategy):
    """
    File: merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge

    Concatenate all inputs into a single string.
    """

    def merge(self, inputs: List[Any]) -> Any:
        """
        Merge a list of branch outputs by concatenating them as strings.

        Args:
            inputs: List of values buffered from incoming branches.

        Returns:
            A single concatenated string.
        """
        return "".join(str(item) for item in inputs)
