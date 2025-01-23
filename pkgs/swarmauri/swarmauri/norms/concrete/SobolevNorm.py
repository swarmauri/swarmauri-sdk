from typing import Callable, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.innerproducts.concrete.SobolevInnerProduct import SobolevInnerProduct
from swarmauri.norms.base.NormBase import NormBase
from swarmauri.norms.base.NormInnerProductMixin import NormInnerProductMixin

class SobolevNorm(NormBase, NormInnerProductMixin):
    """
    Sobolev norm implementation using the Sobolev inner product.
    This class computes the Sobolev norm in Sobolev spaces.
    """

    inner_product: SobolevInnerProduct = SobolevInnerProduct()
    type: Literal['SobolevNorm'] = 'SobolevNorm'

    def compute(self, f: Callable[[float], float], a: float, b: float, k: int = 1, num_points: int = 1000) -> float:
        """
        Compute the Sobolev norm of the function `f` over the interval [a, b], considering derivatives up to order k.
        
        Args:
            f: The input function (typically representing the function in the Sobolev space).
            a: The start of the interval.
            b: The end of the interval.
            k: The order of derivatives to include in the Sobolev norm (default is 1).
            num_points: The number of points for numerical integration (default is 1000).
        
        Returns:
            The Sobolev norm of `f`.
        """
        # Compute the Sobolev inner product of f with itself
        inner_prod = self.inner_product.compute(f, f, a=a, b=b, k=k, num_points=num_points)

        # Return the square root of the inner product to get the norm
        return inner_prod ** 0.5
