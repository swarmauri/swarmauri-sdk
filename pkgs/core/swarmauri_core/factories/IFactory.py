from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

# Generic type variable for flexible factory implementations
T = TypeVar("T")


class IFactory(ABC, Generic[T]):
    """
    Interface defining core methods for factories.
    """

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> T:
        """Create and return an instance of type T."""
        pass

    @abstractmethod
    def register(self, resource: str, name: str, resource_class: Type[T]) -> None:
        """Register a class with the factory."""
        pass
