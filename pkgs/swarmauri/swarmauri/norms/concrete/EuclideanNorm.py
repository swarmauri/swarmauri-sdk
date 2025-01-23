from swarmauri.innerproducts.concrete.DotProduct import DotProduct
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.base.NormBase import NormBase
from swarmauri.norms.base.NormInnerProductMixin import NormInnerProductMixin

class DiscreteL2Norm(NormBase, NormInnerProductMixin):
    """
    Euclidean norm implementation using the dot product as the inner product.
    """
    inner_product: DotProduct = DotProduct()
    type: Literal['DiscreteL2Norm'] = DiscreteL2Norm

    def compute(self, x: Vector) -> float:
        # Norm is the square root of the inner product of x with itself
        return (self.inner_product.compute(x, x)) ** 0.5
