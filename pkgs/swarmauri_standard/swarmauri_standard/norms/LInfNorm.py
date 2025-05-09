import logging
from typing import Sequence, TypeVar, Union
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

# Define a TypeVar to represent supported input types
T = TypeVar("T", Sequence[float], Union[callable, str])


@ComponentBase.register_type(NormBase, "LInfNorm")
class LInfNorm(NormBase):
    """
    A class implementing the L-infinity norm for real-valued functions.

    This class provides the concrete implementation of the LInfNorm, which measures
    the largest absolute value in a function's domain. It inherits from NormBase
    and implements the compute method to provide the L-infinity norm computation.

    Attributes:
        resource: Type of resource this class represents.

    Methods:
        compute: Computes the L-infinity norm of the given input.
    """

    resource: str = "LInfNorm"

    def __init__(self) -> None:
        """
        Initializes the LInfNorm object.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def compute(self, x: T) -> float:
        """
        Computes the L-infinity norm of the given input.

        The L-infinity norm is defined as the maximum absolute value in the input
        sequence or function.

        Args:
            x: Input to compute the norm of. It can be a sequence of floats, a
               callable function, or a string representation.

        Returns:
            float: The computed L-infinity norm value.

        Raises:
            ValueError: If the input type is not supported.
        """
        self.logger.debug(f"Computing L-infinity norm for input type {type(x)}")

        if isinstance(x, Sequence):
            # For sequences, compute the maximum absolute value
            return max(abs(value) for value in x)
        elif isinstance(x, str):
            # For string representation, attempt to process it
            # This can be extended for more complex string handling
            return self.compute([float(num) for num in x.split()])
        elif callable(x):
            # For callable objects, evaluate at specific points
            # This is a simplified approach; actual implementation may vary
            try:
                # Assuming the callable returns a sequence of values
                return self.compute(x())
            except Exception as e:
                raise ValueError("Callable did not return a sequence") from e
        else:
            raise ValueError(f"Unsupported input type: {type(x)}")

    # The following methods are inherited from NormBase and do not need to be
    # overridden unless specific behavior is required. They are included here
    # for completeness.

    def check_non_negativity(self, x: T) -> bool:
        """
        Verifies the non-negativity property of the norm.

        Args:
            x: Input to check non-negativity for

        Returns:
            bool: True if norm is non-negative, False otherwise
        """
        self.logger.debug("Checking non-negativity property")
        norm = self.compute(x)
        return norm >= 0

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verifies the triangle inequality property of the norm.

        Args:
            x: First input vector
            y: Second input vector

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        self.logger.debug("Checking triangle inequality property")
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = (
            self.compute(x + y)
            if isinstance(x, Sequence) and isinstance(y, Sequence)
            else 0.0
        )
        return norm_xy <= norm_x + norm_y

    def check_absolute_homogeneity(self, x: T, alpha: float) -> bool:
        """
        Verifies the absolute homogeneity property of the norm.

        Args:
            x: Input vector
            alpha: Scaling factor

        Returns:
            bool: True if absolute homogeneity holds, False otherwise
        """
        self.logger.debug(f"Checking absolute homogeneity with alpha {alpha}")
        norm_x = self.compute(x)
        norm_alpha_x = (
            self.compute([alpha * val for val in x]) if isinstance(x, Sequence) else 0.0
        )
        return norm_alpha_x == abs(alpha) * norm_x

    def check_definiteness(self, x: T) -> bool:
        """
        Verifies the definiteness property of the norm.

        A norm is definite if norm(x) = 0 if and only if x = 0.

        Args:
            x: Input vector

        Returns:
            bool: True if definiteness holds, False otherwise
        """
        self.logger.debug("Checking definiteness property")
        norm = self.compute(x)
        if norm == 0:
            return x == 0
        return True


logger = logging.getLogger(__name__)
