from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional
from swarmauri.chains.concrete.ChainStep import ChainStep


class IChainDependencyResolver(ABC):
    @abstractmethod
    def build_dependencies(self) -> List[ChainStep]:
        """
        Builds the dependencies for a particular sequence in the matrix.

        Args:
            matrix (List[List[str]]): The prompt matrix.
            sequence_index (int): The index of the sequence to build dependencies for.

        Returns:
            Tuple containing indegrees and graph dicts.
        """
        pass

    @abstractmethod
    def resolve_dependencies(
        self, matrix: List[List[Optional[str]]], sequence_index: int
    ) -> List[int]:
        """
        Resolves the execution order based on the provided dependencies.

        Args:
            indegrees (Dict[int, int]): The indegrees of each node.
            graph (Dict[int, List[int]]): The graph representing dependencies.

        Returns:
            List[int]: The resolved execution order.
        """
        pass
