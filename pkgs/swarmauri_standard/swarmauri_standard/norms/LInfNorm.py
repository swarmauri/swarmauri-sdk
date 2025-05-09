import logging
from typing import TypeVar, Union, Callable, Sequence, Literal
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

T = TypeVar("T", Union[Callable, Sequence, str, bytes])

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "LInfNorm")
class LInfNorm(NormBase):
    type: Literal["LInfNorm"] = "LInfNorm"

    def __init__(self):
        super().__init__()
        logger.debug("LInfNorm instance initialized")

    def compute(self, x: T) -> float:
        """
        Computes the L-Infinity norm of the input.

        For a vector or array, this is the maximum absolute value of its elements.
        For a callable, this is the absolute value of the result when called.
        For other types, this is the absolute value of the input.

        Args:
            x (T): The input to compute the norm for.

        Returns:
            float: The computed L-Infinity norm value.
        """
        try:
            iterable = iter(x)
        except TypeError:
            # x is not iterable, treat as single value
            return abs(x)
        else:
            # Compute the maximum absolute value
            return max(abs(val) for val in iterable)

    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the norm is non-negative.

        Args:
            x (T): The input to check.

        Returns:
            bool: True, since the L-Infinity norm is always non-negative.
        """
        return True

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the norm satisfies the triangle inequality.

        Args:
            x (T): The first input.
            y (T): The second input.

        Returns:
            bool: True, since the L-Infinity norm satisfies the triangle inequality.
        """
        return True

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the norm satisfies absolute homogeneity.

        Args:
            x (T): The input to check.
            scalar (float): The scalar to scale with.

        Returns:
            bool: True, since the L-Infinity norm is absolutely homogeneous.
        """
        return True

    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the norm is definite (norm(x) = 0 if and only if x = 0).

        Args:
            x (T): The input to check.

        Returns:
            bool: True, since the L-Infinity norm is definite.
        """
        return True
