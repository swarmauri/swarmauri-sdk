from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.service_registries.IServiceRegistry import IServiceRegistry

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class ServiceRegistryBase(IServiceRegistry, ComponentBase):
    """
    Concrete implementation of the IServiceRegistry abstract base class.
    """

    services: dict[str, Any] = {}
    type: Literal["ServiceRegistryBase"] = "ServiceRegistryBase"
    resource: str | None = Field(
        default=ResourceTypes.SERVICE_REGISTRY.value, frozen=True
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    def register_service(self, name: str, details: dict[str, Any]) -> None:
        """
        Register a new service with the given name and details.
        """
        self.services[name] = details

    def get_service(self, name: str) -> dict[str, Any] | None:
        """
        Retrieve a service by its name.
        """
        return self.services.get(name)

    def get_services_by_roles(self, roles: list[str]) -> list[str]:
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

    def update_service(self, name: str, details: dict[str, Any]) -> None:
        """
        Update the details of the service with the given name.
        """
        if name in self.services:
            self.services[name].update(details)
            print(f"Service {name} updated with new details: {details}")
        else:
            raise ValueError(f"Service {name} not found.")

    def get_services(self) -> list[str]:
        """
        Get all services.
        """
        return list(self.services.keys())
