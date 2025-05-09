from abc import ABC, abstractmethod
from typing import Union, Optional
import logging
import numpy as np

# Set up logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase


@ComponentBase.register_type(InnerProductBase, "TraceFormWeightedInnerProduct")
class TraceFormWeightedInnerProduct(InnerProductBase):
    """
    A concrete implementation of the InnerProductBase class for computing the inner product
    using the weighted trace of matrix product.

    This class provides the functionality to compute the inner product of two matrices
    with an additional weight matrix that modulates the trace operation.
    """

    def __init__(self, weight_matrix: Optional[np.ndarray] = None):
        """
        Initializes the TraceFormWeightedInnerProduct instance.

        Args:
            weight_matrix: The weight matrix used to modulate the trace operation.
                           If None, an identity matrix of appropriate size is used.
        """
        super().__init__()
        self.weight_matrix = weight_matrix
        self.dtype = None  # Will be set based on input matrices

    def compute(
        self, a: Union[object, object], b: Union[object, object]
    ) -> Union[float, complex]:
        """
        Computes the inner product using the trace of the matrix product
        modulated by the weight matrix.

        Args:
            a: The first matrix
            b: The second matrix

        Returns:
            Union[float, complex]: The result of the inner product computation

        Raises:
            ValueError: If the input matrices are incompatible
        """
        # Ensure matrices are numpy arrays
        a = np.asarray(a, dtype=self.dtype)
        b = np.asarray(b, dtype=self.dtype)

        # Check matrix dimensions for multiplication
        if a.shape[-1] != b.shape[0]:
            raise ValueError("Matrix dimensions are incompatible for multiplication")

        # Compute the matrix product
        product_matrix = np.dot(a, b)

        # Apply the weight matrix
        if self.weight_matrix is None:
            # Default to identity matrix if weight is not provided
            weight = np.identity(product_matrix.shape[0], dtype=product_matrix.dtype)
        else:
            weight = self.weight_matrix

        # Ensure weight matrix dimensions match
        if weight.shape != product_matrix.shape:
            raise ValueError("Weight matrix dimensions do not match the product matrix")

        # Apply element-wise multiplication with weight matrix
        weighted_product = product_matrix * weight

        # Compute the trace
        trace_value = np.trace(weighted_product)

        return trace_value

    def check_conjugate_symmetry(
        self, a: Union[object, object], b: Union[object, object]
    ) -> bool:
        """
        Checks if the inner product implementation satisfies conjugate symmetry.

        Args:
            a: The first matrix
            b: The second matrix

        Returns:
            bool: True if <a, b> equals the conjugate of <b, a>, False otherwise
        """
        # Compute <a, b>
        inner_product_ab = self.compute(a, b)

        # Compute <b, a>
        inner_product_ba = self.compute(b, a)

        # Check if <a, b> is the conjugate of <b, a>
        return np.isclose(inner_product_ab, np.conj(inner_product_ba))

    def check_linearity_first_argument(
        self,
        a: Union[object, object],
        b: Union[object, object],
        c: Union[object, object],
    ) -> bool:
        """
        Checks if the inner product implementation is linear in the first argument.

        Args:
            a: The first matrix
            b: The second matrix
            c: The third matrix

        Returns:
            bool: True if the inner product is linear in the first argument, False otherwise
        """
        # Test linearity: <a + c, b> == <a, b> + <c, b>
        inner_product_ac_b = self.compute(a + c, b)
        inner_product_a_b = self.compute(a, b)
        inner_product_c_b = self.compute(c, b)
        linearity_add = np.isclose(
            inner_product_ac_b, inner_product_a_b + inner_product_c_b
        )

        # Test scalar multiplication: <k*a, b> == k*<a, b>
        k = 2.0
        inner_product_ka_b = self.compute(k * a, b)
        scalar_multiplication = np.isclose(inner_product_ka_b, k * inner_product_a_b)

        return linearity_add and scalar_multiplication

    def check_positivity(self, a: Union[object, object]) -> bool:
        """
        Checks if the inner product implementation satisfies positive definiteness.

        Args:
            a: The matrix to check

        Returns:
            bool: True if <a, a> is positive, False otherwise
        """
        # Compute <a, a>
        inner_product_aa = self.compute(a, a)

        # For positive definiteness, <a, a> should be positive
        if np.iscomplex(inner_product_aa):
            # For complex numbers, check if the real part is positive
            return inner_product_aa.real > 0
        else:
            return inner_product_aa > 0
