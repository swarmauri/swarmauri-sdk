from typing import Union, Sequence, Callable, Optional, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.INorm import INorm
import logging
import numpy as np

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class LInfNorm(NormBase):
    """
    Implementation of the L-Infinity norm (supremum norm) for real-valued functions.

    Inherits From:
        NormBase: Base class for all norms in the system
        ComponentBase: Base class for all components in the system

    Attributes:
        resource: Type of resource this component represents
        type: Type identifier for this norm class
    """

    type: Literal["LInfNorm"] = "LInfNorm"
    resource: Optional[str] = ResourceTypes.NORM.value

    def compute(self, x: Union[Sequence, Callable]) -> float:
        """
        Compute the L-Infinity norm of the input.

        The L-Infinity norm is defined as the maximum absolute value in the domain
        of the input. For functions, this is the maximum absolute value of the function
        over its domain. For sequences, this is the maximum absolute value of the elements.

        Args:
            x: The input to compute the norm of. Can be a sequence or a callable function.

        Returns:
            float: The computed L-Infinity norm value.

        Raises:
            ValueError: If the input type is not supported
        """
        try:
            if callable(x):
                # For callable functions, evaluate at several points to estimate the maximum
                # Assuming the domain is bounded, we can sample key points
                # For simplicity, we'll assume the domain is [-1, 1]
                x_vals = np.linspace(-1, 1, 1000)
                y_vals = [abs(x(t)) for t in x_vals]
                return max(y_vals)
            elif isinstance(x, (Sequence, np.ndarray)):
                # For sequences, find the maximum absolute value
                return max(abs(val) for val in x)
            else:
                logger.error("Unsupported input type for LInfNorm.compute()")
                raise ValueError("Unsupported input type")
        except Exception as e:
            logger.error(f"Error in LInfNorm.compute(): {str(e)}")
            raise

    def check_non_negativity(self, x: Union[Sequence, Callable]) -> None:
        """
        Verify the non-negativity property of the L-Infinity norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify non-negativity for.

        Raises:
            AssertionError: If the non-negativity property is not satisfied
        """
        norm = self.compute(x)
        assert norm >= 0, "LInfNorm does not satisfy non-negativity"
        logger.info("LInfNorm non-negativity check passed")

    def check_triangle_inequality(
        self, x: Union[Sequence, Callable], y: Union[Sequence, Callable]
    ) -> None:
        """
        Verify the triangle inequality property of the L-Infinity norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: The first input vector
            y: The second input vector

        Raises:
            AssertionError: If the triangle inequality is not satisfied
        """
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = self.compute(
            [x[i] + y[i] for i in range(len(x))] if isinstance(x, Sequence) else None
        )

        assert norm_xy <= norm_x + norm_y, (
            "LInfNorm does not satisfy triangle inequality"
        )
        logger.info("LInfNorm triangle inequality check passed")

    def check_absolute_homogeneity(
        self, x: Union[Sequence, Callable], alpha: float
    ) -> None:
        """
        Verify the absolute homogeneity property of the L-Infinity norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: The input vector
            alpha: The scalar to scale the vector by

        Raises:
            AssertionError: If absolute homogeneity is not satisfied
        """
        norm_x = self.compute(x)
        scaled_x = [alpha * val for val in x] if isinstance(x, Sequence) else None
        norm_scaled = self.compute(scaled_x)

        assert np.isclose(norm_scaled, abs(alpha) * norm_x), (
            "LInfNorm does not satisfy absolute homogeneity"
        )
        logger.info("LInfNorm absolute homogeneity check passed")

    def check_definiteness(self, x: Union[Sequence, Callable]) -> None:
        """
        Verify the definiteness property of the L-Infinity norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify definiteness for.

        Raises:
            AssertionError: If definiteness is not satisfied
        """
        norm = self.compute(x)
        if isinstance(x, Sequence):
            is_zero = all(val == 0 for val in x)
        else:
            is_zero = x == 0

        if is_zero and norm != 0:
            raise AssertionError("LInfNorm does not satisfy definiteness: ||0|| != 0")
        if not is_zero and norm == 0:
            raise AssertionError(
                "LInfNorm does not satisfy definiteness: x != 0 but ||x|| = 0"
            )

        logger.info("LInfNorm definiteness check passed")
