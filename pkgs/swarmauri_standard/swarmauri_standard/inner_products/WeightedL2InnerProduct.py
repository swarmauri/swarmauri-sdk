import logging
from numbers import Number
from typing import Any, Callable, Dict, Literal, TypeVar, Union

import numpy as np
from swarmauri_core.vectors.IVector import IVector
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Vector = TypeVar("Vector", bound=IVector)
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "WeightedL2InnerProduct")
class WeightedL2InnerProduct(InnerProductBase):
    """
    Weighted L2 inner product for real/complex functions.

    This class implements a weighted L2 inner product, which defines an inner product
    with position-dependent weights for weighted L2 spaces. The weight function must
    be strictly positive.

    Attributes
    ----------
    type : Literal["WeightedL2InnerProduct"]
        The type identifier for this inner product implementation
    resource : str
        The resource type identifier, defaulting to INNER_PRODUCT
    weight_function : Callable[[Any], Union[float, np.ndarray]]
        A function that returns a positive weight at each position
    """

    type: Literal["WeightedL2InnerProduct"] = "WeightedL2InnerProduct"
    weight_function: Callable[[Any], Union[float, np.ndarray]]

    def __init__(
        self,
        weight_function: Callable[[Any], Union[float, np.ndarray]],
        **kwargs: Dict[str, Any],
    ):
        """
        Initialize the WeightedL2InnerProduct with a weight function.

        Parameters
        ----------
        weight_function : Callable[[Any], Union[float, np.ndarray]]
            A function that returns a positive weight at each position
        **kwargs : Dict[str, Any]
            Additional keyword arguments

        Raises
        ------
        ValueError
            If the weight function is not provided
        """
        if weight_function is None:
            logger.error("Weight function must be provided")
            raise ValueError("Weight function must be provided")

        kwargs["weight_function"] = weight_function
        super().__init__(**kwargs)

        logger.info("WeightedL2InnerProduct initialized with custom weight function")

    def _validate_weight_at_points(self, points: Any) -> None:
        """
        Validate that the weight function is positive at given points.

        Parameters
        ----------
        points : Any
            Points at which to evaluate the weight function

        Raises
        ------
        ValueError
            If the weight function returns non-positive values
        """
        weights = self.weight_function(points)

        if isinstance(weights, (np.ndarray, list)):
            if np.any(np.array(weights) <= 0):
                logger.error("Weight function must be strictly positive")
                raise ValueError("Weight function must be strictly positive")
        elif weights <= 0:
            logger.error("Weight function must be strictly positive")
            raise ValueError("Weight function must be strictly positive")

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> complex:
        """
        Compute the weighted L2 inner product between two objects.

        For functions, the inner product is computed as:
        <a, b> = ∫ a(x) * conj(b(x)) * w(x) dx

        For vectors/matrices, the inner product is:
        <a, b> = sum(a * conj(b) * w)

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        complex
            The inner product value

        Raises
        ------
        TypeError
            If the input types are not supported
        ValueError
            If the dimensions of inputs don't match
        """
        logger.debug(
            f"Computing weighted L2 inner product between {type(a)} and {type(b)}"
        )

        # Handle callable functions (requires numerical integration)
        if callable(a) and callable(b):
            # This is a simplified implementation
            # In a real-world scenario, you would use numerical integration
            # over the domain with appropriate quadrature points

            # For demonstration, we'll use a simple grid
            # In practice, replace with proper numerical integration
            try:
                # Example: integrate over [0,1] with 1000 points
                # This is a simplification; actual implementation would depend on the domain
                x = np.linspace(0, 1, 1000)
                weights = self.weight_function(x)

                # Check positivity of weights
                if np.any(weights <= 0):
                    logger.error("Weight function returned non-positive values")
                    raise ValueError("Weight function must be strictly positive")

                # Compute function values
                a_values = np.array([a(xi) for xi in x])
                b_values = np.array([b(xi) for xi in x])

                # Compute inner product with trapezoidal rule
                dx = x[1] - x[0]
                result = np.sum(a_values * np.conjugate(b_values) * weights) * dx
                return complex(result)
            except Exception as e:
                logger.error(
                    f"Error computing inner product for callable functions: {str(e)}"
                )
                raise

        # Handle numpy arrays or vectors
        elif isinstance(a, (np.ndarray, list)) and isinstance(b, (np.ndarray, list)):
            a_array = np.array(a)
            b_array = np.array(b)

            if a_array.shape != b_array.shape:
                logger.error(f"Dimension mismatch: {a_array.shape} vs {b_array.shape}")
                raise ValueError(
                    f"Dimensions must match: {a_array.shape} vs {b_array.shape}"
                )

            # Get weights for each position
            # For simplicity, we assume the arrays represent points where we evaluate the weight
            # In practice, this might need to be adapted based on what the arrays represent
            weights = self.weight_function(
                np.arange(len(a_array)) if a_array.ndim == 1 else None
            )

            # Ensure weights have the right shape
            if isinstance(weights, Number):
                weights_array = np.full_like(a_array, weights, dtype=float)
            else:
                weights_array = np.array(weights)
                if weights_array.shape != a_array.shape:
                    logger.error(
                        f"Weight shape {weights_array.shape} doesn't match input shape {a_array.shape}"
                    )
                    raise ValueError(
                        f"Weight shape must match input shape: {weights_array.shape} vs {a_array.shape}"
                    )

            # Check positivity of weights
            if np.any(weights_array <= 0):
                logger.error("Weight function returned non-positive values")
                raise ValueError("Weight function must be strictly positive")

            # Compute the weighted inner product
            result = np.sum(a_array * np.conjugate(b_array) * weights_array)
            return complex(result)

        else:
            logger.error(f"Unsupported types: {type(a)} and {type(b)}")
            raise TypeError(
                f"Unsupported types for WeightedL2InnerProduct: {type(a)} and {type(b)}"
            )

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the weighted L2 inner product satisfies the conjugate symmetry property:
        <a, b> = <b, a>* (complex conjugate).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object
        b : Union[Vector, Matrix, Callable]
            The second object

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug(f"Checking conjugate symmetry for {type(a)} and {type(b)}")

        try:
            # Compute <a, b>
            inner_ab = self.compute(a, b)

            # Compute <b, a> and take complex conjugate
            inner_ba_conj = np.conjugate(self.compute(b, a))

            # Check if they are approximately equal
            is_symmetric = np.isclose(inner_ab, inner_ba_conj)

            if not is_symmetric:
                logger.warning(
                    f"Conjugate symmetry check failed: <a,b>={inner_ab}, <b,a>*={inner_ba_conj}"
                )

            return is_symmetric
        except Exception as e:
            logger.error(f"Error checking conjugate symmetry: {str(e)}")
            return False

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the weighted L2 inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second object
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise
        """
        logger.debug(
            f"Checking linearity in first argument with alpha={alpha}, beta={beta}"
        )

        try:
            # For callable functions
            if callable(a1) and callable(a2) and callable(b):
                # Create a linear combination function
                def linear_combo(x):
                    return alpha * a1(x) + beta * a2(x)

                # Compute <alpha*a1 + beta*a2, b>
                left_side = self.compute(linear_combo, b)

                # Compute alpha*<a1, b> + beta*<a2, b>
                right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            # For arrays
            elif (
                isinstance(a1, (np.ndarray, list))
                and isinstance(a2, (np.ndarray, list))
                and isinstance(b, (np.ndarray, list))
            ):
                a1_array = np.array(a1)
                a2_array = np.array(a2)

                # Create linear combination
                linear_combo = alpha * a1_array + beta * a2_array

                # Compute <alpha*a1 + beta*a2, b>
                left_side = self.compute(linear_combo, b)

                # Compute alpha*<a1, b> + beta*<a2, b>
                right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            else:
                logger.error(
                    f"Unsupported types: {type(a1)}, {type(a2)}, and {type(b)}"
                )
                return False

            # Check if they are approximately equal
            is_linear = np.isclose(left_side, right_side)

            if not is_linear:
                logger.warning(
                    f"Linearity check failed: <alpha*a1+beta*a2,b>={left_side}, "
                    f"alpha*<a1,b>+beta*<a2,b>={right_side}"
                )

            return is_linear
        except Exception as e:
            logger.error(f"Error checking linearity: {str(e)}")
            return False

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the weighted L2 inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for {type(a)}")

        try:
            # Compute <a, a>
            inner_product = self.compute(a, a)

            # Check if it's real (should be for any inner product)
            if not np.isclose(inner_product.imag, 0):
                logger.warning(
                    f"Inner product <a,a> has non-zero imaginary part: {inner_product.imag}"
                )
                return False

            # Check if it's non-negative
            is_positive = inner_product.real >= 0

            # For arrays, also check if <a,a> = 0 implies a = 0
            if isinstance(a, (np.ndarray, list)) and np.isclose(inner_product.real, 0):
                a_array = np.array(a)
                is_positive = is_positive and np.allclose(a_array, 0)

            if not is_positive:
                logger.warning(f"Positivity check failed: <a,a>={inner_product.real}")

            return is_positive
        except Exception as e:
            logger.error(f"Error checking positivity: {str(e)}")
            return False

    def norm(self, a: Union[Vector, Matrix, Callable]) -> float:
        """
        Compute the norm induced by the weighted L2 inner product.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to compute the norm for

        Returns
        -------
        float
            The norm value

        Raises
        ------
        ValueError
            If the inner product is negative (which shouldn't happen for a valid inner product)
        """
        logger.debug(f"Computing norm for {type(a)}")

        try:
            inner_product = self.compute(a, a)

            # The inner product <a,a> should be real and non-negative
            if inner_product.imag != 0 or inner_product.real < 0:
                logger.error(f"Invalid inner product value: {inner_product}")
                raise ValueError(
                    f"Inner product <a,a> must be real and non-negative, got {inner_product}"
                )

            return np.sqrt(inner_product.real)
        except Exception as e:
            logger.error(f"Error computing norm: {str(e)}")
            raise
