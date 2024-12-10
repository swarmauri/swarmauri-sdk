from typing import Any, Type
from swarmauri_core.factories.IFactory import IFactory, T


class FactoryBase(IFactory[T]):
    """
    Base factory class for registering and creating instances.
    """

    def register(self, resource: str, type: str, resource_class: Type[T]) -> None:
        """
        Register a resource class under a specific resource and type.
        """
        raise NotImplementedError("register method must be implemented in derived classes.")

    def create(self, resource: str, type: str, *args: Any, **kwargs: Any) -> T:
        """
        Create an instance of the class associated with the given resource and type.
        """
        raise NotImplementedError("create method must be implemented in derived classes.")