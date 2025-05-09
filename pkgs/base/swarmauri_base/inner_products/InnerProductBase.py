from abc import ABC
import logging
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

logger = logging.getLogger(__name__)


class InnerProductBase(IInnerProduct, ABC):
    """Base implementation of the IInnerProduct interface.
    
    Provides a concrete base class for implementing inner product operations.
    This class implements the interface defined by IInnerProduct while leaving
    the core computation methods to be implemented by subclasses.
    
    All computation methods raise NotImplementedError and should be
    implemented by concrete subclasses.
    """
    
    def compute(self, x: "IVector", y: "IVector") -> float:
        """Compute the inner product between two vectors.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            The inner product of x and y as a scalar value.
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.debug("Base compute method called")
        raise NotImplementedError("Subclasses must implement the compute method")
        
    def check_conjugate_symmetry(self, x: "IVector", y: "IVector") -> bool:
        """Check if the inner product satisfies conjugate symmetry.
        
        Conjugate symmetry requires that the inner product of x and y is
        equal to the conjugate of the inner product of y and x.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if conjugate symmetry holds, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.debug("Base check_conjugate_symmetry method called")
        raise NotImplementedError("Subclasses must implement the check_conjugate_symmetry method")
        
    def check_linearity_first_argument(self, 
                                      x: "IVector", 
                                      y: "IVector", 
                                      z: "IVector",
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Check if the inner product is linear in the first argument.
        
        Linearity in the first argument requires that for any vectors x, y, z
        and scalars a, b, the following holds:
        <ax + by, z> = a<x, z> + b<y, z>
        
        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y
            
        Returns:
            True if linearity holds, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.debug("Base check_linearity_first_argument method called")
        raise NotImplementedError("Subclasses must implement the check_linearity_first_argument method")
        
    def check_positivity(self, x: "IVector") -> bool:
        """Check if the inner product is positive definite.
        
        Positive definiteness requires that for any non-zero vector x,
        the inner product <x, x> is positive.
        
        Args:
            x: Vector to check
            
        Returns:
            True if positivity holds, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.debug("Base check_positivity method called")
        raise NotImplementedError("Subclasses must implement the check_positivity method")