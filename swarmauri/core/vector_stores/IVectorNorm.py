# core/vectors/IVectorNorm.py

from abc import ABC, abstractmethod
from typing import List, Union

class IVectorNorm(ABC):
    """
    Interface for calculating vector norms.
    Supports L1 norm, L2 norm, and Max norm calculations.
    """

    @abstractmethod
    def l1_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L1 norm (Manhattan norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L1 norm.

        Returns:
        - float: The L1 norm of the vector.
        """
        pass

    @abstractmethod
    def l2_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the L2 norm (Euclidean norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the L2 norm.

        Returns:
        - float: The L2 norm of the vector.
        """
        pass

    @abstractmethod
    def max_norm(self, vector: List[Union[int, float]]) -> float:
        """
        Calculate the Max norm (infinity norm) of a vector.

        Parameters:
        - vector (List[Union[int, float]]): The vector for which to calculate the Max norm.

        Returns:
        - float: The Max norm of the vector.
        """
        pass