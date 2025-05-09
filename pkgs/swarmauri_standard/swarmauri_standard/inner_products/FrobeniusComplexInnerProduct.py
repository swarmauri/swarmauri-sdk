"""Module implementing the Frobenius inner product for complex matrices."""

from typing import Literal
import numpy as np
import logging

from swarmauri_base.inner_products import InnerProductBase

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplexInnerProduct")
class FrobeniusComplexInnerProduct(InnerProductBase):
    """
    Class implementing the Frobenius inner product for complex matrices.

    This class provides functionality to compute the Frobenius inner product
    for complex matrices, which is based on the trace of the product of matrices.
    The implementation ensures conjugate symmetry and handles complex numbers
    appropriately.

    Methods:
        compute(a, b): Computes the inner product of matrices a and b.
        check_conjugate_symmetry(a, b): Checks if the inner product is conjugate symmetric.
        check_linearity(a, b, c): Checks if the inner product is linear in the first argument.
        check_positivity(a): Checks if the inner product is positive definite.
    """

    type: Literal["FrobeniusComplexInnerProduct"] = "FrobeniusComplexInnerProduct"

    def __init__(self) -> None:
        """
        Initializes the FrobeniusComplexInnerProduct instance.
        """
        super().__init__()
        logger.debug("FrobeniusComplexInnerProduct instance initialized")

    def compute(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Computes the Frobenius inner product of two complex matrices.

        The Frobenius inner product is defined as the sum of the element-wise
        products of the conjugate of the second matrix with the first matrix.
        Mathematically, it is equivalent to trace(A^* @ B), where A and B
        are complex matrices.

        Args:
            a: The first complex matrix.
            b: The second complex matrix.

        Returns:
            A float representing the Frobenius inner product result.

        Raises:
            ValueError: If the input matrices are not of compatible shapes.
        """
        logger.debug("Computing Frobenius inner product")
        
        # Ensure matrices are numpy arrays
        a = np.asarray(a)
        b = np.asarray(b)
        
        # Check if matrices can be multiplied element-wise
        if a.shape != b.shape:
            logger.error("Input matrices must have the same shape")
            raise ValueError("Input matrices must have the same shape")
        
        # Compute element-wise product and sum
        product = a * b.conj()
        result = np.sum(product)
        
        # Return the real part to ensure a real-valued inner product
        return np.real(result)

    def check_conjugate_symmetry(self, a: np.ndarray, b: np.ndarray) -> bool:
        """
        Checks if the inner product is conjugate symmetric.

        This method verifies if <a, b> = <b, a>*,
        where * denotes the complex conjugate.

        Args:
            a: The first complex matrix.
            b: The second complex matrix.

        Returns:
            bool: True if the inner product is conjugate symmetric, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")
        
        # Compute <a, b>
        inner_ab = self.compute(a, b)
        
        # Compute <b, a>
        inner_ba = self.compute(b, a)
        
        # Check if <a, b> is the conjugate of <b, a>
        return np.isclose(inner_ab, inner_ba.conjugate())

    def check_linearity(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        This method verifies two properties:
        1. <a + c, b> = <a, b> + <c, b>
        2. <c * a, b> = c * <a, b>

        Args:
            a: The first complex matrix.
            b: The second complex matrix.
            c: A complex scalar.

        Returns:
            bool: True if the inner product is linear, False otherwise.
        """
        logger.debug("Checking linearity")
        
        # Test linearity: <a + c, b> = <a, b> + <c, b>
        a_plus_c = a + c
        inner_a_plus_c_b = self.compute(a_plus_c, b)
        inner_a_b = self.compute(a, b)
        inner_c_b = self.compute(c, b)
        
        # Check if the two results are close
        is_linear_add = np.isclose(inner_a_plus_c_b, inner_a_b + inner_c_b)
        
        # Test scalar multiplication: <c * a, b> = c * <a, b>
        c_times_a = c * a
        inner_c_a_b = self.compute(c_times_a, b)
        c_times_inner_a_b = c * inner_a_b
        
        is_linear_scale = np.isclose(inner_c_a_b, c_times_inner_a_b)
        
        return is_linear_add and is_linear_scale

    def check_positivity(self, a: np.ndarray) -> bool:
        """
        Checks if the inner product is positive definite.

        For the Frobenius inner product, this is always true except
        when the matrix is the zero matrix.

        Args:
            a: The complex matrix to check.

        Returns:
            bool: True if the inner product is positive definite, False otherwise.
        """
        logger.debug("Checking positivity")
        
        # Compute the inner product of a with itself
        inner_aa = self.compute(a, a)
        
        # The result should be positive unless a is the zero matrix
        return inner_aa > 0.0