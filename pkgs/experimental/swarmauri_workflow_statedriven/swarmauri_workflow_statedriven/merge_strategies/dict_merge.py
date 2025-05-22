# File: swarmauri/workflows/merge_strategies/dict_merge.py

from typing import Any, List, Dict
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class DictMergeStrategy(MergeStrategy):
    """
    MergeStrategy that shallow‑merges a list of dicts into a single dict.
    Later dicts override earlier keys.
    """

    def merge(self, inputs: List[Any]) -> Any:
        """
        Merge a list of branch outputs by updating a result dict with each input.
        Only dict inputs are merged; others are ignored.

        Args:
            inputs: List of values buffered from incoming branches.

        Returns:
            A single dict containing the combined key‑value pairs.
        """
        result: Dict[Any, Any] = {}
        for item in inputs:
            if isinstance(item, dict):
                result.update(item)
        return result
