from abc import ABC, abstractmethod
from typing import Callable, Any, Dict

class IAgentRouterCRUD(ABC):
    """
    Interface for managing API routes within a SwarmAgent.
    """
    
    @abstractmethod
    def create_route(self, path: str, method: str, handler: Callable[[Any], Any]) -> None:
        """
        Create a new route for the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method (e.g., 'GET', 'POST').
        - handler (Callable[[Any], Any]): The function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def read_route(self, path: str, method: str) -> Dict:
        """
        Retrieve information about a specific route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        
        Returns:
        - Dict: Information about the route, including path, method, and handler.
        """
        pass
    
    @abstractmethod
    def update_route(self, path: str, method: str, new_handler: Callable[[Any], Any]) -> None:
        """
        Update the handler function for an existing route.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        - new_handler (Callable[[Any], Any]): The new function that handles requests to this route.
        """
        pass
    
    @abstractmethod
    def delete_route(self, path: str, method: str) -> None:
        """
        Delete a specific route from the API.
        
        Parameters:
        - path (str): The URL path for the route.
        - method (str): The HTTP method.
        """
        pass