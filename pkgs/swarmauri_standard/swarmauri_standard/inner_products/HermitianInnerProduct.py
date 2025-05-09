from typing import Union, Literal
import logging
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Define logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """A concrete implementation of InnerProductBase for Hermitian inner products.

    This class handles complex inner products with Hermitian symmetry. It supports
    conjugate symmetry and L2 structure for complex vectors.
    """

    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"

    def __init__(self):
        """Initializes the HermitianInnerProduct instance."""
        super().__init__()
        self._vector_type = Union[np.ndarray, complex]

    def compute(
        self, a: Union[np.ndarray, complex], b: Union[np.ndarray, complex]
    ) -> Union[float, complex]:
        """Computes the Hermitian inner product between two complex vectors.

        The Hermitian inner product is defined as the conjugate of the transpose of
        the first vector multiplied by the second vector.

        Args:
            a: The first complex vector
            b: The second complex vector

        Returns:
            Union[float, complex]: The result of the Hermitian inner product computation

        Raises:
            ValueError: If the input vectors are not of the correct type
        """
        logger.debug("Computing Hermitian inner product")

        if not isinstance(a, (np.ndarray, complex)) or not isinstance(
            b, (np.ndarray, complex)
        ):
            logger.error("Input vectors must be complex or numpy arrays")
            raise ValueError("Input vectors must be complex or numpy arrays")

        # Compute the Hermitian inner product using numpy's vdot
        result = np.vdot(a, b)

        logger.debug(f"Inner product result: {result}")
        return result

    def check_conjugate_symmetry(
        self, a: Union[np.ndarray, complex], b: Union[np.ndarray, complex]
    ) -> bool:
        """Checks if the inner product implementation satisfies conjugate symmetry.

        Conjugate symmetry means that <a, b> = conjugate(<b, a>).

        Args:
            a: The first complex vector
            b: The second complex vector

        Returns:
            bool: True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry")

        inner_product_ab = self.compute(a, b)
        inner_product_ba = self.compute(b, a)

        # Check if inner_product_ab is equal to the conjugate of inner_product_ba
        return np.isclose(inner_product_ab, np.conj(inner_product_ba))

    def check_linearity_first_argument(
        self,
        a: Union[np.ndarray, complex],
        b: Union[np.ndarray, complex],
        c: Union[np.ndarray, complex],
    ) -> bool:
        """Checks if the inner product is linear in the first argument.

        Linearity in the first argument means that the inner product of (c * a + b)
        with another vector should equal c * <a, vector> + <b, vector>.

        Args:
            a: The first complex vector
            b: The second complex vector
            c: The scalar coefficient

        Returns:
            bool: True if linearity in the first argument holds, False otherwise
        """
        logger.debug("Checking linearity in first argument")

        # Compute <c*a + b, a>
        left_side = self.compute(c * a + b, a)

        # Compute c*<a, a> + <b, a>
        right_side = c * self.compute(a, a) + self.compute(b, a)

        return np.isclose(left_side, right_side)

    def check_positivity(self, a: Union[np.ndarray, complex]) -> bool:
        """Checks if the inner product satisfies positive definiteness.

        Positive definiteness means that the inner product of a vector with itself
        is positive and only zero if the vector is the zero vector.

        Args:
            a: The complex vector to check

        Returns:
            bool: True if positive definiteness holds, False otherwise
        """
        logger.debug("Checking positivity")

        inner_product = self.compute(a, a)

        # Ensure the result is a real positive number
        if not np.isscalar(inner_product) or inner_product.dtype != np.float64:
            return False

        return inner_product > 0
