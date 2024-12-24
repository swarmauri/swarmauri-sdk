from typing import Any, Callable, Dict, Literal
from swarmauri_base.factories.FactoryBase import FactoryBase


class AgentFactory(FactoryBase):
    """
    Class-specific factory for managing resources and types.
    """

    type: Literal["AgentFactory"] = "AgentFactory"
    _registry: Dict[str, Callable] = {}

    def register(self, type: str, resource_class: Callable) -> None:
        """
        Register a resource class with a specific type.
        """
        if type in self._registry:
            raise ValueError(f"Type '{type}' is already registered.")
        self._registry[type] = resource_class

    def create(self, type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of the class associated with the given type name.
        """
        if type not in self._registry:
            raise ValueError(f"Type '{type}' is not registered.")

        cls = self._registry[type]
        return cls(*args, **kwargs)

    def get_agents(self):
        """
        Return a list of registered agent types.
        """
        return list(self._registry.keys())
