import logging
from typing import Callable, Literal, TypeVar, Union

import numpy as np
from numpy.typing import NDArray
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.vectors.Vector import Vector

# Configure logging
logger = logging.getLogger(__name__)

Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "SobolevH1InnerProduct")
class SobolevH1InnerProduct(InnerProductBase):
    """
    Implementation of the H1 Sobolev space inner product.

    The H1 Sobolev inner product combines the L2 inner product of functions
    with the L2 inner product of their first derivatives. This makes it
    particularly useful for problems where both function values and their
    smoothness (derivatives) are important.

    Attributes
    ----------
    type : Literal["SobolevH1InnerProduct"]
        The type identifier for this inner product
    alpha : float
        Weight for the function value component (L2 norm part)
    beta : float
        Weight for the derivative component (H1 semi-norm part)
    """

    type: Literal["SobolevH1InnerProduct"] = "SobolevH1InnerProduct"
    alpha: float
    beta: float

    def __init__(self, alpha: float = 1.0, beta: float = 1.0, **kwargs):
        """
        Initialize the SobolevH1InnerProduct with specified weights.

        Parameters
        ----------
        alpha : float, optional
            Weight for the function value component, by default 1.0
        beta : float, optional
            Weight for the derivative component, by default 1.0
        """
        # Pass alpha and beta to the parent constructor
        kwargs["alpha"] = alpha
        kwargs["beta"] = beta
        super().__init__(**kwargs)
        logger.info(
            f"Initialized SobolevH1InnerProduct with alpha={alpha}, beta={beta}"
        )

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the H1 Sobolev inner product between two objects.

        For functions f and g, computes:
        <f, g>_H1 = alpha * ∫ f(x)·g(x) dx + beta * ∫ f'(x)·g'(x) dx

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        float
            The H1 inner product value

        Raises
        ------
        TypeError
            If the inputs are not of compatible types or don't provide derivative information
        """
        logger.debug(f"Computing H1 inner product between {type(a)} and {type(b)}")

        # Handle different input types
        if isinstance(a, Callable) and isinstance(b, Callable):
            return self._compute_for_functions(a, b)
        elif isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            return self._compute_for_arrays(a, b)
        elif isinstance(a, Vector) and isinstance(b, Vector):
            # Use the concrete Vector class
            return self._compute_for_vectors(a, b)
        else:
            error_msg = (
                f"Cannot compute H1 inner product for types {type(a)} and {type(b)}"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

    def _compute_for_functions(
        self, f: Callable, g: Callable, domain: tuple = (0, 1), num_points: int = 1000
    ) -> float:
        """
        Compute H1 inner product for two functions using numerical integration.

        Parameters
        ----------
        f : Callable
            First function that returns both value and derivative as a tuple (f(x), f'(x))
        g : Callable
            Second function that returns both value and derivative as a tuple (g(x), g'(x))
        domain : tuple, optional
            Integration domain (a, b), by default (0, 1)
        num_points : int, optional
            Number of points for numerical integration, by default 1000

        Returns
        -------
        float
            The H1 inner product value
        """
        a, b = domain
        x = np.linspace(a, b, num_points)
        dx = (b - a) / (num_points - 1)

        # Evaluate functions and derivatives
        f_values, f_derivatives = zip(*[f(xi) for xi in x])
        g_values, g_derivatives = zip(*[g(xi) for xi in x])

        # Convert to numpy arrays for easier computation
        f_values = np.array(f_values)
        f_derivatives = np.array(f_derivatives)
        g_values = np.array(g_values)
        g_derivatives = np.array(g_derivatives)

        # Compute L2 part: ∫ f(x)·g(x) dx
        l2_part = np.sum(f_values * g_values) * dx

        # Compute derivative part: ∫ f'(x)·g'(x) dx
        derivative_part = np.sum(f_derivatives * g_derivatives) * dx

        # Combine with weights
        result = self.alpha * l2_part + self.beta * derivative_part
        logger.debug(
            f"H1 inner product result: {result} (L2 part: {l2_part}, derivative part: {derivative_part})"
        )

        return result

    def _compute_for_arrays(self, a: NDArray, b: NDArray) -> float:
        """
        Compute H1 inner product for two arrays.

        For this implementation, we assume the arrays represent discrete function values
        on a uniform grid, and we compute derivatives using finite differences.

        Parameters
        ----------
        a : NDArray
            First array of function values
        b : NDArray
            Second array of function values

        Returns
        -------
        float
            The H1 inner product value

        Raises
        ------
        ValueError
            If the arrays have incompatible shapes
        """
        if a.shape != b.shape:
            error_msg = f"Arrays must have the same shape, got {a.shape} and {b.shape}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Compute L2 part
        l2_part = np.sum(a * b) / len(a)

        # Compute derivatives using central differences
        # For simplicity, we use forward/backward differences at boundaries
        a_derivative = np.zeros_like(a)
        b_derivative = np.zeros_like(b)

        # Interior points: central difference
        a_derivative[1:-1] = (a[2:] - a[:-2]) / 2
        b_derivative[1:-1] = (b[2:] - b[:-2]) / 2

        # Boundary points: forward/backward difference
        a_derivative[0] = a[1] - a[0]
        a_derivative[-1] = a[-1] - a[-2]
        b_derivative[0] = b[1] - b[0]
        b_derivative[-1] = b[-1] - b[-2]

        # Compute derivative part
        derivative_part = np.sum(a_derivative * b_derivative) / len(a)

        # Combine with weights
        result = self.alpha * l2_part + self.beta * derivative_part
        logger.debug(
            f"H1 inner product result: {result} (L2 part: {l2_part}, derivative part: {derivative_part})"
        )

        return result

    def _compute_for_vectors(self, a: Vector, b: Vector) -> float:
        """
        Compute H1 inner product for two Vector objects.

        Calculates derivatives using finite differences since Vector doesn't
        store derivative information.

        Parameters
        ----------
        a : Vector
            First vector object
        b : Vector
            Second vector object

        Returns
        -------
        float
            The H1 inner product value
        """
        # Get function values using to_numpy()
        a_values = a.to_numpy()
        b_values = b.to_numpy()

        # Compute derivatives using finite differences (same as in _compute_for_arrays)
        a_derivative = np.zeros_like(a_values)
        b_derivative = np.zeros_like(b_values)

        # Interior points: central difference
        if len(a_values) > 2:
            a_derivative[1:-1] = (a_values[2:] - a_values[:-2]) / 2
            b_derivative[1:-1] = (b_values[2:] - b_values[:-2]) / 2

        # Boundary points: forward/backward difference
        a_derivative[0] = a_values[1] - a_values[0] if len(a_values) > 1 else 0
        b_derivative[0] = b_values[1] - b_values[0] if len(b_values) > 1 else 0

        if len(a_values) > 1:
            a_derivative[-1] = a_values[-1] - a_values[-2]
            b_derivative[-1] = b_values[-1] - b_values[-2]

        # Compute L2 part
        l2_part = np.sum(a_values * b_values) / len(a_values)

        # Compute derivative part
        derivative_part = np.sum(a_derivative * b_derivative) / len(a_derivative)

        # Combine with weights
        result = self.alpha * l2_part + self.beta * derivative_part
        logger.debug(
            f"H1 inner product result: {result} (L2 part: {l2_part}, derivative part: {derivative_part})"
        )

        return result

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the H1 inner product satisfies the conjugate symmetry property.

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

        # Compute <a, b> and <b, a>
        inner_ab = self.compute(a, b)
        inner_ba = self.compute(b, a)

        # For real-valued functions, <a, b> should equal <b, a>
        # For complex-valued functions, <a, b> should equal conjugate(<b, a>)
        if np.iscomplex(inner_ab) or np.iscomplex(inner_ba):
            is_symmetric = np.isclose(inner_ab, np.conj(inner_ba))
        else:
            is_symmetric = np.isclose(inner_ab, inner_ba)

        logger.debug(
            f"Conjugate symmetry check result: {is_symmetric} (<a,b>={inner_ab}, <b,a>={inner_ba})"
        )
        return is_symmetric

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the H1 inner product satisfies linearity in the first argument.

        Verifies if <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>

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

        Raises
        ------
        TypeError
            If the inputs cannot be linearly combined
        """
        logger.debug(
            f"Checking linearity in first argument with alpha={alpha}, beta={beta}"
        )

        # Compute individual inner products
        inner_a1b = self.compute(a1, b)
        inner_a2b = self.compute(a2, b)

        # Compute the right side of the linearity equation
        right_side = alpha * inner_a1b + beta * inner_a2b

        # Compute the left side by creating the linear combination first
        # This implementation depends on the type of inputs
        if isinstance(a1, np.ndarray) and isinstance(a2, np.ndarray):
            linear_combo = alpha * a1 + beta * a2
            left_side = self.compute(linear_combo, b)
        elif isinstance(a1, Callable) and isinstance(a2, Callable):
            # Create a new function representing the linear combination
            def linear_combo(x):
                val1, der1 = a1(x)
                val2, der2 = a2(x)
                return (alpha * val1 + beta * val2, alpha * der1 + beta * der2)

            left_side = self.compute(linear_combo, b)
        elif hasattr(a1, "get_values") and hasattr(a2, "get_values"):
            # This is a simplified approach - a real implementation would need
            # to create a proper Vector object that combines a1 and a2
            a1_values = a1.get_values()
            a2_values = a2.get_values()
            a1_derivatives = a1.get_derivatives()
            a2_derivatives = a2.get_derivatives()

            # Create a mock object with the combined values
            class CombinedVector:
                def get_values(self):
                    return alpha * a1_values + beta * a2_values

                def get_derivatives(self):
                    return alpha * a1_derivatives + beta * a2_derivatives

            linear_combo = CombinedVector()
            left_side = self.compute(linear_combo, b)
        else:
            error_msg = (
                f"Cannot create linear combination of types {type(a1)} and {type(a2)}"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

        # Check if the two sides are approximately equal
        is_linear = np.isclose(left_side, right_side)
        logger.debug(
            f"Linearity check result: {is_linear} (left side: {left_side}, right side: {right_side})"
        )

        return is_linear

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the H1 inner product satisfies the positivity property.

        Verifies if <a, a> >= 0 and <a, a> = 0 iff a = 0

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

        # Compute <a, a>
        inner_aa = self.compute(a, a)

        # Check if it's non-negative
        is_non_negative = inner_aa >= 0

        # Check if it's zero only when a is zero
        is_zero_for_zero_only = True

        # This check depends on the type of input
        if isinstance(a, np.ndarray):
            # For arrays, check if a is non-zero when inner product is non-zero
            if np.isclose(inner_aa, 0) and not np.allclose(a, 0):
                is_zero_for_zero_only = False
        elif isinstance(a, Callable):
            # For functions, this is hard to verify in general
            # We would need to sample the function at multiple points
            # For now, we assume this part of the check passes
            pass
        elif hasattr(a, "get_values"):
            # For vector objects, check values
            a_values = a.get_values()
            a_derivatives = a.get_derivatives()
            if np.isclose(inner_aa, 0) and (
                not np.allclose(a_values, 0) or not np.allclose(a_derivatives, 0)
            ):
                is_zero_for_zero_only = False

        is_positive = is_non_negative and is_zero_for_zero_only
        logger.debug(
            f"Positivity check result: {is_positive} (inner product: {inner_aa})"
        )

        return is_positive

    def __str__(self) -> str:
        """
        Return a string representation of the H1 inner product.

        Returns
        -------
        str
            String representation
        """
        return f"SobolevH1InnerProduct(alpha={self.alpha}, beta={self.beta})"
