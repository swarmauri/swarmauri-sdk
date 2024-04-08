from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from ...agents.ISwarmAgent import ISwarmAgent

class IAgentRegistration(ABC):
    """
    Interface for registering agents with the swarm, designed to support CRUD operations on ISwarmAgent instances.
    """

    @abstractmethod
    def register_agent(self, agent: ISwarmAgent) -> bool:
        """
        Register a new agent with the swarm.

        Parameters:
            agent (ISwarmAgent): An instance of ISwarmAgent representing the agent to register.

        Returns:
            bool: True if the registration succeeded; False otherwise.
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, updated_agent: ISwarmAgent) -> bool:
        """
        Update the details of an existing agent. This could include changing the agent's configuration,
        task assignment, or any other mutable attribute.

        Parameters:
            agent_id (str): The unique identifier for the agent.
            updated_agent (ISwarmAgent): An updated ISwarmAgent instance to replace the existing one.

        Returns:
            bool: True if the update was successful; False otherwise.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm based on its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent to be removed.

        Returns:
            bool: True if the removal was successful; False otherwise.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[ISwarmAgent]:
        """
        Retrieve an agent's instance from its unique identifier.

        Parameters:
            agent_id (str): The unique identifier for the agent of interest.

        Returns:
            Optional[ISwarmAgent]: The ISwarmAgent instance if found; None otherwise.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[ISwarmAgent]:
        """
        List all registered agents.

        Returns:
            List[ISwarmAgent]: A list containing instances of all registered ISwarmAgents.
        """
        pass