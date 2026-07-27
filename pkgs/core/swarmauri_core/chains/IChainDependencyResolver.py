from abc import ABC, abstractmethod
from typing import List, Optional

from swarmauri_core.chains.IChainStep import IChainStep


class IChainDependencyResolver(ABC):
    @abstractmethod
    def build_dependencies(self) -> list[IChainStep]:
        """
        Builds the dependencies for a particular sequence in the matrix.

        Args:
            matrix (List[List[str]]): The prompt matrix.
            sequence_index (int): The index of the sequence to build
            dependencies for.

        Returns:
            Tuple containing indegrees and graph dicts.
        """

    @abstractmethod
    def resolve_dependencies(
        self, matrix: list[list[str | None]], sequence_index: int
    ) -> list[int]:
        """
        Resolves the execution order based on the provided dependencies.

        Args:
            indegrees (Dict[int, int]): The indegrees of each node.
            graph (Dict[int, List[int]]): The graph representing dependencies.

        Returns:
            List[int]: The resolved execution order.
        """
