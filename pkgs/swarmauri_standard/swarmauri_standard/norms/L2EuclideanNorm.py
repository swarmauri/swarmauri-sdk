from typing import Union, TypeVar
import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.norms.INorm import INorm

T = TypeVar("T", Union["IVector", "IMatrix", str, bytes, Sequence, Callable])

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "L2EuclideanNorm")
class L2EuclideanNorm(NormBase):
    """
    Concrete implementation of the NormBase class for computing the L2 Euclidean norm.

    The L2 Euclidean norm is defined as the square root of the sum of the squares of
    the vector components. This class provides the implementation for computing this norm
    and checking its properties.

    Inherits From:
        NormBase: Base class providing template logic for norm computations
        INorm: Interface for norm computations on vector spaces
        ComponentBase: Base class for all components in the system

    Provides:
        Implementation of the compute method for L2 norm calculation
        Implementations for checking norm properties like non-negativity,
        triangle inequality, absolute homogeneity, and definiteness
    """

    def __init__(self):
        """
        Initializes the L2EuclideanNorm instance.
        """
        super().__init__()
        logger.debug("L2EuclideanNorm instance initialized")

    def compute(self, x: T) -> float:
        """
        Computes the L2 Euclidean norm of the given input.

        Args:
            x: T
                The input vector to compute the norm for. Must support element-wise
                squaring and summation operations.

        Returns:
            float:
                The computed L2 norm value

        Raises:
            ValueError: If the input vector is empty or contains invalid values
        """
        logger.debug("Starting L2 norm computation")

        try:
            # Convert input to numpy array if not already
            if not isinstance(x, np.ndarray):
                x = np.asarray(x)

            if x.size == 0:
                raise ValueError("Input vector cannot be empty")

            # Square each element
            squared = np.square(x)

            # Sum the squares
            sum_of_squares = np.sum(squared)

            # Compute square root
            norm = np.sqrt(sum_of_squares)

            logger.debug(f"L2 norm computed successfully: {norm}")
            return float(norm)

        except Exception as e:
            logger.error(f"Error computing L2 norm: {str(e)}")
            raise ValueError(f"Failed to compute L2 norm: {str(e)}")

    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the computed norm satisfies non-negativity.

        Args:
            x: T
                The input vector to check

        Returns:
            bool:
                True if the norm is non-negative, False otherwise
        """
        logger.debug("Checking non-negativity of L2 norm")
        norm = self.compute(x)
        return norm >= 0.0

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the computed norm satisfies the triangle inequality.

        Args:
            x: T
                The first input vector
            y: T
                The second input vector

        Returns:
            bool:
                True if ||x + y|| <= ||x|| + ||y||, False otherwise
        """
        logger.debug("Checking triangle inequality for L2 norm")

        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_x_plus_y = self.compute(x + y)

        return norm_x_plus_y <= (norm_x + norm_y)

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the computed norm satisfies absolute homogeneity.

        Args:
            x: T
                The input vector
            scalar: float
                The scalar to scale with

        Returns:
            bool:
                True if ||c * x|| = |c| * ||x||, False otherwise
        """
        logger.debug("Checking absolute homogeneity for L2 norm")

        scaled_x = x * scalar
        norm_scaled = self.compute(scaled_x)
        norm_x = self.compute(x)

        return np.isclose(norm_scaled, abs(scalar) * norm_x)

    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the computed norm is definite (norm(x) = 0 if and only if x = 0).

        Args:
            x: T
                The input vector

        Returns:
            bool:
                True if norm(x) = 0 implies x = 0, False otherwise
        """
        logger.debug("Checking definiteness of L2 norm")
        norm = self.compute(x)
        return norm == 0.0 if x.size == 0 or np.all(x == 0) else norm > 0.0
