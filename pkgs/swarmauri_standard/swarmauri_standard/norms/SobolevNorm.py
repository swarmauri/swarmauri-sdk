from typing import Union, Sequence, Callable, Optional
import numpy as np
import math
import logging

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from base.swarmauri_base.norms.NormBase import NormBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class SobolevNorm(NormBase):
    """
    Implementation of the Sobolev norm, which combines the L2 norm of a function and its derivatives.

    Inherits From:
        NormBase: Base implementation for norm computations

    Attributes:
        resource: Type of resource this component represents
    """

    resource: Optional[str] = ResourceTypes.NORM.value

    def compute(self, x: Union[Callable, Sequence, np.ndarray, str]) -> float:
        """
        Compute the Sobolev norm of the input, combining function and derivative norms.

        Args:
            x: The input to compute the norm of. Can be a callable function, a sequence of values,
                a numpy array, or a string representation.

        Returns:
            float: The computed Sobolev norm value.

        Raises:
            ValueError: If the input type is not supported or invalid.
        """
        logger.debug("Computing Sobolev norm")

        # Convert to numpy array for consistent processing
        if isinstance(x, Callable):
            # For callable function, evaluate at multiple points
            # Here we assume evaluation at a set of points, perhaps using quadrature
            # For simplicity, let's evaluate at 10 random points
            points = np.random.uniform(0, 1, 10)
            fx = np.array([x(p) for p in points])
            # Compute L2 norm of function
            func_norm = np.linalg.norm(fx, 2)
            # For derivatives, need to compute numerically or assume provided
            # For this example, we'll assume no higher derivatives
            deriv_norm = 0.0
            total_norm = func_norm + deriv_norm
        elif isinstance(x, (Sequence, np.ndarray)):
            # Assume x contains function and derivative values
            # Split into function and derivatives
            if len(x) < 2:
                # Only function value provided
                func = np.array(x)
                func_norm = np.linalg.norm(func, 2)
                deriv_norm = 0.0
                total_norm = func_norm + deriv_norm
            else:
                # First part is function, rest are derivatives
                func = x[0]
                func_norm = np.linalg.norm(func, 2)
                derivs = x[1:]
                deriv_norm = sum(np.linalg.norm(d, 2) for d in derivs)
                total_norm = func_norm + deriv_norm
        elif isinstance(x, str):
            # Try to evaluate string as function
            # For simplicity, assume it's a constant function
            try:
                value = float(x)
                func_norm = abs(value)
                deriv_norm = 0.0
                total_norm = func_norm + deriv_norm
            except ValueError:
                raise ValueError(f"Could not evaluate string '{x}' as a function")
        else:
            raise ValueError(f"Unsupported input type: {type(x)}")

        logger.debug(f"Computed Sobolev norm: {total_norm}")
        return total_norm

    def check_non_negativity(
        self, x: Union[Callable, Sequence, np.ndarray, str]
    ) -> None:
        """
        Verify the non-negativity property of the Sobolev norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify non-negativity for.

        Raises:
            AssertionError: If non-negativity is not satisfied.
        """
        logger.debug("Checking non-negativity")
        norm = self.compute(x)
        if norm < 0:
            raise AssertionError("Norm is negative, violating non-negativity")
        logger.debug("Non-negativity check passed")

    def check_triangle_inequality(
        self,
        x: Union[Callable, Sequence, np.ndarray, str],
        y: Union[Callable, Sequence, np.ndarray, str],
    ) -> None:
        """
        Verify the triangle inequality property of the Sobolev norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: The first input vector.
            y: The second input vector.

        Raises:
            AssertionError: If triangle inequality is not satisfied.
        """
        logger.debug("Checking triangle inequality")

        # Convert to numpy arrays
        if isinstance(x, Callable):
            x_vals = np.array([x(p) for p in np.random.uniform(0, 1, 10)])
        else:
            x_vals = np.array(x)

        if isinstance(y, Callable):
            y_vals = np.array([y(p) for p in np.random.uniform(0, 1, 10)])
        else:
            y_vals = np.array(y)

        sum_norm = self.compute(x_vals + y_vals)
        x_norm = self.compute(x_vals)
        y_norm = self.compute(y_vals)

        if (
            sum_norm > x_norm + y_norm + 1e-9
        ):  # Adding small epsilon for floating point errors
            raise AssertionError(
                f"Triangle inequality failed: {sum_norm} > {x_norm} + {y_norm}"
            )
        logger.debug("Triangle inequality check passed")

    def check_absolute_homogeneity(
        self, x: Union[Callable, Sequence, np.ndarray, str], alpha: float
    ) -> None:
        """
        Verify the absolute homogeneity property of the Sobolev norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: The input vector.
            alpha: The scalar to scale the vector by.

        Raises:
            AssertionError: If absolute homogeneity is not satisfied.
        """
        logger.debug("Checking absolute homogeneity")

        # Compute norm of scaled x
        scaled_x = self._scale_input(x, alpha)
        scaled_norm = self.compute(scaled_x)

        # Compute |alpha| * ||x||
        x_norm = self.compute(x)
        expected_norm = abs(alpha) * x_norm

        if not np.isclose(scaled_norm, expected_norm, atol=1e-9):
            raise AssertionError(
                f"Absolute homogeneity failed: {scaled_norm} != {expected_norm}"
            )
        logger.debug("Absolute homogeneity check passed")

    def check_definiteness(self, x: Union[Callable, Sequence, np.ndarray, str]) -> None:
        """
        Verify the definiteness property of the Sobolev norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify definiteness for.

        Raises:
            AssertionError: If definiteness is not satisfied.
        """
        logger.debug("Checking definiteness")
        norm = self.compute(x)

        if norm == 0:
            # Check if x is the zero vector
            if isinstance(x, (Sequence, np.ndarray)):
                if not all(v == 0 for v in x):
                    raise AssertionError(
                        "Norm is zero but input is not the zero vector"
                    )
            elif isinstance(x, Callable):
                # Check if function is identically zero
                points = np.random.uniform(0, 1, 10)
                if not all(abs(x(p)) < 1e-9 for p in points):
                    raise AssertionError(
                        "Norm is zero but function is not identically zero"
                    )
            else:
                # Handle other types if necessary
                pass
        logger.debug("Definiteness check passed")

    def _scale_input(
        self, x: Union[Callable, Sequence, np.ndarray, str], alpha: float
    ) -> Union[Callable, Sequence, np.ndarray, str]:
        """
        Helper method to scale the input by a factor alpha.

        Args:
            x: The input to scale.
            alpha: The scaling factor.

        Returns:
            Scaled input.
        """
        if isinstance(x, Callable):
            return lambda p: alpha * x(p)
        elif isinstance(x, (Sequence, np.ndarray)):
            return alpha * np.array(x)
        elif isinstance(x, str):
            # Handle string scaling - assumes it's a constant function
            try:
                value = float(x)
                return str(alpha * value)
            except ValueError:
                raise ValueError(f"Cannot scale string '{x}'")
        else:
            raise ValueError(f"Unsupported type for scaling: {type(x)}")
