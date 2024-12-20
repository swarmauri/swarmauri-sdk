import logging
from typing import Any, Callable, Dict, Literal
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.utils._get_subclasses import get_classes_from_module


class AgentFactory(FactoryBase):
    """
    Class-specific factory for managing resources and types.
    """

    type: Literal["AgentFactory"] = "AgentFactory"
    _registry: Dict[str, Callable] = get_classes_from_module("Agent")

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
        logging.info(self._registry)
        if type not in self._registry:
            raise ValueError(f"Type '{type}' is not registered.")

        cls = self._registry[type]
        return cls(*args, **kwargs)

    def get(self):
        """
        Return a list of registered agent types.
        """
        return list(self._registry.keys())

    def unregister(self, type: str) -> None:
        """
        Unregister a resource class with a specific type.
        """
        if type not in self._registry:
            raise ValueError(f"Type '{type}' is not registered.")
        del self._registry[type]
