from typing import Union, Literal
import numpy as np
import logging

# Define logger
logger = logging.getLogger(__name__)

from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplexInnerProduct")
class FrobeniusComplexInnerProduct(InnerProductBase):
    """
    A class that implements the Frobenius inner product for complex matrices.

    This class provides functionality to compute the Frobenius inner product, which is
    based on the trace of the product of the conjugate transpose of the first matrix
    and the second matrix. It inherits from the InnerProductBase class and implements
    the required methods for computing and validating the inner product properties.

    Attributes:
        type: Literal["FrobeniusComplexInnerProduct"] = "FrobeniusComplexInnerProduct"
            The type identifier for this inner product implementation.

    Methods:
        compute: Computes the Frobenius inner product between two complex matrices.
        check_conjugate_symmetry: Verifies the conjugate symmetry property of the inner product.
        check_linearity_first_argument: Checks if the inner product is linear in the first argument.
        check_positivity: Validates the positive definiteness of the inner product.
    """

    type: Literal["FrobeniusComplexInnerProduct"] = "FrobeniusComplexInnerProduct"

    def compute(
        self, a: Union[np.ndarray, object], b: Union[np.ndarray, object]
    ) -> Union[float, complex]:
        """
        Computes the Frobenius inner product between two complex matrices.

        The Frobenius inner product is computed as the trace of the product of the
        conjugate transpose of the first matrix and the second matrix. This is
        equivalent to summing the element-wise products of the matrices.

        Args:
            a: The first complex matrix.
            b: The second complex matrix.

        Returns:
            Union[float, complex]: The result of the Frobenius inner product computation.

        Raises:
            ValueError: If the input matrices are not compatible for the inner product computation.
        """
        logger.debug("Computing Frobenius inner product for complex matrices")

        # Ensure inputs are numpy arrays
        if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
            raise ValueError("Inputs must be numpy arrays")

        # Compute the conjugate transpose of matrix a
        a_conj_transpose = a.conj().T

        # Compute the product of a_conj_transpose and b
        product_matrix = a_conj_transpose @ b

        # Compute the trace of the product matrix
        trace = np.trace(product_matrix)

        logger.debug(f"Frobenius inner product result: {trace}")
        return trace

    def check_conjugate_symmetry(
        self, a: Union[np.ndarray, object], b: Union[np.ndarray, object]
    ) -> bool:
        """
        Checks if the inner product satisfies conjugate symmetry.

        Conjugate symmetry requires that <a, b> = conj(<b, a>). This method computes
        both inner products and checks for their conjugate symmetry.

        Args:
            a: The first element to check.
            b: The second element to check.

        Returns:
            bool: True if conjugate symmetry holds, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")

        # Compute <a, b>
        inner_product_ab = self.compute(a, b)

        # Compute <b, a> and take its conjugate
        inner_product_ba = self.compute(b, a)
        inner_product_ba_conj = np.conj(inner_product_ba)

        # Check if <a, b> equals the conjugate of <b, a>
        return np.isclose(inner_product_ab, inner_product_ba_conj)

    def check_linearity_first_argument(
        self,
        a: Union[np.ndarray, object],
        b: Union[np.ndarray, object],
        c: Union[np.ndarray, object],
    ) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        Linearity in the first argument requires that for any matrices a, b, c and
        scalar k, <a + c, b> = <a, b> + <c, b> and <k*a, b> = k*<a, b>.

        Args:
            a: The first matrix for linearity check.
            b: The second matrix for linearity check.
            c: The third matrix for linearity check.

        Returns:
            bool: True if linearity in the first argument holds, False otherwise.
        """
        logger.debug("Checking linearity in the first argument")

        # Test additivity: <a + c, b> = <a, b> + <c, b>
        additivity_result = self.compute(a + c, b)
        expected_additivity = self.compute(a, b) + self.compute(c, b)

        # Test homogeneity: <k*a, b> = k*<a, b> for some scalar k
        # Choose k = 2.0 for testing
        k = 2.0
        homogeneity_result = self.compute(k * a, b)
        expected_homogeneity = k * self.compute(a, b)

        # Check both conditions
        return np.isclose(additivity_result, expected_additivity) and np.isclose(
            homogeneity_result, expected_homogeneity
        )

    def check_positivity(self, a: Union[np.ndarray, object]) -> bool:
        """
        Checks if the inner product satisfies positive definiteness.

        Positive definiteness requires that for any non-zero matrix a, <a, a> > 0.
        For the zero matrix, <a, a> = 0.

        Args:
            a: The matrix to check for positivity.

        Returns:
            bool: True if positivity holds, False otherwise.
        """
        logger.debug("Checking positivity")

        # Compute <a, a>
        inner_product_aa = self.compute(a, a)

        # Check if the result is positive (and not zero for non-zero a)
        if np.allclose(a, np.zeros_like(a)):
            return inner_product_aa == 0
        else:
            return inner_product_aa > 0
