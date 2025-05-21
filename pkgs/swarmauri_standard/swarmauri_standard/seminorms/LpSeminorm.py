import logging
import math
from typing import Literal

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import InputType, T
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "LpSeminorm")
class LpSeminorm(SeminormBase):
    """
    Non-point-separating variant of Lp norm.

    Computes an Lp-like seminorm that might not distinguish all vectors.
    Unlike a true norm, a seminorm can assign zero to non-zero vectors.

    The Lp seminorm is defined as:
    ||x||_p = (sum_i |x_i|^p)^(1/p) for p in (0, ∞)

    Attributes
    ----------
    type : Literal["LpSeminorm"]
        The type identifier for this component
    p : float
        The parameter p for the Lp seminorm (must be in (0, ∞))
    epsilon : float
        Small value used for numerical stability
    """

    type: Literal["LpSeminorm"] = "LpSeminorm"
    p: float = 2.0
    epsilon: float = 1e-10

    def __init__(self, p: float = 2.0, epsilon: float = 1e-10, **kwargs):
        """
        Initialize an Lp seminorm with the given p value.

        Parameters
        ----------
        p : float, optional
            The parameter p for the Lp seminorm, by default 2.0
        epsilon : float, optional
            Small value used for numerical stability, by default 1e-10

        Raises
        ------
        ValueError
            If p is not in the range (0, ∞)
        """
        super().__init__(**kwargs)

        if p <= 0:
            raise ValueError(f"Parameter p must be positive, got {p}")

        self.p = p
        self.epsilon = epsilon
        logger.info(f"Initialized LpSeminorm with p={p}")

    def _convert_to_array(self, x: InputType) -> np.ndarray:
        """
        Convert input to a numpy array for computation.

        Parameters
        ----------
        x : InputType
            The input to convert

        Returns
        -------
        np.ndarray
            The converted input as a numpy array

        Raises
        ------
        TypeError
            If the input type is not supported
        """
        if isinstance(x, IVector):
            return np.array(x.to_array())
        elif isinstance(x, IMatrix):
            return np.array(x.to_array())
        elif isinstance(x, (list, tuple, np.ndarray)):
            # Don't force dtype=float which discards imaginary parts
            return np.array(x)
        elif isinstance(x, str):
            # Convert string to array of character codes
            return np.array([ord(c) for c in x], dtype=float)
        elif callable(x):
            # For callable objects, we cannot compute a seminorm directly
            raise TypeError("Cannot compute Lp seminorm for callable objects")
        else:
            try:
                # Try to convert to array as a last resort
                return np.array(x)
            except Exception:
                raise TypeError(f"Unsupported input type for LpSeminorm: {type(x)}")

    def compute(self, x: InputType) -> float:
        """
        Compute the Lp seminorm of the input.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for

        Returns
        -------
        float
            The Lp seminorm value

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the computation cannot be performed on the given input
        """
        logger.debug(
            f"Computing Lp seminorm with p={self.p} for input of type {type(x)}"
        )

        try:
            arr = self._convert_to_array(x)

            if np.iscomplexobj(arr):
                arr = np.abs(arr)

            # Handle special cases for common p values
            if math.isclose(self.p, 1.0):
                return float(np.sum(np.abs(arr)))
            elif math.isclose(self.p, 2.0):
                return float(np.sqrt(np.sum(np.abs(arr) ** 2)))
            else:
                # General case for any p
                return float(np.sum(np.abs(arr) ** self.p) ** (1.0 / self.p))

        except Exception as e:
            logger.error(f"Error computing Lp seminorm: {str(e)}")
            raise

    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        The triangle inequality states that:
        ||x + y|| ≤ ||x|| + ||y||

        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check

        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise

        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the check cannot be performed on the given inputs
        """
        logger.debug(
            f"Checking triangle inequality for inputs of types {type(x)} and {type(y)}"
        )

        try:
            x_arr = self._convert_to_array(x)
            y_arr = self._convert_to_array(y)

            if x_arr.shape != y_arr.shape:
                raise ValueError(
                    f"Inputs must have the same shape: {x_arr.shape} vs {y_arr.shape}"
                )

            # Compute the seminorm of x + y
            sum_seminorm = self.compute(x_arr + y_arr)

            # Compute the seminorm of x and y separately
            x_seminorm = self.compute(x_arr)
            y_seminorm = self.compute(y_arr)

            # Check the triangle inequality with a small epsilon for numerical stability
            return sum_seminorm <= x_seminorm + y_seminorm + self.epsilon

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            raise

    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        The scalar homogeneity states that:
        ||αx|| = |α|·||x||

        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by

        Returns
        -------
        bool
            True if scalar homogeneity holds, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        """
        logger.debug(
            f"Checking scalar homogeneity for input of type {type(x)} with scalar {alpha}"
        )

        try:
            x_arr = self._convert_to_array(x)

            # Convert alpha to a complex number to handle different types
            alpha_complex = complex(alpha)
            alpha_abs = abs(alpha_complex)

            # Compute ||αx||
            scaled_seminorm = self.compute(alpha_complex * x_arr)

            # Compute |α|·||x||
            x_seminorm = self.compute(x_arr)
            expected_scaled_seminorm = alpha_abs * x_seminorm

            # Check scalar homogeneity with a small epsilon for numerical stability
            return abs(scaled_seminorm - expected_scaled_seminorm) <= self.epsilon * (
                1 + expected_scaled_seminorm
            )

        except Exception as e:
            logger.error(f"Error checking scalar homogeneity: {str(e)}")
            raise
