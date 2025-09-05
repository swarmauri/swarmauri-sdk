import logging
from typing import Callable, Literal, TypeVar, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Vector = TypeVar("Vector", bound="IVector")
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplexInnerProduct")
class FrobeniusComplexInnerProduct(InnerProductBase):
    """
    Frobenius inner product implementation for complex matrices.

    This class implements the Frobenius inner product for complex matrices,
    which is defined as <A, B> = Tr(A* B), where A* is the conjugate transpose
    of A and Tr denotes the trace operation.

    The Frobenius inner product satisfies all inner product properties including
    conjugate symmetry, linearity in the first argument, and positivity.

    Attributes
    ----------
    type : Literal["FrobeniusComplexInnerProduct"]
        The specific type identifier for this inner product implementation
    """

    type: Literal["FrobeniusComplexInnerProduct"] = "FrobeniusComplexInnerProduct"

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the Frobenius inner product between two matrices.

        For complex matrices A and B, computes Tr(A* B) where A* is the conjugate
        transpose of A and Tr is the trace operation.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first matrix for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second matrix for inner product calculation

        Returns
        -------
        float
            The inner product value

        Raises
        ------
        TypeError
            If inputs are not matrices or cannot be converted to matrices
        ValueError
            If matrix dimensions are incompatible
        """
        logger.debug(
            f"Computing Frobenius inner product between {type(a)} and {type(b)}"
        )

        try:
            # Convert inputs to numpy arrays if they aren't already
            a_matrix = np.array(a, dtype=complex)
            b_matrix = np.array(b, dtype=complex)

            # Check if dimensions match
            if a_matrix.shape != b_matrix.shape:
                raise ValueError(
                    f"Matrix dimensions don't match: {a_matrix.shape} vs {b_matrix.shape}"
                )

            # Compute the inner product: Tr(A* B)
            # This is equivalent to sum(conj(a_ij) * b_ij) over all elements
            result = np.sum(np.conjugate(a_matrix) * b_matrix)

            logger.debug(f"Frobenius inner product result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error computing Frobenius inner product: {str(e)}")
            raise

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the Frobenius inner product satisfies the conjugate symmetry property:
        <a, b> = conj(<b, a>).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first matrix
        b : Union[Vector, Matrix, Callable]
            The second matrix

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug(f"Checking conjugate symmetry for {type(a)} and {type(b)}")

        try:
            # Compute <a, b>
            ab_inner = self.compute(a, b)

            # Compute <b, a> and take conjugate
            ba_inner_conj = np.conjugate(self.compute(b, a))

            # Check if they're equal within numerical precision
            is_symmetric = np.isclose(ab_inner, ba_inner_conj)

            logger.debug(f"Conjugate symmetry check result: {is_symmetric}")
            logger.debug(f"<a,b> = {ab_inner}, conj(<b,a>) = {ba_inner_conj}")

            return is_symmetric

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
        Check if the Frobenius inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
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
        logger.debug(
            f"Checking linearity in first argument with alpha={alpha}, beta={beta}"
        )

        try:
            # Convert inputs to numpy arrays
            a1_matrix = np.array(a1, dtype=complex)
            a2_matrix = np.array(a2, dtype=complex)
            b_matrix = np.array(b, dtype=complex)

            # Check dimensions
            if a1_matrix.shape != a2_matrix.shape or a1_matrix.shape != b_matrix.shape:
                raise ValueError("Matrix dimensions don't match")

            # Compute left side: <alpha*a1 + beta*a2, b>
            combined = alpha * a1_matrix + beta * a2_matrix
            left_side = self.compute(combined, b_matrix)

            # Compute right side: alpha*<a1, b> + beta*<a2, b>
            right_side = alpha * self.compute(
                a1_matrix, b_matrix
            ) + beta * self.compute(a2_matrix, b_matrix)

            # Check if they're equal within numerical precision
            is_linear = np.isclose(left_side, right_side)

            logger.debug(f"Linearity check result: {is_linear}")
            logger.debug(f"Left side: {left_side}, Right side: {right_side}")

            return is_linear

        except Exception as e:
            logger.error(f"Error checking linearity: {str(e)}")
            raise

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the Frobenius inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The matrix to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        logger.debug(f"Checking positivity for {type(a)}")

        try:
            a_matrix = np.array(a, dtype=complex)

            # Compute <a, a>
            inner_product = self.compute(a_matrix, a_matrix)

            # For complex matrices, the inner product should be a real number >= 0
            is_real = np.isclose(inner_product.imag, 0)
            is_nonnegative = inner_product.real >= 0

            # Check if <a, a> = 0 iff a = 0
            is_zero_iff_a_zero = not np.isclose(inner_product, 0) or np.allclose(
                a_matrix, 0
            )

            result = is_real and is_nonnegative and is_zero_iff_a_zero

            logger.debug(f"Positivity check result: {result}")
            logger.debug(
                f"<a,a> = {inner_product}, is_real: {is_real}, is_nonnegative: {is_nonnegative}"
            )
            logger.debug(f"Zero iff a is zero: {is_zero_iff_a_zero}")

            return result

        except Exception as e:
            logger.error(f"Error checking positivity: {str(e)}")
            raise

    def norm(self, a: Union[Vector, Matrix, Callable]) -> float:
        """
        Compute the Frobenius norm of a matrix.

        For a matrix A, the Frobenius norm is defined as sqrt(<A, A>).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The matrix to compute the norm for

        Returns
        -------
        float
            The Frobenius norm value
        """
        logger.debug(f"Computing Frobenius norm for {type(a)}")

        try:
            # Compute sqrt(<a, a>)
            inner_product = self.compute(a, a)

            # The inner product should be real and non-negative
            if not np.isclose(inner_product.imag, 0) or inner_product.real < 0:
                raise ValueError("Inner product <a,a> must be real and non-negative")

            norm_value = np.sqrt(inner_product.real)

            logger.debug(f"Frobenius norm result: {norm_value}")
            return norm_value

        except Exception as e:
            logger.error(f"Error computing Frobenius norm: {str(e)}")
            raise
