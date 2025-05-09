import numpy as np
import logging
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplexInnerProduct")
class FrobeniusComplexInnerProduct(InnerProductBase):
    """Concrete implementation of the InnerProductBase class for computing the Frobenius inner product for complex matrices.
    
    This class provides the functionality for computing the Frobenius inner product
    between two complex matrices. The Frobenius inner product is defined as the sum
    of the element-wise products of the conjugate of one matrix with the other.
    
    The class inherits from InnerProductBase and implements the core computation
    methods required for the inner product operations.
    """
    
    type: str = "FrobeniusComplexInnerProduct"
    
    def __init__(self):
        """Initialize the FrobeniusComplexInnerProduct instance."""
        super().__init__()
        logger.debug("FrobeniusComplexInnerProduct instance initialized")
    
    def compute(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute the Frobenius inner product between two complex matrices.
        
        The Frobenius inner product is computed as the sum of the element-wise
        products of the conjugate of one matrix with the other. This is equivalent
        to the trace of the product of one matrix with the conjugate transpose
        of the other.
        
        Args:
            x: First complex matrix
            y: Second complex matrix
            
        Returns:
            The Frobenius inner product of x and y as a scalar value.
            
        Raises:
            ValueError: If the input matrices are not compatible for inner product computation
        """
        logger.debug("Computing Frobenius inner product")
        
        # Ensure the input matrices are numpy arrays
        if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
            raise ValueError("Inputs must be numpy arrays")
            
        # Compute the element-wise product with conjugate of y
        product = x * y.conj()
        
        # Sum all elements to get the inner product
        inner_product = np.sum(product)
        
        # Return as a float
        return float(inner_product)
    
    def check_conjugate_symmetry(self, x: np.ndarray, y: np.ndarray) -> bool:
        """Check if the inner product satisfies conjugate symmetry.
        
        Conjugate symmetry requires that the inner product of x and y is
        equal to the conjugate of the inner product of y and x.
        
        Args:
            x: First complex matrix
            y: Second complex matrix
            
        Returns:
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry")
        
        ip_xy = self.compute(x, y)
        ip_yx = self.compute(y, x)
        
        # Compute the conjugate of ip_yx and compare with ip_xy
        return np.isclose(ip_xy, ip_yx.conj())
    
    def check_linearity_first_argument(self, 
                                      x: np.ndarray, 
                                      y: np.ndarray, 
                                      z: np.ndarray,
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Check if the inner product is linear in the first argument.
        
        Linearity in the first argument requires that for any matrices x, y, z
        and scalars a, b, the following holds:
        <a*x + b*y, z> = a*<x, z> + b*<y, z>
        
        Args:
            x: First complex matrix
            y: Second complex matrix
            z: Third complex matrix
            a: Scalar coefficient for x
            b: Scalar coefficient for y
            
        Returns:
            True if linearity holds, False otherwise
        """
        logger.debug("Checking linearity in the first argument")
        
        # Compute left-hand side: <a*x + b*y, z>
        lhs = self.compute(a * x + b * y, z)
        
        # Compute right-hand side: a*<x, z> + b*<y, z>
        rhs = a * self.compute(x, z) + b * self.compute(y, z)
        
        # Use numpy's isclose for numeric comparison
        return np.isclose(lhs, rhs)
    
    def check_positivity(self, x: np.ndarray) -> bool:
        """Check if the inner product is positive definite.
        
        Positive definiteness requires that for any non-zero matrix x,
        the inner product <x, x> is positive.
        
        Args:
            x: Complex matrix to check
            
        Returns:
            True if positivity holds, False otherwise
        """
        logger.debug("Checking positivity")
        
        ip = self.compute(x, x)
        
        # The inner product of a matrix with itself is a real number
        # We check if it's positive
        return ip > 0