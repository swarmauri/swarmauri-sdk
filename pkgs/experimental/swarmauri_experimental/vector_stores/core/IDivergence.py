from abc import ABC, abstractmethod
from typing import List

class IDivergence(ABC):
    """
    Interface for calculating the divergence of a vector field.
    """

    @abstractmethod
    def calculate_divergence(self, vector_field: List[List[float]], point: List[float]) -> float:
        """
        Calculate the divergence of a vector field at a specific point.

        Parameters:
        - vector_field (List[List[float]]): A representation of the vector field as a list of vectors.
        - point (List[float]): The point at which the divergence is to be calculated.

        Returns:
        - float: The divergence value at the specified point.
        """
        pass