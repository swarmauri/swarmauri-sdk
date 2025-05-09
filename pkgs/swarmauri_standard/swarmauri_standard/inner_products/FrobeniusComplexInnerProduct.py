from typing import Callable, Union, Literal
import numpy as np
import logging

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplexInnerProduct")
class FrobeniusComplexInnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of the Frobenius inner product for complex matrices.
    Inherits from the InnerProductBase class and implements the compute method
    to calculate the trace-based inner product with conjugate symmetry.

    The Frobenius inner product is defined as the trace of the product of one matrix
    with the conjugate transpose of the other. It is a commonly used inner product
    for complex matrices and ensures conjugate symmetry.
    """

    type: Literal["FrobeniusComplexInnerProduct"] = "FrobeniusComplexInnerProduct"

    def __init__(self) -> None:
        """
        Initializes the FrobeniusComplexInnerProduct instance.
        """
        super().__init__()
        logger.debug("FrobeniusComplexInnerProduct instance initialized")

    def compute(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> float:
        """
        Computes the Frobenius inner product between two complex matrices.

        The Frobenius inner product is defined as:
        <A, B> = trace(A * B^H)
        where B^H is the conjugate transpose of B.

        Args:
            a: The first complex matrix (numpy.ndarray or IVector)
            b: The second complex matrix (numpy.ndarray or IVector)

        Returns:
            float: The result of the Frobenius inner product operation.

        Raises:
            ValueError: If the input matrices are not compatible for multiplication
            ZeroDivisionError: If any operation leads to division by zero
        """
        logger.debug("Computing Frobenius inner product")

        # Ensure inputs are numpy arrays
        if not isinstance(a, np.ndarray):
            a = a.to_numpy()
        if not isinstance(b, np.ndarray):
            b = b.to_numpy()

        # Check if matrices can be multiplied
        if a.shape[1] != b.shape[0]:
            raise ValueError("Incompatible dimensions for matrix multiplication")

        # Compute conjugate transpose of b
        b_conj_transpose = b.conj().T

        # Compute element-wise product and trace
        product = np.multiply(a, b_conj_transpose)
        trace = np.trace(product)

        return float(trace)

    def check_conjugate_symmetry(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the conjugate symmetry property for the Frobenius inner product.

        For complex matrices A and B, the inner product should satisfy:
        <A, B> = conjugate(<B, A>)

        Args:
            a: The first complex matrix
            b: The second complex matrix

        Raises:
            ValueError: If conjugate symmetry is not satisfied
        """
        logger.debug("Checking conjugate symmetry")

        # Compute inner products
        inner_ab = self.compute(a, b)
        inner_ba = self.compute(b, a)

        # Check conjugate symmetry
        if not np.isclose(inner_ab, inner_ba.conjugate(), rtol=1e-4):
            raise ValueError("Conjugate symmetry not satisfied")

    def check_linearity_first_argument(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
        c: Union[IVector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the linearity property in the first argument of the inner product.

        For complex matrices A, B, C and scalar α:
        - Linearity: <A + B, C> = <A, C> + <B, C>
        - Homogeneity: <αA, C> = α <A, C>

        Args:
            a: The first complex matrix
            b: The second complex matrix
            c: The third complex matrix

        Raises:
            ValueError: If linearity in the first argument is not satisfied
        """
        logger.debug("Checking linearity in first argument")

        # Test linearity: <a + b, c> = <a, c> + <b, c>
        ab = a + b
        inner_ab_c = self.compute(ab, c)
        inner_a_c = self.compute(a, c)
        inner_b_c = self.compute(b, c)

        if not np.isclose(inner_ab_c, inner_a_c + inner_b_c, rtol=1e-4):
            raise ValueError("Linearity in first argument not satisfied")

        # Test homogeneity: <αa, c> = α <a, c>
        alpha = 2.0
        a_scaled = alpha * a
        inner_scaled = self.compute(a_scaled, c)
        expected = alpha * inner_a_c

        if not np.isclose(inner_scaled, expected, rtol=1e-4):
            raise ValueError("Homogeneity in first argument not satisfied")

    def check_positivity(self, a: Union[IVector, np.ndarray, Callable]) -> None:
        """
        Verifies the positivity property of the inner product.

        For any non-zero complex matrix A:
        - <A, A> > 0

        Args:
            a: The complex matrix to check for positivity

        Raises:
            ValueError: If the positivity property is not satisfied
        """
        logger.debug("Checking positivity")

        inner_aa = self.compute(a, a)

        if inner_aa <= 0:
            raise ValueError(
                f"Positivity not satisfied. Inner product <a, a> = {inner_aa}"
            )
