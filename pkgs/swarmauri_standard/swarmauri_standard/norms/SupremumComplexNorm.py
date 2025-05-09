from typing import Union, Sequence, Callable, Optional, Tuple, Type, cast
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.norms.INorm import INorm
import logging
import numpy as np

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "SupremumComplexNorm")
class SupremumComplexNorm(NormBase):
    """Concrete implementation of the NormBase class for computing the supremum norm for complex-valued functions.

    The supremum norm (also known as the infinity norm) computes the maximum absolute value of a complex function
    over a given interval [a, b]. This implementation handles both function evaluations and sequence inputs.

    Inherits From:
        NormBase: Base class providing the interface for norm computations
        ComponentBase: Base class for all components in the system

    Attributes:
        resource: Type of resource this component represents
    """
    resource: Optional[str] = "norm"
    type: Type[str] = "SupremumComplexNorm"

    def __init__(self):
        """Initialize the SupremumComplexNorm instance."""
        super().__init__()
        logger.debug("Initialized SupremumComplexNorm")

    def compute(self, x: Union[Callable, Sequence, str, bytes, np.ndarray]) -> float:
        """Compute the supremum norm of the input.

        For functions: Evaluates the function over the interval [a, b] and finds the maximum absolute value.
        For sequences: Finds the maximum absolute value in the sequence.

        Args:
            x: The input to compute the norm of. Can be a function, sequence, string, or bytes.

        Returns:
            float: The computed supremum norm value.

        Raises:
            ValueError: If the input type is not supported.
            TypeError: If the input cannot be processed.
        """
        logger.debug("Computing supremum norm")
        
        try:
            if callable(x):
                # Assuming interval [a, b] is [-1, 1] if not specified
                # This would need to be generalized based on actual requirements
                a, b = -1.0, 1.0
                x_eval = cast(Callable, x)
                samples = 1000  # Number of evaluation points
                x_values = np.linspace(a, b, samples)
                y_values = np.abs(x_eval(x_values))
                return np.max(y_values)
            
            elif isinstance(x, (Sequence, np.ndarray)):
                return np.max(np.abs(x))
            
            elif isinstance(x, (str, bytes)):
                # Handle string or bytes input if necessary
                # For example, treat as sequence of characters
                return np.max(np.abs([ord(c) for c in x]))
            
            else:
                raise ValueError(f"Unsupported input type: {type(x).__name__}")
                
        except Exception as e:
            logger.error(f"Error computing supremum norm: {str(e)}")
            raise TypeError("Failed to compute norm due to invalid input type") from e

    def check_non_negativity(self, x: Union[Callable, Sequence, str, bytes, np.ndarray]) -> None:
        """Verify the non-negativity property of the norm.

        Args:
            x: The input to verify non-negativity for.

        Raises:
            AssertionError: If the norm is negative.
        """
        logger.debug("Checking non-negativity property")
        norm_value = self.compute(x)
        assert norm_value >= 0, "Norm value is negative"

    def check_triangle_inequality(self, x: Union[Callable, Sequence, str, bytes, np.ndarray],
                                    y: Union[Callable, Sequence, str, bytes, np.ndarray]) -> None:
        """Verify the triangle inequality property of the norm.

        Args:
            x: The first input vector.
            y: The second input vector.

        Raises:
            AssertionError: If the triangle inequality is not satisfied.
        """
        logger.debug("Checking triangle inequality property")
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = self.compute(x + y)
        assert norm_xy <= norm_x + norm_y, "Triangle inequality violated"

    def check_absolute_homogeneity(self, x: Union[Callable, Sequence, str, bytes, np.ndarray],
                                    alpha: float) -> None:
        """Verify the absolute homogeneity property of the norm.

        Args:
            x: The input vector.
            alpha: The scalar to scale the vector by.

        Raises:
            AssertionError: If absolute homogeneity is not satisfied.
        """
        logger.debug("Checking absolute homogeneity property")
        norm_x = self.compute(x)
        scaled_x = alpha * x
        norm_scaled_x = self.compute(scaled_x)
        assert np.isclose(norm_scaled_x, abs(alpha) * norm_x, rtol=1e-9), \
            "Absolute homogeneity property not satisfied"

    def check_definiteness(self, x: Union[Callable, Sequence, str, bytes, np.ndarray]) -> None:
        """Verify the definiteness property of the norm.

        Args:
            x: The input to verify definiteness for.

        Raises:
            AssertionError: If definiteness is not satisfied.
        """
        logger.debug("Checking definiteness property")
        norm_value = self.compute(x)
        if norm_value == 0:
            # Check if x is the zero vector
            if isinstance(x, Callable):
                # For functions, check if it's the zero function
                # This is a simplified check and may need more sophisticated handling
                try:
                    if x(0) == 0:
                        return
                except:
                    pass
                raise AssertionError("Non-zero function has zero norm")
            elif isinstance(x, (Sequence, np.ndarray, str, bytes)):
                if all(v == 0 for v in x):
                    return
                else:
                    raise AssertionError("Non-zero vector has zero norm")
            else:
                raise AssertionError("Unsupported type for definiteness check")
        else:
            return