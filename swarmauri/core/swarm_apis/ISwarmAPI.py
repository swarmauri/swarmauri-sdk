from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISwarmAPI(ABC):
    """
    Interface for managing the swarm's API endpoints.
    """
    
    @abstractmethod
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Lists all registered agents within the swarm.

        Returns:
        - List[Dict[str, Any]]: A list of dictionaries containing information about each agent.
        """
        pass

    @abstractmethod
    def get_swarm_capabilities(self) -> List[str]:
        """
        Retrieves a list of all unique capabilities supported by the swarm.

        Returns:
        - List[str]: A list of unique capabilities.
        """
        pass

    @abstractmethod
    def dispatch_request(self, request_data: Dict[str, Any]) -> Any:
        """
        Dispatches an incoming user request to one or more suitable agents based on their capabilities.

        Parameters:
        - request_data (Dict[str, Any]): Data related to the incoming request.

        Returns:
        - Any: Response from processing the request.
        """
        pass