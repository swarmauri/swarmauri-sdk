from abc import ABC, abstractmethod


class ICostGuardRail(ABC):
    """Interface for cost guard rails."""

    @abstractmethod
    def allow(self, cost: float) -> bool:
        """Return whether the given cost is permitted."""

    @abstractmethod
    def remaining_budget(self) -> float:
        """Return the remaining budget."""
