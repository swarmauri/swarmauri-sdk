from typing import Any, Callable, Dict, Literal
from swarmauri_base.factories.FactoryBase import FactoryBase
from swarmauri.utils._get_subclasses import get_classes_from_module


class Factory(FactoryBase):
    """
    Non-recursive factory extending FactoryBase.
    """

    type: Literal["Factory"] = "Factory"
    _resource_registry: Dict[str, Dict[str, Callable]] = {}

    def register(self, resource: str, type: str, resource_class: Callable) -> None:
        """
        Register a resource class under a specific resource.
        """
        if type in self._resource_registry.get(resource, {}):
            raise ValueError(
                f"Type '{type}' is already registered under resource '{resource}'."
            )

        if resource not in self._resource_registry:
            self._resource_registry[resource] = get_classes_from_module(resource)

        if type not in self._resource_registry[resource]:
            self._resource_registry[resource][type] = resource_class

    def create(self, resource: str, type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of the class associated with the given resource and type.
        """
        if resource not in self._resource_registry:
            self._resource_registry[resource] = get_classes_from_module(resource)

        if type not in self._resource_registry[resource]:
            raise ValueError(
                f"Type '{type}' is not registered under resource '{resource}'."
            )

        cls = self._resource_registry[resource][type]
        return cls(*args, **kwargs)
