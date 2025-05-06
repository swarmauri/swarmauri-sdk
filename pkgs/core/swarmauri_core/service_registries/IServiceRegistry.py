from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IServiceRegistry(ABC):
    """
    Abstract base class for service registries.
    """

    @abstractmethod
    def register_service(self, name: str, details: Dict[str, Any]) -> None:
        """
        Register a new service with the given name and details.
        """
        pass

    @abstractmethod
    def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a service by its name.
        """
        pass

    @abstractmethod
    def get_services_by_roles(self, roles: List[str]) -> List[str]:
        """
        Get services filtered by their roles.
        """
        pass

    @abstractmethod
    def unregister_service(self, name: str) -> None:
        """
        unregister the service with the given name.
        """
        pass

    @abstractmethod
    def update_service(self, name: str, details: Dict[str, Any]) -> None:
        """
        Update the details of the service with the given name.
        """
        pass
