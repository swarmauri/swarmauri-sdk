from typing import Literal, List
from swarmauri.innerproducts.concrete.FrobeniusInnerProduct import FrobeniusInnerProduct
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.base.NormBase import NormBase
from swarmauri.norms.base.NormInnerProductMixin import NormInnerProductMixin

class FrobeniusNorm(NormBase, NormInnerProductMixin):
    """
    Frobenius norm implementation using the Frobenius inner product.
    """
    inner_product: FrobeniusInnerProduct = FrobeniusInnerProduct()
    type: Literal['FrobeniusNorm'] = "FrobeniusNorm"

    def compute(self, x: List[Vector]) -> float:
        """
        Computes the Frobenius norm of a matrix.
        The Frobenius norm is the square root of the Frobenius inner product
        of the matrix with itself.

        Args:
            x (List[Vector]): The matrix whose Frobenius norm is to be computed.
        
        Returns:
            float: The Frobenius norm of the matrix.
        """
        return (self.inner_product.compute(x, x)) ** 0.5
