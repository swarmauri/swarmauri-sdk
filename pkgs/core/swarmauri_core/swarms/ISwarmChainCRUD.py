from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISwarmChainCRUD(ABC):
    """
    Interface to provide CRUD operations for ICallableChain within swarms.
    """

    @abstractmethod
    def create_chain(self, chain_id: str, chain_definition: Dict[str, Any]) -> None:
        """
        Creates a callable chain with the provided definition.

        Parameters:
        - chain_id (str): A unique identifier for the callable chain.
        - chain_definition (Dict[str, Any]): The definition of the callable chain including steps and their configurations.
        """
        pass

    @abstractmethod
    def read_chain(self, chain_id: str) -> Dict[str, Any]:
        """
        Retrieves the definition of a callable chain by its identifier.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be retrieved.

        Returns:
        - Dict[str, Any]: The definition of the callable chain.
        """
        pass

    @abstractmethod
    def update_chain(self, chain_id: str, new_definition: Dict[str, Any]) -> None:
        """
        Updates an existing callable chain with a new definition.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be updated.
        - new_definition (Dict[str, Any]): The new definition of the callable chain including updated steps and configurations.
        """
        pass

    @abstractmethod
    def delete_chain(self, chain_id: str) -> None:
        """
        Removes a callable chain from the swarm.

        Parameters:
        - chain_id (str): The unique identifier of the callable chain to be removed.
        """
        pass

    @abstractmethod
    def list_chains(self) -> List[Dict[str, Any]]:
        """
        Lists all callable chains currently managed by the swarm.

        Returns:
        - List[Dict[str, Any]]: A list of callable chain definitions.
        """
        pass