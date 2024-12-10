from typing import Any, Dict, Literal, Type
from swarmauri.factories.base.FactoryBase import FactoryBase, T


class AgentFactory(FactoryBase[T]):
    """
    Class-specific factory for managing resources and types.
    """
    type: Literal['AgentFactory'] = 'AgentFactory'
    _registry: Dict[str, Type[T]] = {}

    def register(self, type: str, resource_class: Type[T]) -> None:
        """
        Register a resource class with a specific type.
        """
        if type in self._registry:
            raise ValueError(f"Type '{type}' is already registered.")
        self._registry[type] = resource_class

    def create(self, type: str, *args: Any, **kwargs: Any) -> T:
        """
        Create an instance of the class associated with the given type name.
        """
        if type not in self._registry:
            raise ValueError(f"Type '{type}' is not registered.")

        cls = self._registry[type]
        return cls(*args, **kwargs)
