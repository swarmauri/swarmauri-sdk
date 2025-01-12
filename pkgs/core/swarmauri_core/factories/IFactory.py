from abc import ABC, abstractmethod
from typing import Any, Callable


class IFactory(ABC):
    """
    Interface defining core methods for factories.
    """

    @abstractmethod
    def create(self, type: str, *args: Any, **kwargs: Any) -> Any:
        """Create and return an instance."""
        pass

    @abstractmethod
    def register(self, type: str, resource_class: Callable) -> None:
        """Register a class with the factory."""
        pass

    @abstractmethod
    def get(self):
        """Return a list of registered agent types."""
        pass

    @abstractmethod
    def unregister(self, type: str) -> None:
        """Unregister a class from the factory."""
        pass
