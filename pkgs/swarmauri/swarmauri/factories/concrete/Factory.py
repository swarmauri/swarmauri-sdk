from typing import Any, Callable, Dict, Literal
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.utils._get_subclasses import get_classes_from_module


class Factory(FactoryBase):
    """
    Non-recursive factory extending FactoryBase.
    """

    type: Literal["Factory"] = "Factory"
    _resource_registry: Dict[str, Dict[str, Callable]] = {}

    def _register(self, resource: str) -> None:
        """
        Register a resource class under a specific resource.
        """
        if resource not in self._resource_registry:
            self._resource_registry[resource] = get_classes_from_module(resource)
        else:
            raise ValueError(f"Resource '{resource}' is already registered.")

    def create(self, resource: str, type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of the class associated with the given resource and type.
        """
        if resource not in self._resource_registry:
            self._register(resource)

        if type not in self._resource_registry[resource]:
            raise ValueError(
                f"Type '{type}' does not exist under resource '{resource}'."
            )

        cls = self._resource_registry[resource][type]
        return cls(*args, **kwargs)
