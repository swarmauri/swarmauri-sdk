from typing import Any, Callable, Literal, Optional
from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_core.ComponentBase import ResourceTypes
from swarmauri_core.factories.IFactory import IFactory
from pydantic import ConfigDict, Field


class FactoryBase(IFactory, ComponentBase):
    """
    Base factory class for registering and creating instances.
    """

    resource: Optional[str] = Field(default=ResourceTypes.FACTORY.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["FactoryBase"] = "FactoryBase"

    def register(self, type: str, resource_class: Callable) -> None:
        """
        Register a resource class under a specific resource and type.
        """
        raise NotImplementedError(
            "register method must be implemented in derived classes."
        )

    def create(self, type: str, *args: Any, **kwargs: Any) -> Any:
        """
        Create an instance of the class associated with the given resource and type.
        """
        raise NotImplementedError(
            "create method must be implemented in derived classes."
        )
