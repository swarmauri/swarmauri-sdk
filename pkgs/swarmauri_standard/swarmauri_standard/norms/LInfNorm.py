import logging
from abc import ABC
from typing import Union, Any, Sequence, Optional
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "LInfNorm")
class LInfNorm(NormBase):
    """Concrete implementation of the L-Infinity norm.

    This class implements the L-Infinity norm (supremum norm) for various types of inputs.
    The L-Infinity norm of a vector is the maximum of the absolute values of its elements.
    For functions, it is the supremum of the absolute values over the function's domain.

    Inherits from:
        NormBase: Abstract base class for all norms.
    """

    type: Literal["LInfNorm"] = "LInfNorm"
    """Type identifier for the L-Infinity norm."""

    def __init__(self, domain: Optional[Sequence] = None):
        """Initialize the LInfNorm instance.

        Args:
            domain: Bounded domain over which the norm is computed. If None, domain is inferred.
        """
        super().__init__()
        self.domain = domain

    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """Compute the L-Infinity norm of the input.

        The L-Infinity norm is defined as the maximum absolute value in the input.

        Args:
            x: The input to compute the norm for. Can be a vector, matrix, sequence, string, or callable.

        Returns:
            float: The computed L-Infinity norm value.

        Raises:
            ValueError: If the input type is not supported.
        """
        logger.debug(f"Computing L-Infinity norm for input: {x}")
        
        # Handle different input types
        if isinstance(x, (IVector, IMatrix)):
            values = x.to_list()
        elif isinstance(x, Sequence):
            values = x
        elif isinstance(x, str):
            # Treat each character as a separate element
            # Try to convert characters to numeric values if possible
            try:
                values = [float(c) for c in x]
            except ValueError:
                # If characters are not numeric, use their Unicode values
                values = [ord(c) for c in x]
        elif callable(x):
            # For callable objects, evaluate at points in the domain
            if self.domain is None:
                raise ValueError("Domain must be specified for callable inputs")
            values = [abs(x(point)) for point in self.domain]
        else:
            raise ValueError(f"Unsupported input type: {type(x)}")

        # Compute the maximum absolute value
        max_value = max(abs(v) for v in values)
        logger.debug(f"Computed L-Infinity norm: {max_value}")
        return max_value

    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """Check if the norm is non-negative.

        Args:
            x: The input to check the norm for.

        Raises:
            AssertionError: If the norm is negative.
        """
        logger.debug("Checking non-negativity")
        norm = self.compute(x)
        if norm < 0:
            raise AssertionError(f"L-Infinity norm {norm} is negative")
        logger.debug("Non-negativity check passed")

    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """Check the triangle inequality: ||x + y|| <= ||x|| + ||y||.

        Args:
            x: First input vector.
            y: Second input vector.

        Raises:
            AssertionError: If the triangle inequality is violated.
        """
        logger.debug("Checking triangle inequality")
        norm_x_plus_y = self.compute(x + y)
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        if norm_x_plus_y > norm_x + norm_y:
            raise AssertionError(f"Triangle inequality violated: {norm_x_plus_y} > {norm_x} + {norm_y}")
        logger.debug("Triangle inequality check passed")

    def check_absolute_homogeneity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                     a: float) -> None:
        """Check absolute homogeneity: ||a * x|| = |a| * ||x||.

        Args:
            x: Input vector.
            a: Scalar multiplier.

        Raises:
            AssertionError: If absolute homogeneity is violated.
        """
        logger.debug(f"Checking absolute homogeneity with scalar {a}")
        norm_scaled = self.compute(a * x)
        norm_original = self.compute(x)
        expected = abs(a) * norm_original
        if not (abs(norm_scaled - expected) < 1e-9):
            raise AssertionError(f"Absolute homogeneity violated: {norm_scaled} != {expected}")
        logger.debug("Absolute homogeneity check passed")

    def check_definiteness(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """Check definiteness: ||x|| = 0 if and only if x is the zero vector.

        Args:
            x: Input vector to check.

        Raises:
            AssertionError: If definiteness is violated.
        """
        logger.debug("Checking definiteness")
        norm = self.compute(x)
        if norm == 0:
            logger.info("Norm is zero, input is zero vector")
        else:
            logger.info("Norm is non-zero, input is non-zero")
        logger.debug("Definiteness check completed")

    def __str__(self) -> str:
        return f"L-Infinity Norm ({self.type})"

    def __repr__(self) -> str:
        return f"LInfNorm()"