"""Module implementing the Hermitian inner product for swarmauri_standard package."""
from typing import Literal
from abc import ABC, abstractmethod
import logging

from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """
    A concrete implementation of InnerProductBase for computing Hermitian inner products.

    This class handles complex inner products with Hermitian symmetry, supporting
    conjugate symmetry and L2 structure for complex vectors.

    Methods:
        compute(a, b): Computes the inner product of two complex vectors.
        check_conjugate_symmetry(a, b): Verifies conjugate symmetry of the inner product.
        check_linearity(a, b, c): Checks linearity in the first argument.
        check_positivity(a): Verifies positive definiteness of the inner product.
    """

    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"

    def __init__(self):
        """
        Initializes the HermitianInnerProduct instance.
        """
        super().__init__()
        logger.debug("Initialized HermitianInnerProduct.")

    def compute(self, a: complex, b: complex) -> float:
        """
        Computes the inner product of two complex vectors with Hermitian symmetry.

        Args:
            a: The first complex vector.
            b: The second complex vector.

        Returns:
            A float representing the inner product result.

        Raises:
            TypeError: If input vectors are not of complex type.
        """
        logger.debug("Computing Hermitian inner product...")
        
        if not isinstance(a, complex) or not isinstance(b, complex):
            raise TypeError("Input vectors must be complex.")

        # Compute the inner product using conjugate symmetry
        product = a * b.conjugate()
        return float(product.real)  # Return only the real part of the product

    def check_conjugate_symmetry(self, a: complex, b: complex) -> bool:
        """
        Checks if the inner product satisfies conjugate symmetry (<a, b> = <b, a>*).

        Args:
            a: The first complex vector.
            b: The second complex vector.

        Returns:
            bool: True if conjugate symmetric, False otherwise.
        """
        logger.debug("Checking conjugate symmetry...")
        
        inner_product_ab = self.compute(a, b)
        inner_product_ba = self.compute(b, a)
        
        # Check if <a, b> is the conjugate of <b, a>
        return inner_product_ab == inner_product_ba.conjugate()

    def check_linearity(self, a: complex, b: complex, c: complex) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        Args:
            a: The first complex vector.
            b: The second complex vector.
            c: A scalar for linearity check.

        Returns:
            bool: True if the inner product is linear, False otherwise.
        """
        logger.debug("Checking linearity...")
        
        # Check linearity: <a + b, c> = <a, c> + <b, c>
        # and <k*a, b> = k*<a, b>
        inner_product_add = self.compute(a + b, c)
        inner_product_sum = self.compute(a, c) + self.compute(b, c)
        
        inner_product_scale = self.compute(c * a, b)
        inner_product_scaled = c * self.compute(a, b)
        
        return (inner_product_add == inner_product_sum) and \
               (inner_product_scale == inner_product_scaled)

    def check_positivity(self, a: complex) -> bool:
        """
        Checks if the inner product is positive definite.

        Args:
            a: The vector to check.

        Returns:
            bool: True if the inner product is positive definite, False otherwise.
        """
        logger.debug("Checking positivity...")
        
        inner_product = self.compute(a, a)
        
        # For positive definiteness, <a, a> must be positive for a ≠ 0
        if a == 0:
            return inner_product == 0.0
        return inner_product > 0.0