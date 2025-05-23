# File: swarmauri/workflows/merge_strategies/flatten_merge.py

from typing import Any, List
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class FlattenMergeStrategy(MergeStrategy):
    def merge(self, inputs: List[Any]) -> Any:
        # this returns List[Scalar] even if inputs was [[a,b],[c]]
        flattened: List[Any] = []
        for item in inputs:
            if isinstance(item, list):
                flattened.extend(item)
            else:
                flattened.append(item)
        return flattened
