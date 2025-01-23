# swarmauri/innerproducts/concrete/DotProduct.py
from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from swarmauri.vectors.concrete.Vector import Vector
from typing import Literal

class DotProduct(InnerProductBase):
    """
    A class representing the dot product of two vectors.

    The dot product is a way to compute a scalar value from two vectors.
    It is widely used in linear algebra, statistics, and other fields.
    """

    type: Literal['DotProduct'] = 'DotProduct'

    def compute(self, u: Vector, v: Vector) -> float:
        """
        Compute the dot product of two vectors, ensuring the result is a real value.

        Args:
            u: The first vector.
            v: The second vector.

        Returns:
            A float representing the dot product.

        Raises:
            ValueError: If the vectors have different dimensions.
        """
        if len(u.value) != len(v.value):
            raise ValueError("Vectors must have the same dimension to compute the dot product.")

        # Compute the dot product as the sum of element-wise products
        return sum(u_i * v_i for u_i, v_i in zip(u.value, v.value))  # Returns a real number (float)
