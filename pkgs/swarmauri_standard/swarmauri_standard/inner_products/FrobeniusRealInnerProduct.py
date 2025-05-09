import logging
import numpy as np

from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Define logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(InnerProductBase, "FrobeniusRealInnerProduct")
class FrobeniusRealInnerProduct(InnerProductBase):
    """
    A concrete implementation of the InnerProductBase class for computing the Frobenius inner product
    for real matrices. The Frobenius inner product is defined as the sum of the element-wise products
    of the matrices, which is equivalent to the trace of the matrix product of the transpose of the
    first matrix and the second matrix.

    Attributes:
        type (Literal["FrobeniusRealInnerProduct"]): The type identifier for this inner product implementation.
    """

    type: Literal["FrobeniusRealInnerProduct"] = "FrobeniusRealInnerProduct"

    def __init__(self) -> None:
        """
        Initializes the FrobeniusRealInnerProduct instance.
        """
        super().__init__()
        logger.debug("FrobeniusRealInnerProduct instance initialized")

    def compute(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Computes the Frobenius inner product between two real matrices.

        Args:
            a: The first real matrix
            b: The second real matrix

        Returns:
            float: The result of the Frobenius inner product computation

        Raises:
            ValueError: If the input matrices are not real or have different shapes
        """
        if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
            raise ValueError("Inputs must be numpy arrays")
        if a.dtype.kind not in ('f', 'i') or b.dtype.kind not in ('f', 'i'):
            raise ValueError("Matrices must be real")
        if a.shape != b.shape:
            raise ValueError("Matrices must have the same shape")

        # Compute element-wise product and sum all elements
        inner_product = np.sum(a * b)
        logger.debug(f"Computed Frobenius inner product: {inner_product}")
        return inner_product

    def check_conjugate_symmetry(self, a: np.ndarray, b: np.ndarray) -> bool:
        """
        Checks if the inner product implementation satisfies conjugate symmetry.

        For real matrices, the Frobenius inner product is symmetric, meaning
        <a, b> = <b, a>.

        Args:
            a: The first matrix
            b: The second matrix

        Returns:
            bool: True if conjugate symmetry holds, False otherwise
        """
        return self.compute(a, b) == self.compute(b, a)

    def check_linearity_first_argument(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """
        Checks if the inner product implementation is linear in the first argument.

        This method verifies that for any matrices a, b, c and scalar k:
        <a + c, b> = <a, b> + <c, b>
        <k*a, b> = k*<a, b>

        Args:
            a: The first matrix
            b: The second matrix
            c: The third matrix

        Returns:
            bool: True if linearity in the first argument holds, False otherwise
        """
        # Check linearity for addition
        add_result = self.compute(a + c, b)
        linear_add = self.compute(a, b) + self.compute(c, b)
        if not np.isclose(add_result, linear_add):
            return False

        # Check linearity for scalar multiplication
        scalar = 2.0
        scaled_a = scalar * a
        mult_result = self.compute(scaled_a, b)
        linear_mult = scalar * self.compute(a, b)
        if not np.isclose(mult_result, linear_mult):
            return False

        return True

    def check_linearity_second_argument(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
        """
        Checks if the inner product implementation is linear in the second argument.

        This method verifies that for any matrices a, b, c and scalar k:
        <a, b + c> = <a, b> + <a, c>
        <a, k*b> = k*<a, b>

        Args:
            a: The first matrix
            b: The second matrix
            c: The third matrix

        Returns:
            bool: True if linearity in the second argument holds, False otherwise
        """
        # Check linearity for addition
        add_result = self.compute(a, b + c)
        linear_add = self.compute(a, b) + self.compute(a, c)
        if not np.isclose(add_result, linear_add):
            return False

        # Check linearity for scalar multiplication
        scalar = 2.0
        scaled_b = scalar * b
        mult_result = self.compute(a, scaled_b)
        linear_mult = scalar * self.compute(a, b)
        if not np.isclose(mult_result, linear_mult):
            return False

        return True

    def check_positivity(self, a: np.ndarray) -> bool:
        """
        Checks if the inner product implementation satisfies positive definiteness.

        For the Frobenius inner product, this is true if the result of compute(a, a)
        is positive for all non-zero matrices a.

        Args:
            a: The matrix to check for positivity

        Returns:
            bool: True if the inner product is positive definite, False otherwise
        """
        value = self.compute(a, a)
        return value > 0