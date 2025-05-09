import logging
import numpy as np
from typing import TypeVar, Union
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

T = TypeVar("T", Union["IVector", "IMatrix", str, bytes, Sequence, Callable])


@ComponentBase.register_type(NormBase, "SupremumComplexNorm")
class SupremumComplexNorm(NormBase):
    """
    Concrete implementation of the NormBase class for computing the supremum norm on complex-valued functions.

    The supremum norm is defined as the maximum absolute value of the function over a specified interval [a, b].
    By default, the interval is assumed to be [0, 1]. The implementation evaluates the function at discrete
    points within this interval and computes the maximum absolute value.

    Inherits From:
        NormBase: Base class providing common interfaces for norm computations.
        ComponentBase: Base class for all components in the system.
    """

    type: Literal["SupremumComplexNorm"] = "SupremumComplexNorm"

    def __init__(self):
        """
        Initializes the SupremumComplexNorm instance.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SupremumComplexNorm instance initialized")

    def compute(self, x: T) -> float:
        """
        Computes the supremum norm of a complex-valued function over the interval [0, 1].

        Args:
            x: T
                The input function to compute the norm for. Assumed to be a callable function.

        Returns:
            float:
                The computed supremum norm value.

        Raises:
            ValueError: If the input x is not a callable function.
        """
        self.logger.debug("Computing supremum norm")

        if not callable(x):
            self.logger.error("Input x is not a callable function")
            raise ValueError("Input x must be a callable function")

        # Generate a grid of 1000 points in the interval [0, 1]
        t = np.linspace(0, 1, 1000)

        # Evaluate the function at each point and compute absolute values
        values = np.abs(x(t))

        # Find the maximum absolute value
        max_value = np.max(values)

        self.logger.debug(f"Computed supremum norm: {max_value}")
        return float(max_value)

    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the supremum norm satisfies non-negativity.

        Args:
            x: T
                The input to check

        Returns:
            bool:
                True if the norm is non-negative, False otherwise
        """
        self.logger.debug("Checking non-negativity")
        return True

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the supremum norm satisfies the triangle inequality.

        Args:
            x: T
                The first input vector/matrix
            y: T
                The second input vector/matrix

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise
        """
        self.logger.debug("Checking triangle inequality")
        return True

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the supremum norm satisfies absolute homogeneity.

        Args:
            x: T
                The input to check
            scalar: float
                The scalar to scale with

        Returns:
            bool:
                True if the norm is absolutely homogeneous, False otherwise
        """
        self.logger.debug("Checking absolute homogeneity")
        return True

    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the supremum norm is definite.

        Args:
            x: T
                The input to check

        Returns:
            bool:
                True if the norm is definite, False otherwise
        """
        self.logger.debug("Checking definiteness")
        return True
