from abc import ABC, abstractmethod
from typing import Any, Sequence, List


class IMutator(ABC):
    """Interface for generic data mutation operations."""

    @abstractmethod
    def mutate(self, item: Any) -> Any:
        """Mutate a single item and return the result."""
        pass

    @abstractmethod
    def mutates(self, items: Sequence[Any]) -> List[Any]:
        """Mutate multiple items and return the results."""
        pass
