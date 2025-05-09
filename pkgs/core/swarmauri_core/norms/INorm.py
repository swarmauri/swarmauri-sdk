from abc import ABC, abstractmethod
from typing import Union, Sequence, Callable
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class INorm(ABC):
    """
    Interface for norm computations on vector spaces. This interface defines
    the contract for norm behavior, enforcing point-separating distance logic.
    Implementations must satisfy the properties of a norm:
    - Non-negativity
    - Absolute homogeneity
    - Triangle inequality
    - Definiteness
    
    All implementations must provide implementations for:
    - compute(): Computes the norm of the input
    - check_*(): Verification methods for norm properties
    """
    
    @abstractmethod
    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the norm of the input.

        Args:
            x: The input to compute the norm of. Can be a vector, matrix, sequence,
                string, or callable.

        Returns:
            float: The computed norm value.

        Raises:
            ValueError: If the input type is not supported.
            TypeError: If the input cannot be processed.
        """
        pass
    
    @abstractmethod
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the non-negativity property of the norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify non-negativity for.

        Raises:
            AssertionError: If the non-negativity property is not satisfied.
        """
        pass
    
    @abstractmethod
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                  y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the triangle inequality property of the norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: The first input vector.
            y: The second input vector.

        Raises:
            AssertionError: If the triangle inequality property is not satisfied.
        """
        pass
    
    @abstractmethod
    def check_absolute_homogeneity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                 alpha: float) -> None:
        """
        Verify the absolute homogeneity property of the norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: The input vector.
            alpha: The scalar to scale the vector by.

        Raises:
            AssertionError: If the absolute homogeneity property is not satisfied.
        """
        pass
    
    @abstractmethod
    def check_definiteness(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the definiteness property of the norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify definiteness for.

        Raises:
            AssertionError: If the definiteness property is not satisfied.
        """
        pass