from typing import Literal, Optional
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.base.NormBase import NormBase
from swarmauri.norms.base.NormInnerProductMixin import NormInnerProductMixin
from swarmauri.innerproducts.concrete.L2InnerProduct import L2InnerProduct

class L2Norm(NormBase, NormInnerProductMixin):
    """
    L2 norm implementation for vectors, supporting custom domains and sampling.
    """
    type: Literal['L2Norm'] = 'L2Norm'
    inner_product: L2InnerProduct = L2InnerProduct()
    a: Optional[float] = None
    b: Optional[float] = Nonea
    k: float = 1.0
    num_of_points: Optional[int] = None


    def compute(self, x: Vector) -> float:
        """
        Compute the L2 norm of a vector using L2InnerProduct.

        Args:
            x (Vector): The vector (or function) to compute the norm for.

        Returns:
            float: The computed L2 norm.
        """
        # Determine the domain to use
        domain = (self.a, self.b) if self.a is not None and self.b is not None else x.domain
        if domain is None:
            raise ValueError("Domain must be specified for callable vectors or functions.")

        a, b = domain

        # Handle function inputs
        if callable(x.value):
            # Compute the L2 norm as the square root of the inner product
            result = self.inner_product.compute(x.value, x.value, a, b)
        else:
            # Handle non-callable vectors by converting to function representation
            values = x.to_numpy()
            num_points = self.num_of_points if self.num_of_points is not None else len(values)
            sample_points = np.linspace(a, b, num_points)

            # Convert discrete values into a callable function
            def f_discrete(t):
                index = int((t - a) / (b - a) * (len(values) - 1))
                return values[min(index, len(values) - 1)]

            result = self.inner_product.compute(f_discrete, f_discrete, a, b)

        # Apply scaling factor and return the norm
        return (self.k * result) ** 0.5