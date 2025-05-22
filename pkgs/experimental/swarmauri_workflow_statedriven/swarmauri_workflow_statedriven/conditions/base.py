# File: swarmauri/workflows/conditions/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class Condition(ABC):
    """
    Base class for all transition and join conditions.
    """

    @abstractmethod
    def evaluate(self, state: Dict[str, Any]) -> bool:
        """
        Evaluate this condition against the current workflow state.

        Args:
            state: mapping of state names to their outputs.

        Returns:
            True if the condition is satisfied; False otherwise.
        """
        ...
