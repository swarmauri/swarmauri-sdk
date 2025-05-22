# File: swarmauri/workflows/merge_strategies/base.py

from abc import ABC, abstractmethod
from typing import Any, List


class MergeStrategy(ABC):
    """
    Base class for merge strategies combining multiple buffered inputs
    into a single value for a converged node.
    """

    @abstractmethod
    def merge(self, inputs: List[Any]) -> Any:
        """
        Merge a list of branch outputs into one input for the converged state.

        Args:
            inputs: List of values buffered from incoming branches.
        Returns:
            A single merged output value.
        """
        ...
