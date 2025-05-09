"""Module implementing the Euclidean inner product for swarmauri_standard package."""

from typing import Literal
import numpy as np
import logging
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

# Set up logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    """Concrete implementation of the InnerProductBase for Euclidean inner product.
    
    This class provides the standard Euclidean inner product implementation for real-valued vectors.
    It inherits from the InnerProductBase class and implements all required methods.
    
    Attributes:
        type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"
            Type identifier for the inner product implementation.
    """
    type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"

    def __init__(self):
        """Initializes the EuclideanInnerProduct instance."""
        super().__init__()
        self.type = "EuclideanInnerProduct"

    def compute(self, a: object, b: object) -> float:
        """Computes the Euclidean inner product of two real vectors.
        
        Args:
            a: First real vector (list, numpy.ndarray, or similar iterable)
            b: Second real vector (list, numpy.ndarray, or similar iterable)
            
        Returns:
            float: Result of the Euclidean inner product computation.
            
        Raises:
            ValueError: If input vectors are not of compatible dimensions
        """
        logger.debug("Computing Euclidean inner product of vectors")
        
        try:
            a_np = np.asarray(a)
            b_np = np.asarray(b)
            
            if a_np.ndim != 1 or b_np.ndim != 1:
                raise ValueError("Input vectors must be 1-dimensional")
                
            if len(a_np) != len(b_np):
                raise ValueError("Input vectors must be of the same length")
                
            result = np.dot(a_np, b_np)
            logger.debug(f"Computation result: {result}")
            return result
            
        except ValueError as ve:
            logger.error(f"ValueError in compute method: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in compute method: {e}")
            raise e

    def check_conjugate_symmetry(self, a: object, b: object) -> bool:
        """Checks if the inner product is conjugate symmetric (<a, b> = <b, a>*).
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            bool: True if the inner product is conjugate symmetric, False otherwise
        """
        logger.debug("Checking conjugate symmetry")
        
        try:
            inner_product_ab = self.compute(a, b)
            inner_product_ba = self.compute(b, a)
            
            # Since we're dealing with real vectors, the conjugate symmetry
            # reduces to standard symmetry
            return np.isclose(inner_product_ab, inner_product_ba)
            
        except Exception as e:
            logger.error(f"Error in check_conjugate_symmetry: {e}")
            return False

    def check_linearity(self, a: object, b: object, c: object) -> bool:
        """Checks if the inner product is linear in the first argument.
        
        Verifies that <a + c, b> = <a, b> + <c, b> for some vector c.
        
        Args:
            a: First vector
            b: Second vector
            c: Third vector (to be added to a)
            
        Returns:
            bool: True if the inner product is linear, False otherwise
        """
        logger.debug("Checking linearity of inner product")
        
        try:
            # Compute individual inner products
            inner_product_ab = self.compute(a, b)
            inner_product_cb = self.compute(c, b)
            
            # Compute inner product of (a + c) and b
            a_plus_c = np.asarray(a) + np.asarray(c)
            inner_product_ab_c = self.compute(a_plus_c, b)
            
            # Check if <a+c, b> equals <a,b> + <c,b>
            return np.isclose(inner_product_ab_c, inner_product_ab + inner_product_cb)
            
        except Exception as e:
            logger.error(f"Error in check_linearity: {e}")
            return False

    def check_positivity(self, a: object) -> bool:
        """Checks if the inner product is positive definite.
        
        Verifies that <a, a> > 0 for any non-zero vector a.
        
        Args:
            a: Vector to check
            
        Returns:
            bool: True if the inner product is positive definite, False otherwise
        """
        logger.debug("Checking positivity of inner product")
        
        try:
            a_np = np.asarray(a)
            if a_np.size == 0:
                logger.warning("Empty vector provided for positivity check")
                return False
                
            inner_product_aa = self.compute(a, a)
            
            if inner_product_aa <= 0:
                logger.warning("Inner product result was not positive")
                return False
                
            # Check if the vector is the zero vector
            if np.allclose(a_np, np.zeros_like(a_np)):
                logger.warning("Zero vector provided for positivity check")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in check_positivity: {e}")
            return False

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f"EuclideanInnerProduct(type={self.type})"