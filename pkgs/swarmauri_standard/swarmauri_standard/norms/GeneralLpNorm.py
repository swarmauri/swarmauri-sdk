from typing import Union, Sequence, Callable, Optional, Literal
from swarmauri_base.norms.NormBase import NormBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """
    Implementation of the General Lp Norm for real-valued functions.

    This class provides the concrete implementation of the Lp norm, which is
    widely used in various mathematical and engineering applications. The norm
    is parameterized by p, where p must be greater than 1 and finite.

    Inherits From:
        NormBase: Base class for all norm implementations

    Attributes:
        p (float): The parameter of the Lp norm, must be > 1 and finite
        type (Literal["GeneralLpNorm"]): Type identifier for the component
    """

    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"

    def __init__(self, p: float):
        """
        Initialize the GeneralLpNorm instance.

        Args:
            p (float): The parameter for the Lp norm, must be > 1 and finite

        Raises:
            ValueError: If p is not greater than 1 or is not finite
        """
        if not (isinstance(p, float) and p > 1 and p != float("inf")):
            raise ValueError("p must be a finite float greater than 1")

        self.p = p
        super().__init__()

    def compute(self, x: Union[Sequence, Callable, str]) -> float:
        """
        Compute the Lp norm of the input.

        The Lp norm is defined as:

        For vector x = (x1, x2, ..., xn):
        ||x||_p = (|x1|^p + |x2|^p + ... + |xn|^p)^(1/p)

        For matrix X = [x1; x2; ...; xn]:
        ||X||_p = max(||x1||_p, ||x2||_p, ..., ||xn||_p)

        Args:
            x (Union[Sequence, Callable, str]): The input to compute the norm of.
                                                  Can be a vector, matrix, string,
                                                  or callable.

        Returns:
            float: The computed Lp norm value.

        Raises:
            ValueError: If the input type is not supported
        """
        if isinstance(x, Sequence):
            if isinstance(x[0], Sequence):  # Matrix case
                return max(self.compute(row) for row in x)
            else:  # Vector case
                return (sum(abs(xi) ** self.p for xi in x)) ** (1.0 / self.p)
        elif isinstance(x, (Callable, str)):
            # For callables or strings, try to compute the norm
            # This is a simplified approach - actual implementation
            # might need to be more sophisticated based on use case
            if callable(x):
                try:
                    return self.compute(x())
                except Exception as e:
                    logger.error(f"Failed to compute norm for callable: {e}")
                    raise
            else:
                logger.error("String input type is not supported for norm computation")
                raise ValueError("String input type is not supported")
        else:
            logger.error(f"Unsupported input type for norm computation: {type(x)}")
            raise ValueError(f"Unsupported input type: {type(x)}")

    def check_non_negativity(self, x: Union[Sequence, Callable, str]) -> None:
        """
        Verify the non-negativity property of the norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x (Union[Sequence, Callable, str]): The input to verify non-negativity for.

        Raises:
            AssertionError: If the non-negativity property is not satisfied
        """
        norm = self.compute(x)
        if norm < 0:
            logger.error("Non-negativity violation: Norm is negative")
            raise AssertionError("Norm cannot be negative")

    def check_triangle_inequality(
        self, x: Union[Sequence, Callable, str], y: Union[Sequence, Callable, str]
    ) -> None:
        """
        Verify the triangle inequality property of the norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x (Union[Sequence, Callable, str]): The first input vector.
            y (Union[Sequence, Callable, str]): The second input vector.

        Raises:
            AssertionError: If the triangle inequality is not satisfied
        """
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        combined = (
            [xi + yi for xi, yi in zip(x, y)] if isinstance(x, Sequence) else x + y
        )
        norm_combined = self.compute(combined)

        if norm_combined > norm_x + norm_y:
            logger.error("Triangle inequality violation")
            raise AssertionError("Triangle inequality not satisfied")

    def check_absolute_homogeneity(
        self, x: Union[Sequence, Callable, str], alpha: float
    ) -> None:
        """
        Verify the absolute homogeneity property of the norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x (Union[Sequence, Callable, str]): The input vector.
            alpha (float): The scalar to scale the vector by.

        Raises:
            AssertionError: If absolute homogeneity is not satisfied
        """
        norm_x = self.compute(x)
        scaled = [alpha * xi for xi in x] if isinstance(x, Sequence) else alpha * x
        norm_scaled = self.compute(scaled)

        if not (abs(norm_scaled - abs(alpha) * norm_x) < 1e-9):
            logger.error("Absolute homogeneity violation")
            raise AssertionError("Absolute homogeneity not satisfied")

    def check_definiteness(self, x: Union[Sequence, Callable, str]) -> None:
        """
        Verify the definiteness property of the norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x (Union[Sequence, Callable, str]): The input to verify definiteness for.

        Raises:
            AssertionError: If definiteness property is not satisfied
        """
        norm = self.compute(x)
        if norm == 0:
            # Check if x is the zero vector
            if not (isinstance(x, Sequence) and all(xi == 0 for xi in x)):
                logger.error("Definiteness violation: Non-zero vector has zero norm")
                raise AssertionError("Non-zero vector has zero norm")
        else:
            if isinstance(x, Sequence) and all(xi == 0 for xi in x):
                logger.error(
                    "Definiteness violation: Zero vector does not have zero norm"
                )
                raise AssertionError("Zero vector does not have zero norm")
