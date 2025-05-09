from abc import ABC
from typing import Literal
import logging
from ..ComponentBase import ComponentBase
from ..inner_products.IInnerProduct import IInnerProduct

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """Concrete implementation of InnerProductBase for Hermitian inner products.

    Provides functionality for computing inner products with conjugate symmetry,
    suitable for complex vector spaces. Implements the Hermitian inner product
    definition where the inner product of vectors x and y is defined as the
    conjugate transpose of x multiplied by y.
    """

    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"

    def compute(self, x: "IVector", y: "IVector") -> float:
        """Compute the Hermitian inner product of two complex vectors.

        The Hermitian inner product is defined as the conjugate transpose of
        the first vector multiplied by the second vector. This implementation
        ensures conjugate symmetry and handles complex vectors appropriately.

        Args:
            x: The first complex vector
            y: The second complex vector

        Returns:
            The real-valued inner product of x and y

        Raises:
            ValueError: If the input vectors are not of complex type
        """
        logger.debug("Computing Hermitian inner product")

        # Ensure input vectors are complex
        if not x.is_complex or not y.is_complex:
            raise ValueError("HermitianInnerProduct requires complex vectors")

        # Compute conjugate transpose of x and dot product with y
        product = x.conj().dot(y)

        # Return real part to ensure scalar output
        return float(product.real)

    def check_conjugate_symmetry(self, x: "IVector", y: "IVector") -> bool:
        """Check if the inner product satisfies conjugate symmetry.

        For Hermitian inner product, we must verify that <x, y> = conj(<y, x>).

        Args:
            x: First complex vector
            y: Second complex vector

        Returns:
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry")

        # Compute inner products
        inner_xy = self.compute(x, y)
        inner_yx = self.compute(y, x)

        # Check if inner_xy is the conjugate of inner_yx
        return inner_xy == inner_yx.conjugate()

    def check_linearity_first_argument(
        self, x: "IVector", y: "IVector", z: "IVector", a: float = 1.0, b: float = 1.0
    ) -> bool:
        """Verify linearity in the first argument.

        Checks if a<x,z> + b<y,z> equals <ax + by, z>.

        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y

        Returns:
            True if linearity holds, False otherwise
        """
        logger.debug("Checking linearity in first argument")

        # Compute left side: a<x,z> + b<y,z>
        left = a * self.compute(x, z) + b * self.compute(y, z)

        # Compute right side: <ax + by, z>
        ax_by = a * x + b * y
        right = self.compute(ax_by, z)

        # Compare with tolerance for floating point precision
        return abs(left - right) < 1e-12

    def check_positivity(self, x: "IVector") -> bool:
        """Check if the inner product is positive definite.

        For any non-zero vector x, <x, x> should be positive.

        Args:
            x: Vector to check

        Returns:
            True if the inner product is positive, False otherwise
        """
        logger.debug("Checking positivity")

        # Compute inner product of x with itself
        inner = self.compute(x, x)

        # Ensure result is a positive real number
        return inner > 0.0
