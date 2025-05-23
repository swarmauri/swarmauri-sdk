import logging
from typing import Literal, TypeVar, Union

import numpy as np
from numpy.typing import NDArray
from swarmauri_core.vectors.IVector import IVector
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Configure logging
logger = logging.getLogger(__name__)

Vector = TypeVar("Vector", bound=IVector)
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "FrobeniusRealInnerProduct")
class FrobeniusRealInnerProduct(InnerProductBase):
    """
    Implementation of the Frobenius inner product for real-valued matrices.

    The Frobenius inner product is defined as the sum of element-wise products
    of two matrices, which is equivalent to Tr(A^T B) for real matrices.

    Attributes
    ----------
    type : Literal["FrobeniusRealInnerProduct"]
        The specific type identifier for this inner product implementation
    """

    type: Literal["FrobeniusRealInnerProduct"] = "FrobeniusRealInnerProduct"

    def compute(self, a: Union[NDArray, Matrix], b: Union[NDArray, Matrix]) -> float:
        """
        Compute the Frobenius inner product between two real matrices.

        The Frobenius inner product is defined as the sum of element-wise products,
        which is equivalent to Tr(A^T B) for real matrices.

        Parameters
        ----------
        a : Union[NDArray, Matrix]
            The first matrix for inner product calculation
        b : Union[NDArray, Matrix]
            The second matrix for inner product calculation

        Returns
        -------
        float
            The Frobenius inner product value

        Raises
        ------
        ValueError
            If inputs are not matrices, are not real, or have different shapes
        """
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise ValueError("Both inputs must be numpy arrays (matrices)")

        logger.debug(
            f"Computing Frobenius inner product between matrices of shape {a.shape} and {b.shape}"
        )

        if a.shape != b.shape:
            raise ValueError(f"Matrix shapes must match: {a.shape} != {b.shape}")

        if np.iscomplexobj(a) or np.iscomplexobj(b):
            raise ValueError("This implementation only supports real-valued matrices")

        # Compute the Frobenius inner product
        # For real matrices, this is equivalent to np.sum(a * b) or np.trace(a.T @ b)
        result = np.sum(a * b)

        logger.debug(f"Frobenius inner product result: {result}")
        return float(result)

    def check_conjugate_symmetry(
        self, a: Union[NDArray, Matrix], b: Union[NDArray, Matrix]
    ) -> bool:
        """
        Check if the Frobenius inner product satisfies conjugate symmetry property.

        For real matrices, this simplifies to checking if <a,b> = <b,a>.

        Parameters
        ----------
        a : Union[NDArray, Matrix]
            The first matrix
        b : Union[NDArray, Matrix]
            The second matrix

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug(
            f"Checking conjugate symmetry for matrices of shape {a.shape} and {b.shape}"
        )

        # For real matrices, conjugate symmetry means <a,b> = <b,a>
        forward = self.compute(a, b)
        backward = self.compute(b, a)

        # Check if the values are close enough (floating point comparison)
        is_symmetric = np.isclose(forward, backward)

        logger.debug(
            f"Conjugate symmetry check result: {is_symmetric} ({forward} vs {backward})"
        )
        return bool(is_symmetric)

    def check_linearity_first_argument(
        self,
        a1: Union[NDArray, Matrix],
        a2: Union[NDArray, Matrix],
        b: Union[NDArray, Matrix],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the Frobenius inner product satisfies linearity in the first argument.

        This checks if <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[NDArray, Matrix]
            First component of the first argument
        a2 : Union[NDArray, Matrix]
            Second component of the first argument
        b : Union[NDArray, Matrix]
            The second matrix
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise
        """
        logger.debug(f"Checking linearity with alpha={alpha}, beta={beta}")

        # Validate that all matrices have the same shape
        if a1.shape != a2.shape or a1.shape != b.shape:
            raise ValueError("All matrices must have the same shape")

        # Compute the left side: <alpha*a1 + beta*a2, b>
        left_side = self.compute(alpha * a1 + beta * a2, b)

        # Compute the right side: alpha*<a1, b> + beta*<a2, b>
        right_side = alpha * self.compute(a1, b) + beta * self.compute(a2, b)

        # Check if the values are close enough (floating point comparison)
        is_linear = np.isclose(left_side, right_side)

        logger.debug(
            f"Linearity check result: {is_linear} ({left_side} vs {right_side})"
        )
        return bool(is_linear)

    def check_positivity(self, a: Union[NDArray, Matrix]) -> bool:
        """
        Check if the Frobenius inner product satisfies the positivity property.

        This checks if <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[NDArray, Matrix]
            The matrix to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for matrix of shape {a.shape}")

        # Compute <a, a>
        inner_product = self.compute(a, a)

        # Check if inner product is non-negative
        is_non_negative = inner_product >= 0

        # Check if inner product is zero iff a is zero
        is_zero_iff_a_zero = (inner_product == 0 and np.all(a == 0)) or (
            inner_product > 0 and not np.all(a == 0)
        )

        result = is_non_negative and is_zero_iff_a_zero

        logger.debug(
            f"Positivity check result: {result} (inner product: {inner_product})"
        )
        return result
