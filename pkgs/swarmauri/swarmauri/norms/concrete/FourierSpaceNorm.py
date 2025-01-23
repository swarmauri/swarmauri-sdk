from swarmauri.innerproducts.concrete.FourierSpaceInnerProduct import FourierSpaceInnerProduct
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.base.NormBase import NormBase
from swarmauri.norms.base.NormInnerProductMixin import NormInnerProductMixin
from typing import Literal

class FourierSpaceNorm(NormBase, NormInnerProductMixin):
    """
    Fourier space norm implementation using the Fourier space inner product.
    """
    inner_product: FourierSpaceInnerProduct = FourierSpaceInnerProduct()
    type: Literal['FourierSpaceNorm'] = "FourierSpaceNorm"

    def compute(self, x: Vector) -> float:
        # Norm is the square root of the Fourier space inner product of x with itself
        return (self.inner_product.compute(x, x)) ** 0.5
