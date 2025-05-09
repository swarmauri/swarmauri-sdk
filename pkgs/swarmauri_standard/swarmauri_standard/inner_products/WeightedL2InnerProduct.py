from typing import Callable, Optional, Dict, Any
from abc import ABC
import logging
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_core.types import IVector, Literal

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "WeightedL2InnerProduct")
class WeightedL2InnerProduct(InnerProductBase):
    """Concrete implementation of the InnerProductBase for weighted L2 inner product.

    This class provides an implementation of an inner product for real or complex
    functions with position-dependent weights. The weight function must be strictly
    positive to maintain the positive definiteness of the inner product.

    Attributes:
        weight_function: Callable that takes a vector and returns its weights.
        weight_parameters: Optional dictionary of parameters for the weight function.
    """
    type: Literal["WeightedL2InnerProduct"] = "WeightedL2InnerProduct"

    def __init__(self, weight_function: Callable[[IVector], IVector], 
                 weight_parameters: Optional[Dict[str, Any]] = None):
        """Initialize the WeightedL2InnerProduct instance.

        Args:
            weight_function: Function that computes the weight for each vector.
            weight_parameters: Optional parameters for the weight function.
            
        Raises:
            ValueError: If the weight function is not callable or not strictly positive.
        """
        super().__init__()
        if not callable(weight_function):
            raise ValueError("Weight function must be callable")
        if weight_parameters is None:
            weight_parameters = {}
        self.weight_function = weight_function
        self.weight_parameters = weight_parameters

    def compute(self, x: IVector, y: IVector) -> float:
        """Compute the weighted L2 inner product of two vectors.

        The weighted L2 inner product is defined as the integral of the product
        of the conjugate of x, the weight function, and y.

        Args:
            x: First vector
            y: Second vector

        Returns:
            The weighted L2 inner product of x and y.

        Raises:
            ValueError: If the weight function is not strictly positive.
        """
        logger.debug("Computing weighted L2 inner product")
        
        # Get the weight for the vectors
        weight = self.weight_function(x)
        
        # Check if the weight is strictly positive
        if not weight.magnitude_squared() > 0:
            raise ValueError("Weight function must be strictly positive")
            
        # Compute the element-wise product of conjugate(x) and y
        product = x.conjugate().element_wise_multiply(y)
        
        # Apply the weight to the product
        weighted_product = product.element_wise_multiply(weight)
        
        # Integrate to get the inner product value
        return weighted_product.integrate()

    def check_conjugate_symmetry(self, x: IVector, y: IVector) -> bool:
        """Check if the inner product satisfies conjugate symmetry.

        Conjugate symmetry requires that <x, y> = conjugate(<y, x>).

        Args:
            x: First vector
            y: Second vector

        Returns:
            True if conjugate symmetry holds, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")
        
        inner_product_xy = self.compute(x, y)
        inner_product_yx = self.compute(y, x)
        
        # Return whether the inner product is equal to its conjugate
        return inner_product_xy == inner_product_yx.conjugate()

    def check_linearity_first_argument(self, 
                                      x: IVector, 
                                      y: IVector, 
                                      z: IVector,
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Check if the inner product is linear in the first argument.

        Linearity requires that <ax + by, z> = a<x, z> + b<y, z>.

        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y

        Returns:
            True if linearity holds, False otherwise.
        """
        logger.debug("Checking linearity in first argument")
        
        # Compute the left-hand side
        lhs = self.compute(a * x + b * y, z)
        
        # Compute the right-hand side
        rhs = a * self.compute(x, z) + b * self.compute(y, z)
        
        # Return whether they are equal within some tolerance
        return lhs == rhs

    def check_positivity(self, x: IVector) -> bool:
        """Check if the inner product is positive definite.

        Positive definiteness requires that <x, x> is positive for any non-zero x.

        Args:
            x: Vector to check

        Returns:
            True if positivity holds, False otherwise.
        """
        logger.debug("Checking positivity")
        
        inner_product = self.compute(x, x)
        
        # Return whether the inner product is positive
        return inner_product > 0