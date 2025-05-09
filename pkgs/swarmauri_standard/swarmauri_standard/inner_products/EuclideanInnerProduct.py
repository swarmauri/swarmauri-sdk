from typing import Literal
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"
    """Concrete implementation of InnerProductBase for Euclidean inner product computation.
    
    Provides functionality to compute the standard L2 inner product (dot product) 
    for real-valued vectors. Inherits from InnerProductBase and implements all 
    required methods for computing and verifying properties of the inner product.
    """
    
    def compute(self, x: "IVector", y: "IVector") -> float:
        """Compute the Euclidean inner product (dot product) of two vectors.
        
        Args:
            x: First real-valued vector
            y: Second real-valued vector
            
        Returns:
            Scalar value representing the dot product of x and y.
            
        Raises:
            ValueError: If vectors are not of the same dimension
        """
        logger.debug("Computing Euclidean inner product")
        if len(x) != len(y):
            raise ValueError("Vectors must be of the same dimension for inner product computation")
        
        # Compute element-wise multiplication and sum
        return sum(x_i * y_i for x_i, y_i in zip(x, y))
    
    def check_conjugate_symmetry(self, x: "IVector", y: "IVector") -> bool:
        """Verify conjugate symmetry property for the inner product.
        
        For real-valued vectors, this checks if <x, y> == <y, x>.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry")
        inner_xy = self.compute(x, y)
        inner_yx = self.compute(y, x)
        return inner_xy == inner_yx
    
    def check_linearity_first_argument(self, 
                                      x: "IVector", 
                                      y: "IVector", 
                                      z: "IVector",
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Verify linearity in the first argument of the inner product.
        
        Checks if <(a*x + b*y), z> equals a*<x, z> + b*<y, z>.
        
        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Coefficient for x
            b: Coefficient for y
            
        Returns:
            True if linearity holds, False otherwise
        """
        logger.debug("Checking linearity in first argument")
        
        # Compute left-hand side: <a*x + b*y, z>
        ax_by = [a * x_i + b * y_i for x_i, y_i in zip(x, y)]
        lhs = self.compute(ax_by, z)
        
        # Compute right-hand side: a*<x, z> + b*<y, z>
        rhs = a * self.compute(x, z) + b * self.compute(y, z)
        
        return lhs == rhs
    
    def check_positivity(self, x: "IVector") -> bool:
        """Verify positive definiteness of the inner product.
        
        Checks if the inner product of x with itself is positive for any non-zero vector x.
        
        Args:
            x: Vector to check
            
        Returns:
            True if positive definiteness holds, False otherwise
        """
        logger.debug("Checking positivity")
        if len(x) == 0:
            return False
            
        inner_xx = self.compute(x, x)
        return inner_xx > 0