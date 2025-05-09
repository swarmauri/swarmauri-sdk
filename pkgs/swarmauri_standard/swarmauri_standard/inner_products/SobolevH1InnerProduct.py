from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from typing import Literal
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "SobolevH1InnerProduct")
class SobolevH1InnerProduct(InnerProductBase):
    """Implementation of the Sobolev H^1 inner product.
    
    This class provides an inner product that combines the L2 norm of the function
    and its first derivative to measure smoothness and proximity in the Sobolev H^1 space.
    
    Attributes:
        type: Literal["SobolevH1InnerProduct"]
            The type identifier for this inner product implementation.
            
    Methods:
        compute: Computes the inner product between two vectors.
        check_conjugate_symmetry: Verifies conjugate symmetry property.
        check_linearity_first_argument: Verifies linearity in the first argument.
        check_positivity: Checks if the inner product is positive definite.
    """
    type: Literal["SobolevH1InnerProduct"] = "SobolevH1InnerProduct"

    def compute(self, x: "IVector", y: "IVector") -> float:
        """Compute the H1 Sobolev inner product between two vectors.
        
        The H1 inner product is defined as:
        <x, y>_{H1} = <x, y>_{L2} + <x', y'>_{L2}
        
        Where:
        - <x, y>_{L2} is the standard L2 inner product of the function values
        - <x', y'>_{L2} is the L2 inner product of the first derivatives
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            The H1 Sobolev inner product of x and y.
        """
        logger.debug("Computing H1 Sobolev inner product")
        
        # Get function values from vectors
        x_func = x.function_value()
        y_func = y.function_value()
        
        # Compute L2 inner product of function values
        l2_function_inner = x_func.inner_product(y_func)
        
        # Get first derivatives
        x_deriv = x.first_derivative()
        y_deriv = y.first_derivative()
        
        # Compute L2 inner product of first derivatives
        l2_derivative_inner = x_deriv.inner_product(y_deriv)
        
        # Combine both components
        h1_inner = l2_function_inner + l2_derivative_inner
        
        logger.debug(f"H1 inner product result: {h1_inner}")
        return h1_inner

    def check_conjugate_symmetry(self, x: "IVector", y: "IVector") -> bool:
        """Check if the H1 inner product satisfies conjugate symmetry.
        
        Conjugate symmetry requires that <x, y> = <y, x>.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if <x, y> == <y, x>, False otherwise.
        """
        logger.debug("Checking conjugate symmetry for H1 inner product")
        inner_xy = self.compute(x, y)
        inner_yx = self.compute(y, x)
        return inner_xy == inner_yx

    def check_linearity_first_argument(self, 
                                      x: "IVector", 
                                      y: "IVector", 
                                      z: "IVector",
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Check linearity in the first argument for the H1 inner product.
        
        Linearity requires that:
        <a*x + b*y, z> = a*<x, z> + b*<y, z>
        
        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y
            
        Returns:
            True if linearity holds, False otherwise.
        """
        logger.debug("Checking linearity in first argument for H1 inner product")
        
        # Compute left-hand side: <a*x + b*y, z>
        lhs = self.compute(a*x + b*y, z)
        
        # Compute right-hand side: a*<x, z> + b*<y, z>
        rhs = a * self.compute(x, z) + b * self.compute(y, z)
        
        return lhs == rhs

    def check_positivity(self, x: "IVector") -> bool:
        """Check if the H1 inner product is positive definite.
        
        Positive definiteness requires that <x, x> > 0 for all non-zero x.
        
        Args:
            x: Vector to check
            
        Returns:
            True if <x, x> > 0, False otherwise.
        """
        logger.debug("Checking positivity for H1 inner product")
        inner = self.compute(x, x)
        return inner > 0