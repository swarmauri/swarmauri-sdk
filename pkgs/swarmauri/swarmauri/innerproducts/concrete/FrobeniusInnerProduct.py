# swarmauri/innerproducts/concrete/FrobeniusInnerProduct.py

from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase
from swarmauri.vectors.concrete.Vector import Vector
from typing import Literal, Union

class FrobeniusInnerProduct(InnerProductBase):
    """
    A class representing the Frobenius inner product of two matrices.

    The Frobenius inner product is defined as the sum of the element-wise products of two matrices.
    It is widely used in matrix analysis, especially for matrix optimization.
    """

    type: Literal['FrobeniusInnerProduct'] = 'FrobeniusInnerProduct'

    def compute(self, u: Vector, v: Vector) -> Union[float, complex]:
        """
        Compute the Frobenius inner product of two matrices, ensuring the result is a scalar.

        Args:
            u: The first matrix (as a vector of vectors).
            v: The second matrix (as a vector of vectors).

        Returns:
            A scalar representing the Frobenius inner product.

        Raises:
            ValueError: If the matrices have different dimensions.
        """
        if len(u.value) != len(v.value) or any(len(row_u) != len(row_v) for row_u, row_v in zip(u.value, v.value)):
            raise ValueError("Matrices must have the same dimensions to compute the Frobenius inner product.")

        # Compute the Frobenius inner product as the sum of element-wise products
        result = sum(u_i * v_i for row_u, row_v in zip(u.value, v.value) for u_i, v_i in zip(row_u, row_v))

        # Return the result as a scalar (float or complex)
        return result
