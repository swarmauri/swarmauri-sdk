from abc import ABC, abstractmethod
from typing import Any, List, Dict
from swarmauri.core.agents.ISwarmAgent import ISwarmAgent
from swarmauri.core.chains.ICallableChain import ICallableChain

class ISwarm(ABC):
    """
    Interface for a Swarm, representing a collective of agents capable of performing tasks, executing callable chains, and adaptable configurations.
    """

    @abstractmethod
    def add_agent(self, agent: ISwarmAgent) -> None:
        """
        Adds an agent to the swarm.

        Args:
            agent (ISwarmAgent): The agent to be added.
        """
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> bool:
        """
        Removes an agent from the swarm by ID.

        Args:
            agent_id (str): The unique identifier for the agent.
            
        Returns:
            bool: True if the agent was successfully removed; False otherwise.
        """
        pass

    @abstractmethod
    def execute_callable_chain(self, chain: ICallableChain, context: Dict[str, Any] = {}) -> Any:
        """
        Executes a callable chain within the swarm, optionally in a specific execution context.

        Args:
            chain (ICallableChain): The callable chain to be executed.
            context (Dict[str, Any]): Optional context and metadata for executing the chain.
        
        Returns:
            Any: The result of the chain execution.
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> ISwarmAgent:
        """
        Retrieves an agent by its ID from the swarm.

        Args:
            agent_id (str): The unique identifier for the agent.

        Returns:
            ISwarmAgent: The agent associated with the given id.
        """
        pass

    @abstractmethod
    def list_agents(self) -> List[ISwarmAgent]:
        """
        Lists all agents currently in the swarm.

        Returns:
            List[ISwarmAgent]: A list of agents in the swarm.
        """
        pass

    @abstractmethod
    def update_swarm_configuration(self, configuration: Dict[str, Any]) -> None:
        """
        Updates the swarm's configuration.

        Args:
            configuration (Dict[str, Any]): The new configuration settings for the swarm.
        """
        pass

    @abstractmethod
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Retrieves the current status and health information of the swarm, including the number of agents, active tasks, etc.

        Returns:
            Dict[str, Any]: The current status of the swarm.
        """
        pass