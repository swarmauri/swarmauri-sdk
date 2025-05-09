"""Module implementing the Frobenius real inner product for real matrices."""

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
import numpy as np
import logging

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "FrobeniusRealInnerProduct")
class FrobeniusRealInnerProduct(InnerProductBase):
    """
    A class implementing the Frobenius inner product for real matrices.

    This class provides the functionality to compute the Frobenius inner product
    between two real matrices. The Frobenius inner product is defined as the
    sum of the element-wise products of the two matrices, which is equivalent
    to the trace of the matrix product of the transpose of the first matrix
    with the second matrix.

    Inherits From:
        InnerProductBase: The base class for all inner product implementations.

    Methods:
        compute(a, b): Computes the Frobenius inner product of matrices a and b.
        check_conjugate_symmetry(a, b): Checks if the inner product is conjugate symmetric.
        check_linearity(a, b, c): Checks if the inner product is linear in the first argument.
        check_positivity(a): Checks if the inner product is positive definite.
    """

    def __init__(self):
        super().__init__()
        self.type: Literal["FrobeniusRealInnerProduct"] = "FrobeniusRealInnerProduct"

    def compute(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Computes the Frobenius inner product of two real matrices.

        The Frobenius inner product is computed as the sum of the element-wise
        products of the two matrices. This is equivalent to the trace of the
        matrix product of the transpose of the first matrix with the second matrix.

        Args:
            a: The first real matrix.
            b: The second real matrix.

        Returns:
            A float representing the Frobenius inner product result.

        Raises:
            ValueError: If the input matrices are not of the same shape.
        """
        logger.debug("Computing Frobenius inner product")
        
        # Ensure inputs are numpy arrays
        if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
            raise ValueError("Inputs must be numpy arrays")
            
        # Check if matrices have the same shape
        if a.shape != b.shape:
            raise ValueError("Matrices must have the same shape")
            
        # Compute the Frobenius inner product
        return float(np.trace(np.transpose(a) @ b))

    def check_conjugate_symmetry(self, a: np.ndarray, b: np.ndarray) -> bool:
        """
        Checks if the inner product is conjugate symmetric.

        For real matrices, the Frobenius inner product is symmetric, meaning
        that <a, b> = <b, a>.

        Args:
            a: The first matrix.
            b: The second matrix.

        Returns:
            bool: True if the inner product is conjugate symmetric, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")
        
        # Compute inner products
        inner_product_ab = self.compute(a, b)
        inner_product_ba = self.compute(b, a)
        
        # Check if they are equal
        return np.isclose(inner_product_ab, inner_product_ba)

    def check_linearity(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        This method verifies two properties:
        1. Additivity: <a + c, b> = <a, b> + <c, b>
        2. Homogeneity: <c*a, b> = c*<a, b>

        Args:
            a: The first matrix.
            b: The second matrix.
            c: A scalar for linearity check.

        Returns:
            bool: True if the inner product is linear, False otherwise.
        """
        logger.debug("Checking linearity")
        
        # Additivity check
        add_result = self.compute(a + c, b)
        expected_add = self.compute(a, b) + self.compute(c, b)
        
        # Homogeneity check
        homo_result = self.compute(c * a, b)
        expected_homo = c * self.compute(a, b)
        
        # Check if both conditions are satisfied
        return (np.isclose(add_result, expected_add) and 
                np.isclose(homo_result, expected_homo))

    def check_positivity(self, a: np.ndarray) -> bool:
        """
        Checks if the inner product is positive definite.

        For the Frobenius inner product, this is true if the matrix
        is not the zero matrix.

        Args:
            a: The matrix to check.

        Returns:
            bool: True if the inner product is positive definite, False otherwise.
        """
        logger.debug("Checking positivity")
        
        # Compute the inner product of a with itself
        inner_product = self.compute(a, a)
        
        # The result should be positive if a is not the zero matrix
        return inner_product > 0