from abc import ABC, abstractmethod
from typing import List, Any

class IVectorSpan(ABC):
    """
    Interface for determining if a vector is within the span of a set of vectors.
    """

    @abstractmethod
    def in_span(self, vector: Any, basis_vectors: List[Any]) -> bool:
        """
        Checks if the given vector is in the span of the provided basis vectors.

        Parameters:
        - vector (Any): The vector to check.
        - basis_vectors (List[Any]): A list of vectors that might span the vector.

        Returns:
        - bool: True if the vector is in the span of the basis_vectors, False otherwise.
        """
        pass