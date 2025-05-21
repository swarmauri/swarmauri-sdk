import logging
from typing import (
    Callable,
    Dict,
    Literal,
    Sequence,
    TypeVar,
    Union,
)

import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for supported input types
T = TypeVar("T")
VectorType = TypeVar("VectorType", bound=IVector)
MatrixType = TypeVar("MatrixType", bound=IMatrix)
SequenceType = TypeVar("SequenceType", bound=Sequence)
StringType = TypeVar("StringType", bound=str)
CallableType = TypeVar("CallableType", bound=Callable)


@ComponentBase.register_type(NormBase, "SobolevNorm")
class SobolevNorm(NormBase):
    """
    Sobolev norm implementation that combines function and derivative norms.

    The Sobolev norm accounts for the smoothness of a function by incorporating
    the L2 norm of both the function and its derivatives up to a specified order.

    Attributes
    ----------
    type : Literal["SobolevNorm"]
        The type identifier for this norm.
    order : int
        The highest derivative order to consider in the norm computation.
    weights : Dict[int, float]
        Weights for each derivative order in the norm computation.
    """

    type: Literal["SobolevNorm"] = "SobolevNorm"
    order: int = Field(default=1, description="Highest derivative order to consider")
    weights: Dict[int, float] = Field(
        default_factory=lambda: {0: 1.0, 1: 1.0},
        description="Weights for each derivative order",
    )

    def __init__(self, **kwargs):
        """
        Initialize the Sobolev norm with specified parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the parent class constructor.
            May include 'order' and 'weights' to customize the norm.
        """
        super().__init__(**kwargs)
        # Ensure weights dictionary has entries for all orders up to self.order
        for i in range(self.order + 1):
            if i not in self.weights:
                self.weights[i] = 1.0

        logger.debug(
            f"Initialized SobolevNorm with order {self.order} and weights {self.weights}"
        )

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> float:
        """
        Compute the Sobolev norm of the input.

        For callable inputs, computes the weighted sum of L2 norms of the function and its derivatives.
        For other types, falls back to L2 norm of the input itself.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed Sobolev norm value.

        Raises
        ------
        TypeError
            If the input type is not supported or derivatives cannot be computed.
        ValueError
            If the norm cannot be computed for the given input.
        """
        logger.debug(f"Computing Sobolev norm for {type(x).__name__}")

        if callable(x):
            return self._compute_for_callable(x)
        elif isinstance(x, (IVector, IMatrix, Sequence)):
            # For non-callable types, use only the function value (0th derivative)
            # with appropriate weight
            logger.debug("Computing Sobolev norm for non-callable using L2 norm")
            return self._compute_l2_norm(x) * self.weights.get(0, 1.0)
        else:
            raise TypeError(
                f"Unsupported input type for Sobolev norm: {type(x).__name__}"
            )

    def _compute_for_callable(self, func: Callable) -> float:
        """
        Compute the Sobolev norm for a callable function.

        Parameters
        ----------
        func : Callable
            The function for which to compute the Sobolev norm.

        Returns
        -------
        float
            The computed Sobolev norm value.

        Raises
        ------
        ValueError
            If derivatives cannot be computed or evaluated.
        """
        # Check if the function has the necessary attributes for computing derivatives
        if not hasattr(func, "derivative") and not hasattr(func, "__call__"):
            raise ValueError(
                "Function must support derivative computation for Sobolev norm"
            )

        # Initialize sum for the norm calculation
        norm_sum = 0.0

        try:
            # Compute L2 norm of the function itself (0th derivative)
            if 0 in self.weights and self.weights[0] > 0:
                f_norm = self._evaluate_function_norm(func)
                norm_sum += self.weights[0] * f_norm**2
                logger.debug(
                    f"0th derivative contribution: {self.weights[0] * f_norm**2}"
                )

            # Compute L2 norms of derivatives
            current_derivative = func
            for i in range(1, self.order + 1):
                if i in self.weights and self.weights[i] > 0:
                    # Get the next derivative
                    if hasattr(current_derivative, "derivative"):
                        current_derivative = current_derivative.derivative()
                    else:
                        # If no derivative method, raise error
                        raise ValueError(
                            f"Cannot compute {i}th derivative of the function"
                        )

                    # Compute L2 norm of this derivative
                    d_norm = self._evaluate_function_norm(current_derivative)
                    norm_sum += self.weights[i] * d_norm**2
                    logger.debug(
                        f"{i}th derivative contribution: {self.weights[i] * d_norm**2}"
                    )

            # Return the square root of the weighted sum
            return np.sqrt(norm_sum)

        except Exception as e:
            logger.error(f"Error computing Sobolev norm: {str(e)}")
            raise ValueError(f"Failed to compute Sobolev norm: {str(e)}")

    def _evaluate_function_norm(self, func: Callable) -> float:
        """
        Evaluate the L2 norm of a function over a default domain.

        Parameters
        ----------
        func : Callable
            The function to evaluate.

        Returns
        -------
        float
            The L2 norm of the function.
        """
        # For simplicity, evaluate on a default domain [0, 1] with 100 points
        # In practice, this would need to be customized based on the application
        x_values = np.linspace(0, 1, 100)
        try:
            y_values = np.array([func(x) for x in x_values])
            # Compute approximate L2 norm using trapezoidal rule
            return np.sqrt(np.trapz(y_values**2, x_values))
        except Exception as e:
            logger.error(f"Error evaluating function: {str(e)}")
            raise ValueError(f"Failed to evaluate function norm: {str(e)}")

    def _compute_l2_norm(self, x: Union[VectorType, MatrixType, SequenceType]) -> float:
        """
        Compute the L2 norm of a non-callable input.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType]
            The input for which to compute the L2 norm.

        Returns
        -------
        float
            The L2 norm of the input.

        Raises
        ------
        ValueError
            If the norm cannot be computed for the given input.
        """
        try:
            if hasattr(x, "norm"):
                # Use the object's own norm method if available
                return x.norm()
            elif isinstance(x, Sequence):
                # Convert sequence to numpy array and compute norm
                return np.linalg.norm(np.array(x, dtype=float))
            else:
                raise ValueError(f"Cannot compute L2 norm for type {type(x).__name__}")
        except Exception as e:
            logger.error(f"Error computing L2 norm: {str(e)}")
            raise ValueError(f"Failed to compute L2 norm: {str(e)}")

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Sobolev norm satisfies the non-negativity property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm is non-negative, False otherwise.
        """
        try:
            norm_value = self.compute(x)
            return norm_value >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Sobolev norm satisfies the definiteness property.

        The definiteness property states that the norm of x is 0 if and only if x is 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm satisfies the definiteness property, False otherwise.
        """
        try:
            # For a zero input, the norm should be zero
            if self._is_zero(x):
                norm_value = self.compute(x)
                return abs(norm_value) < 1e-10  # Allow for numerical precision issues

            # For a non-zero input, the norm should be positive
            norm_value = self.compute(x)
            return norm_value > 0
        except Exception as e:
            logger.error(f"Error checking definiteness: {str(e)}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the Sobolev norm satisfies the triangle inequality.

        The triangle inequality states that norm(x + y) <= norm(x) + norm(y).

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The first input.
        y : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The second input.

        Returns
        -------
        bool
            True if the norm satisfies the triangle inequality, False otherwise.

        Raises
        ------
        TypeError
            If inputs are not of the same type.
        """
        # Ensure x and y are of the same type - don't catch this error
        if not isinstance(y, type(x)):
            raise TypeError(
                "Inputs must be of the same type for triangle inequality check"
            )

        try:
            # Compute norms
            norm_x = self.compute(x)
            norm_y = self.compute(y)

            # For callable functions
            if callable(x) and callable(y):
                # Create a new function representing x + y
                def sum_func(t):
                    return x(t) + y(t)

                # For functions with derivatives
                if hasattr(x, "derivative") and hasattr(y, "derivative"):
                    # Add derivative method to sum_func
                    def create_derivative(func_x, func_y):
                        def derivative_func(t):
                            return func_x.derivative()(t) + func_y.derivative()(t)

                        return derivative_func

                    sum_func.derivative = lambda: create_derivative(x, y)

                norm_sum = self.compute(sum_func)

            # For vector-like objects
            elif hasattr(x, "__add__"):
                sum_xy = x + y
                norm_sum = self.compute(sum_xy)

            # For sequences
            elif isinstance(x, Sequence) and isinstance(y, Sequence):
                if len(x) != len(y):
                    raise ValueError(
                        "Sequences must have the same length for triangle inequality check"
                    )
                sum_xy = [x[i] + y[i] for i in range(len(x))]
                norm_sum = self.compute(sum_xy)

            else:
                raise TypeError(f"Cannot compute sum for type {type(x).__name__}")

            # Check triangle inequality
            logger.debug(f"Triangle inequality check: {norm_sum} <= {norm_x + norm_y}")
            return (
                norm_sum <= norm_x + norm_y + 1e-10
            )  # Allow for numerical precision issues

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False

    # Fix for check_absolute_homogeneity
    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: float,
    ) -> bool:
        """
        Check if the Sobolev norm satisfies the absolute homogeneity property.

        The absolute homogeneity property states that norm(a*x) = |a|*norm(x) for scalar a.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input.
        scalar : float
            The scalar value.

        Returns
        -------
        bool
            True if the norm satisfies the absolute homogeneity property, False otherwise.
        """
        try:
            # Compute norm of x
            norm_x = self.compute(x)

            # For callable functions
            if callable(x):
                # Create a new function representing scalar * x
                def scaled_func(t):
                    return scalar * x(t)

                # For functions with derivatives
                if hasattr(x, "derivative"):
                    # Add derivative method to scaled_func
                    def create_derivative(func_x, scale):
                        def derivative_func(t):
                            return scale * func_x.derivative()(t)

                        return derivative_func

                    scaled_func.derivative = lambda: create_derivative(x, scalar)

                norm_scaled = self.compute(scaled_func)

            # For vector-like objects with direct multiplication support
            elif hasattr(x, "__mul__") and not isinstance(x, (list, tuple)):
                scaled_x = x * scalar
                norm_scaled = self.compute(scaled_x)

            # For sequences (lists/tuples)
            elif isinstance(x, Sequence):
                # Handle lists by multiplying each element separately
                scaled_x = [float(scalar) * float(item) for item in x]
                norm_scaled = self.compute(scaled_x)

            else:
                raise TypeError(f"Cannot scale input of type {type(x).__name__}")

            # Check absolute homogeneity
            expected_norm = abs(scalar) * norm_x
            logger.debug(
                f"Absolute homogeneity check: {norm_scaled} == {expected_norm}"
            )
            return abs(norm_scaled - expected_norm) < 1e-10 * (
                1 + abs(expected_norm)
            )  # Relative tolerance

        except Exception as e:
            logger.error(f"Error checking absolute homogeneity: {str(e)}")
            return False

    # Fix for _is_zero
    def _is_zero(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the input is effectively zero.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the input is effectively zero, False otherwise.
        """
        try:
            if callable(x) and not hasattr(x, "is_zero"):
                # Sample the function at several points to check if it's zero
                test_points = np.linspace(0, 1, 10)
                return all(abs(x(t)) < 1e-10 for t in test_points)

            elif isinstance(x, Sequence):
                return all(abs(float(item)) < 1e-10 for item in x)

            elif hasattr(x, "is_zero") and callable(x.is_zero):
                # Call the is_zero method directly without comparing to float
                return bool(x.is_zero())

            elif hasattr(x, "__abs__") and callable(x.__abs__):
                # Use isinstance to make sure __abs__ returns something we can compare
                abs_value = x.__abs__()
                if isinstance(abs_value, (int, float)):
                    return abs_value < 1e-10
                return False

            else:
                # Default case
                return x == 0

        except Exception as e:
            logger.error(f"Error checking if input is zero: {str(e)}")
            return False
