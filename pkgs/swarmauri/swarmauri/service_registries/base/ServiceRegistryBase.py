import logging
from typing import Callable, Dict, Any, Literal, Optional

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.service_registries.IServiceRegistry import IServiceRegistry


class ServiceRegistryBase(IServiceRegistry, ComponentBase):
    """
    Concrete implementation of the IServiceRegistry abstract base class.
    """

    services: Dict[str, Any] = {}
    type: Literal["ServiceRegistryBase"] = "ServiceRegistryBase"
    resource: Optional[str] = Field(
        default=ResourceTypes.SERVICE_REGISTRY.value, frozen=True
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def register_service(self, service: Callable, name: str) -> None:
        """
        Register a new service with the given name and details.
        """
        logging.info(f"Registering service {type(service)}.")
        self.services[name] = service

    def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a service by its name.
        """
        return self.services.get(name)

    def get_services(self) -> Dict[str, Any]:
        """Retrieve all service"""
        return list(self.services.values())

    def unregister_service(self, name: str) -> None:
        """
        unregister the service with the given name.
        """
        if name in self.services:
            del self.services[name]
            print(f"Service {name} unregistered.")
        else:
            raise ValueError(f"Service {name} not found.")

    def update_service(self, name: str, **kwargs) -> None:
        """
        Update the details of the service with the given name.
        """
        if name in self.services:
            for key, value in kwargs.items():
                if hasattr(self.services[name], key):
                    self.services[name].__setattr__(key, value)
            print(f"Service {name} updated with new details: {self.services[name]}")
        else:
            raise ValueError(f"Service {name} not found.")
