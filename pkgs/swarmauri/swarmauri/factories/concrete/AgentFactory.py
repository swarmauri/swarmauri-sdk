from typing import Any, Callable, Dict, Literal
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.utils._get_subclasses import get_class_from_module


class AgentFactory(FactoryBase):
    """
    Class-specific factory for managing resources and types.
    """

    type: Literal["AgentFactory"] = "AgentFactory"
    _registry: Dict[str, Callable] = {}

    def _register(self, type: str, resource: str = "Agent") -> None:
        """
        Register a resource class with a specific type.
        """
        if type in self._registry:
            raise ValueError(f"Type '{type}' is already registered.")
        resource_cls = get_class_from_module(resource, type)
        if resource_cls is not None:
            self._registry[type] = resource_cls
        else:
            raise ValueError(f"Type '{type}' is not found in resource '{resource}'.")

    def create(self, type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of the class associated with the given type name.
        """
        self._register(type)

        if type not in self._registry:
            raise ValueError(f"Type '{type}' is not found.")

        cls = self._registry[type]
        return cls(*args, **kwargs)

    def get_agents(self):
        """
        Return a list of registered agent types.
        """
        return list(self._registry.keys())
