from typing import Any, Dict, Type
from swarmauri.factories.base.FactoryBase import FactoryBase, T


class Factory(FactoryBase[T]):
    """
    Non-recursive factory extending FactoryBase.
    """
    def __init__(self) -> None:
        # Make _resource_registry an instance-level variable.
        self._resource_registry: Dict[str, Dict[str, Type[T]]] = {}

    def register(self, resource: str, type: str, resource_class: Type[T]) -> None:
        """
        Register a resource class under a specific resource and type.
        """
        if resource not in self._resource_registry:
            self._resource_registry[resource] = {}

        if type in self._resource_registry[resource]:
            raise ValueError(
                f"Type '{type}' is already registered under resource '{resource}'."
            )

        self._resource_registry[resource][type] = resource_class

    def create(self, resource: str, type: str, *args: Any, **kwargs: Any) -> T:
        """
        Create an instance of the class associated with the given resource and type.
        """
        if resource not in self._resource_registry:
            raise ValueError(f"Resource '{resource}' is not registered.")

        if type not in self._resource_registry[resource]:
            raise ValueError(
                f"Type '{type}' is not registered under resource '{resource}'."
            )

        cls = self._resource_registry[resource][type]
        return cls(*args, **kwargs)
