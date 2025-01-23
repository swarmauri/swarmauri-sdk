# swarmauri/innerproducts/concrete/ComplexDotProduct.py
from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from swarmauri.vectors.concrete.Vector import Vector
from typing import Literal

class ComplexDotProduct(InnerProductBase):
    """
    A class representing the complex dot product of two vectors.

    The complex dot product computes the sum of element-wise products, where the second vector is conjugated.
    It is used in complex vector spaces.
    """

    type: Literal['ComplexDotProduct'] = 'ComplexDotProduct'

    def compute(self, u: Vector, v: Vector) -> complex:
        """
        Compute the complex dot product of two vectors.

        Args:
            u: The first vector.
            v: The second vector.

        Returns:
            A complex number representing the complex dot product.

        Raises:
            ValueError: If the vectors have different dimensions.
        """
        if len(u.value) != len(v.value):
            raise ValueError("Vectors must have the same dimension to compute the complex dot product.")

        # Compute the complex dot product as the sum of element-wise products with conjugation on the second vector
        result = sum(u_i * v_i.conjugate() for u_i, v_i in zip(u.value, v.value))

        # Return the result as a complex number
        return result
