import logging
from typing import Callable, Literal, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import (
    InnerProductBase,
    Matrix,
    Vector,
)

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    """
    Euclidean Inner Product implementation for real-valued vectors.

    This class implements the standard dot product used in Euclidean geometry
    for real vector spaces. It computes the L2 inner product over real-valued,
    finite-dimensional vectors.

    Attributes
    ----------
    type : Literal["EuclideanInnerProduct"]
        The type identifier for this inner product implementation
    """

    type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the Euclidean inner product (dot product) between two vectors.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first vector for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second vector for inner product calculation

        Returns
        -------
        float
            The inner product value

        Raises
        ------
        ValueError
            If inputs are not compatible for dot product computation
        TypeError
            If inputs are not numeric arrays or vectors
        """
        logger.debug(
            f"Computing Euclidean inner product between {type(a)} and {type(b)}"
        )

        try:
            # Convert inputs to numpy arrays if they aren't already
            a_array = np.array(a) if not isinstance(a, np.ndarray) else a
            b_array = np.array(b) if not isinstance(b, np.ndarray) else b

            # Check if inputs are numeric
            if not np.issubdtype(a_array.dtype, np.number) or not np.issubdtype(
                b_array.dtype, np.number
            ):
                raise TypeError("Input vectors must contain numeric values")

            # Check if inputs are finite
            if not np.all(np.isfinite(a_array)) or not np.all(np.isfinite(b_array)):
                raise ValueError("Input vectors must contain only finite values")

            # Check if inputs have compatible dimensions for dot product
            if a_array.shape != b_array.shape:
                raise ValueError(
                    f"Input vectors must have the same shape. Got {a_array.shape} and {b_array.shape}"
                )

            # Compute the dot product
            result = np.sum(a_array * b_array)
            logger.debug(f"Euclidean inner product result: {result}")
            return float(result)

        except Exception as e:
            logger.error(f"Error computing Euclidean inner product: {str(e)}")
            raise

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the Euclidean inner product satisfies the conjugate symmetry property:
        <a, b> = <b, a> for real vectors.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first vector
        b : Union[Vector, Matrix, Callable]
            The second vector

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug(f"Checking conjugate symmetry for {type(a)} and {type(b)}")

        try:
            # Compute inner products in both directions
            ab_product = self.compute(a, b)
            ba_product = self.compute(b, a)

            # For real vectors, the products should be exactly equal
            is_symmetric = np.isclose(ab_product, ba_product)

            logger.debug(
                f"Conjugate symmetry check result: {is_symmetric} (<a,b>={ab_product}, <b,a>={ba_product})"
            )
            return bool(is_symmetric)

        except Exception as e:
            logger.error(f"Error checking conjugate symmetry: {str(e)}")
            raise

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the Euclidean inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second vector
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
            # Convert inputs to numpy arrays
            a1_array = np.array(a1) if not isinstance(a1, np.ndarray) else a1
            a2_array = np.array(a2) if not isinstance(a2, np.ndarray) else a2

            # Check if a1 and a2 have the same shape
            if a1_array.shape != a2_array.shape:
                raise ValueError(
                    f"a1 and a2 must have the same shape. Got {a1_array.shape} and {a2_array.shape}"
                )

            # Compute left side of the equation: <alpha*a1 + beta*a2, b>
            combined = alpha * a1_array + beta * a2_array
            left_side = self.compute(combined, b)

            # Compute right side of the equation: alpha*<a1, b> + beta*<a2, b>
            right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

            # Check if both sides are equal (within numerical precision)
            is_linear = np.isclose(left_side, right_side)

            logger.debug(
                f"Linearity check result: {is_linear} (left={left_side}, right={right_side})"
            )
            return bool(is_linear)

        except Exception as e:
            logger.error(f"Error checking linearity: {str(e)}")
            raise

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the Euclidean inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The vector to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for {type(a)}")

        try:
            # Convert input to numpy array
            a_array = np.array(a) if not isinstance(a, np.ndarray) else a

            # Compute <a, a>
            self_product = self.compute(a, a)

            # Check if <a, a> >= 0
            is_nonnegative = self_product >= 0

            # Check if <a, a> = 0 iff a = 0
            is_zero_iff_a_zero = (self_product == 0 and np.allclose(a_array, 0)) or (
                self_product > 0 and not np.allclose(a_array, 0)
            )

            result = is_nonnegative and is_zero_iff_a_zero
            logger.debug(
                f"Positivity check result: {result} (self-product={self_product})"
            )
            return result

        except Exception as e:
            logger.error(f"Error checking positivity: {str(e)}")
            raise
