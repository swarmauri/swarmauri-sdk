from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IServiceRegistry(ABC):
    """
    Abstract base class for service registries.
    """

    @abstractmethod
    def register_service(self, name: str, details: dict[str, Any]) -> None:
        """
        Register a new service with the given name and details.
        """

    @abstractmethod
    def get_service(self, name: str) -> dict[str, Any] | None:
        """
        Retrieve a service by its name.
        """

    @abstractmethod
    def get_services_by_roles(self, roles: list[str]) -> list[str]:
        """
        Get services filtered by their roles.
        """

    @abstractmethod
    def unregister_service(self, name: str) -> None:
        """
        unregister the service with the given name.
        """

    @abstractmethod
    def update_service(self, name: str, details: dict[str, Any]) -> None:
        """
        Update the details of the service with the given name.
        """
