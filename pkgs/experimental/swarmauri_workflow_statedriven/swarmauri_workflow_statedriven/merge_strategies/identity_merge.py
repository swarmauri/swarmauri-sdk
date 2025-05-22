# File: swarmauri/workflows/merge_strategies/identity_merge.py

from typing import Any
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class IdentityMergeStrategy(MergeStrategy):
    """
    File: merge_strategies/identity_merge.py
    Class: IdentityMergeStrategy
    Method: merge

    A merge strategy that returns the inputs exactly as received,
    without any transformation. Useful when you want to pass through
    a single payload (scalar or list) unchanged.
    """

    def merge(self, inputs: Any) -> Any:
        """
        File: merge_strategies/identity_merge.py
        Class: IdentityMergeStrategy
        Method: merge

        Args:
            inputs: either a scalar or a list of values buffered
                    from incoming branches.

        Returns:
            The same `inputs` object, preserving identity.
        """
        return inputs
