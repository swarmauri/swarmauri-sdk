from typing import Dict, Any, List, Literal, Optional

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

    def register_service(self, name: str, details: Dict[str, Any]) -> None:
        """
        Register a new service with the given name and details.
        """
        self.services[name] = details

    def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a service by its name.
        """
        return self.services.get(name)

    def get_services_by_roles(self, roles: List[str]) -> List[str]:
        """
        Get services filtered by their roles.
        """
        return [
            name
            for name, details in self.services.items()
            if details.get("role") in roles
        ]

    def unregister_service(self, name: str) -> None:
        """
        unregister the service with the given name.
        """
        if name in self.services:
            del self.services[name]
            print(f"Service {name} unregistered.")
        else:
            raise ValueError(f"Service {name} not found.")

    def update_service(self, name: str, details: Dict[str, Any]) -> None:
        """
        Update the details of the service with the given name.
        """
        if name in self.services:
            self.services[name].update(details)
            print(f"Service {name} updated with new details: {details}")
        else:
            raise ValueError(f"Service {name} not found.")
