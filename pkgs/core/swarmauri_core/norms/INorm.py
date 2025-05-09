from abc import ABC, abstractmethod
from typing import TypeVar, Union
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, str, bytes, Sequence, Callable)

class INorm(ABC):
    """
    Interface for norm computations on vector spaces. This class defines the 
    contract for computing norms and verifying norm properties such as 
    non-negativity, triangle inequality, and absolute homogeneity.
    """
    
    def __init__(self):
        """
        Initializes the INorm instance.
        """
        logger.debug("INorm instance initialized")

    @abstractmethod
    def compute(self, x: T) -> float:
        """
        Computes the norm of the given input.

        Args:
            x: T
                - For IVector: Compute the vector norm
                - For IMatrix: Compute the matrix norm
                - For str/bytes: Compute the string length
                - For Sequence: Compute the sequence length
                - For Callable: Compute based on the function's output

        Returns:
            float:
                The computed norm value

        Raises:
            ValueError: If the input type is not supported
        """
        pass

    @abstractmethod
    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the norm satisfies non-negativity.

        Args:
            x: T
                The input to check

        Returns:
            bool:
                True if norm(x) >= 0, False otherwise
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the norm satisfies the triangle inequality.

        Args:
            x: T
                The first input vector/matrix
            y: T
                The second input vector/matrix

        Returns:
            bool:
                True if ||x + y|| <= ||x|| + ||y||, False otherwise
        """
        pass

    @abstractmethod
    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the norm satisfies absolute homogeneity.

        Args:
            x: T
                The input to check
            scalar: float
                The scalar to scale with

        Returns:
            bool:
                True if ||c * x|| = |c| * ||x||, False otherwise
        """
        pass

    @abstractmethod
    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the norm is definite (norm(x) = 0 if and only if x = 0).

        Args:
            x: T
                The input to check

        Returns:
            bool:
                True if norm(x) = 0 implies x = 0, False otherwise
        """
        pass