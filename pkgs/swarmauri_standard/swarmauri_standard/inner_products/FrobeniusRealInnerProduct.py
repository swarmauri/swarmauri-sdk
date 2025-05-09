from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
import logging
import numpy as np

logger = logging.getLogger(__name__)


@InnerProductBase.register_type(IInnerProduct, "FrobeniusRealInnerProduct")
class FrobeniusRealInnerProduct(InnerProductBase):
    """Implementation of the Frobenius inner product for real matrices.

    This class provides the concrete implementation of the InnerProductBase for
    computing the Frobenius inner product between real matrices. The Frobenius
    inner product is defined as the sum of the element-wise products of the two
    matrices, which is equivalent to the trace of the matrix product of the
    transpose of the first matrix and the second matrix.

    Inherits From:
        InnerProductBase: The base class for all inner product implementations.

    Attributes:
        type: Type identifier for this inner product implementation.
    """

    type: Literal["FrobeniusRealInnerProduct"] = "FrobeniusRealInnerProduct"

    def compute(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute the Frobenius inner product between two real matrices.

        The Frobenius inner product is computed as the trace of the matrix
        product of x.T (transpose of x) and y. This is equivalent to summing
        the element-wise products of the two matrices.

        Args:
            x: First real matrix
            y: Second real matrix

        Returns:
            The Frobenius inner product of x and y as a scalar value.

        Raises:
            ValueError: If the input matrices are not of the same shape
        """
        logger.debug("Computing Frobenius inner product")

        if x.shape != y.shape:
            raise ValueError("Matrices must be of the same shape")

        # Compute the trace of x.T @ y which is equivalent to Frobenius inner product
        return float(np.trace(x.T @ y))

    def check_conjugate_symmetry(self, x: np.ndarray, y: np.ndarray) -> bool:
        """Check if the inner product satisfies conjugate symmetry.

        For real matrices, the Frobenius inner product is symmetric, meaning
        that <x, y> = <y, x>. This method verifies this property.

        Args:
            x: First real matrix
            y: Second real matrix

        Returns:
            True if the inner product is conjugate symmetric, False otherwise
        """
        logger.debug("Checking conjugate symmetry")

        inner_product_xy = self.compute(x, y)
        inner_product_yx = self.compute(y, x)

        return np.isclose(inner_product_xy, inner_product_yx)

    def check_linearity_first_argument(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        a: float = 1.0,
        b: float = 1.0,
    ) -> bool:
        """Check linearity in the first argument.

        Verifies that for any matrices x, y, z and scalars a, b:
        <a*x + b*y, z> = a*<x, z> + b*<y, z>

        Args:
            x: First matrix
            y: Second matrix
            z: Third matrix
            a: Scalar coefficient for x
            b: Scalar coefficient for y

        Returns:
            True if the inner product is linear in the first argument, False otherwise
        """
        logger.debug("Checking linearity in first argument")

        # Compute left side: <a*x + b*y, z>
        left_side = self.compute(a * x + b * y, z)

        # Compute right side: a*<x, z> + b*<y, z>
        right_side = a * self.compute(x, z) + b * self.compute(y, z)

        return np.isclose(left_side, right_side)

    def check_positivity(self, x: np.ndarray) -> bool:
        """Check if the inner product is positive definite.

        For the Frobenius inner product, this is true for any non-zero matrix
        since the inner product of any matrix with itself is the sum of the
        squares of its elements, which is always non-negative and positive
        for non-zero matrices.

        Args:
            x: Matrix to check

        Returns:
            True if the inner product is positive definite, False otherwise
        """
        logger.debug("Checking positivity")

        inner_product = self.compute(x, x)
        return inner_product > 0
