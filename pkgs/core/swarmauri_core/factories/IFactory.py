from abc import ABC, abstractmethod
from typing import Any


class IFactory(ABC):
    """
    Interface defining core methods for factories.
    """

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Create and return an instance."""
        pass

    @abstractmethod
    def register(self, resource: str, name: str) -> None:
        """Register a class with the factory."""
        pass
