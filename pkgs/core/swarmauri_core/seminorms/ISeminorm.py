from abc import ABC, abstractmethod
from typing import TypeVar, Union
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, str, callable, Sequence[float], Sequence[Sequence[float]])

class ISeminorm(ABC):
    """
    Interface for seminorm structures. This class defines the core functionality 
    required for seminorm operations. A seminorm is a function that satisfies 
    the triangle inequality and positive scalability but does not necessarily 
    satisfy the condition that only the zero vector has a norm of zero.

    This interface provides a foundation for working with seminorms while 
    remaining agnostic to the underlying implementation.
    """

    @abstractmethod
    def compute(self, input: T) -> float:
        """
        Compute the seminorm of the given input.

        Args:
            input: T
                The input to compute the seminorm on. This can be a vector, matrix, 
                sequence, string, or callable.

        Returns:
            float: 
                The computed seminorm value.

        Raises:
            TypeError: If the input type is not supported.
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        The triangle inequality states that for any two vectors a and b:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        Args:
            a: T
                The first input.
            b: T
                The second input.

        Returns:
            bool: True if the triangle inequality holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check if scalar homogeneity holds for the given input and scalar.

        Scalar homogeneity states that for any vector a and scalar c >= 0:
        seminorm(c * a) = c * seminorm(a)

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool: True if scalar homogeneity holds, False otherwise.
        """
        pass