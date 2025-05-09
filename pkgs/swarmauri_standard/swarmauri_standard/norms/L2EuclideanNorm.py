import logging
from typing import Union, Sequence, Optional
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class L2EuclideanNorm(NormBase):
    """
    Concrete implementation of the NormBase class for computing the L2 Euclidean norm.

    The L2 norm, also known as the Euclidean norm, is the square root of the sum of
    the squares of the vector components. This implementation provides the core
    functionality for computing the norm and validating its properties.

    Inherits From:
        NormBase: Base class for norm computations

    Attributes:
        type: Type identifier for the norm implementation
        resource: Type of resource this component represents
    """

    type: str = "L2EuclideanNorm"
    resource: Optional[str] = "norm"

    def compute(self, x: Union[Sequence, str, Callable]) -> float:
        """
        Compute the L2 Euclidean norm of the input vector.

        The computation follows the formula:
        ||x|| = sqrt(x1^2 + x2^2 + ... + xn^2)

        Args:
            x: Input vector to compute the norm of. Can be a sequence of numbers,
                a string representation, or a callable that produces a vector.

        Returns:
            float: The computed L2 norm value.

        Raises:
            ValueError: If the input cannot be processed into a numeric vector
        """
        try:
            # Convert input to a list of floats if it's a string or callable
            if isinstance(x, str):
                vector = [float(num) for num in x.strip().split()]
            elif callable(x):
                vector = list(x())
            else:
                vector = list(x)

            # Compute the sum of squares
            sum_squares = sum(num**2 for num in vector)

            # Return the square root of the sum
            return sum_squares**0.5

        except (TypeError, ValueError) as e:
            logger.error(f"Failed to compute L2 norm: {str(e)}")
            raise ValueError("Invalid input type for L2 norm computation")

    def check_non_negativity(self, x: Union[Sequence, str, Callable]) -> None:
        """
        Verify the non-negativity property of the L2 norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: Input vector to verify non-negativity for.

        Raises:
            AssertionError: If the non-negativity property is not satisfied
        """
        norm = self.compute(x)
        assert norm >= 0, "L2 norm is negative - non-negativity violated"
        logger.info("Non-negativity property verified for L2 norm")

    def check_triangle_inequality(
        self, x: Union[Sequence, str, Callable], y: Union[Sequence, str, Callable]
    ) -> None:
        """
        Verify the triangle inequality property of the L2 norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: First input vector
            y: Second input vector

        Raises:
            AssertionError: If the triangle inequality is not satisfied
        """
        x_norm = self.compute(x)
        y_norm = self.compute(y)
        sum_norms = x_norm + y_norm

        # Compute the norm of the sum
        combined = [a + b for a, b in zip(x, y)]
        sum_norm = self.compute(combined)

        assert sum_norm <= sum_norms, "Triangle inequality violated for L2 norm"
        logger.info("Triangle inequality property verified for L2 norm")

    def check_absolute_homogeneity(
        self, x: Union[Sequence, str, Callable], alpha: float
    ) -> None:
        """
        Verify the absolute homogeneity property of the L2 norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: Input vector to scale
            alpha: Scalar to use for scaling

        Raises:
            AssertionError: If absolute homogeneity is not satisfied
        """
        scaled = [alpha * num for num in x]
        scaled_norm = self.compute(scaled)
        original_norm = self.compute(x)

        assert abs(scaled_norm - abs(alpha) * original_norm) < 1e-9, (
            f"Absolute homogeneity violated for L2 norm: {scaled_norm} != {abs(alpha)}*{original_norm}"
        )
        logger.info("Absolute homogeneity property verified for L2 norm")

    def check_definiteness(self, x: Union[Sequence, str, Callable]) -> None:
        """
        Verify the definiteness property of the L2 norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: Input vector to verify definiteness for.

        Raises:
            AssertionError: If definiteness property is not satisfied
        """
        norm = self.compute(x)
        if norm == 0:
            assert all(num == 0 for num in x), (
                "Definiteness violated: Non-zero vector with zero norm"
            )
        else:
            assert norm > 0, "Definiteness violated: Zero vector with positive norm"
        logger.info("Definiteness property verified for L2 norm")
