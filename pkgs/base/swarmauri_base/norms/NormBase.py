import logging
from abc import ABC, abstractmethod
from typing import Union, Any, Sequence, Tuple, Optional, Callable
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)

class INorm(ABC):
    """
    Interface for vector norms.

    This abstract base class defines the interface for various vector norms.
    It enforces the contract that any implementing class must provide a compute method
    and can optionally provide specific implementations for different types of checks.
    The checks are designed to verify the mathematical properties of a norm.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the norm of the input.

        Args:
            x: The input to compute the norm for. Can be a vector, matrix, sequence, string, or callable.

        Returns:
            float: The computed norm value.
        """
        raise NotImplementedError("compute method must be implemented by subclass.")

    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check if the norm is non-negative.

        Args:
            x: The input to check the norm for.

        Raises:
            AssertionError: If the norm is negative.
        """
        logger.debug(f"Checking non-negativity for input: {x}")
        norm = self.compute(x)
        if norm < 0:
            raise AssertionError(f"Norm value {norm} is negative. Non-negativity violated.")
        logger.debug("Non-negativity check passed.")

    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check the triangle inequality: ||x + y|| <= ||x|| + ||y||.

        Args:
            x: First input vector.
            y: Second input vector.

        Raises:
            AssertionError: If the triangle inequality is violated.
        """
        logger.debug(f"Checking triangle inequality for inputs: {x}, {y}")
        norm_x_plus_y = self.compute(x + y)
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        if norm_x_plus_y > norm_x + norm_y:
            raise AssertionError(f"Triangle inequality violated: {norm_x_plus_y} > {norm_x} + {norm_y}")
        logger.debug("Triangle inequality check passed.")

    def check_absolute_homogeneity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                     a: float) -> None:
        """
        Check absolute homogeneity: ||a * x|| = |a| * ||x||.

        Args:
            x: Input vector.
            a: Scalar multiplier.

        Raises:
            AssertionError: If absolute homogeneity is violated.
        """
        logger.debug(f"Checking absolute homogeneity for input: {x}, scalar: {a}")
        norm_scaled = self.compute(a * x)
        norm_original = self.compute(x)
        expected = abs(a) * norm_original
        if not (norm_scaled - expected) < 1e-9:  # Using approximate equality for floats
            raise AssertionError(f"Absolute homogeneity violated: {norm_scaled} != {expected}")
        logger.debug("Absolute homogeneity check passed.")

    def check_definiteness(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check definiteness: ||x|| = 0 if and only if x is the zero vector.

        Args:
            x: Input vector to check.

        Raises:
            AssertionError: If definiteness is violated.
        """
        logger.debug(f"Checking definiteness for input: {x}")
        norm = self.compute(x)
        if norm == 0:
            logger.info("Norm is zero, implying x is the zero vector")
        else:
            logger.info("Norm is non-zero, x is non-zero")
        logger.debug("Definiteness check completed.")

    def __str__(self) -> str:
        return f"Norm type: {self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"Norm({self.__class__.__name__})"