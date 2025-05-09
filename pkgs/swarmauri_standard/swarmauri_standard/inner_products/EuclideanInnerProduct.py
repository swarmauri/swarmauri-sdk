from typing import Union, List
import numpy as np
import logging

from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_base ComponentBase import ComponentBase

# Define logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    """
    Computes the standard Euclidean inner product (dot product) between two real-valued vectors.
    
    This class implements the InnerProductBase interface to provide concrete functionality for
    computing the inner product in Euclidean space. It follows the standard mathematical definition
    of the dot product and includes validation methods to ensure the properties of an inner product.
    """
    
    type: str = "EuclideanInnerProduct"
    
    def __init__(self):
        """
        Initializes the EuclideanInnerProduct instance.
        """
        super().__init__()
        
    def compute(self, a: Union[np.ndarray, List[float]], b: Union[np.ndarray, List[float]]) -> float:
        """
        Computes the Euclidean inner product (dot product) between two vectors.
        
        Args:
            a: The first vector (numpy array or list of floats)
            b: The second vector (numpy array or list of floats)
            
        Returns:
            float: The dot product of vectors a and b
            
        Raises:
            ValueError: If the input vectors are not of compatible dimensions
        """
        try:
            # Ensure inputs are numpy arrays
            a = np.asarray(a)
            b = np.asarray(b)
            
            # Compute the dot product
            result = np.dot(a, b)
            
            # Ensure the result is a float
            return float(result)
            
        except ValueError as e:
            logger.error("Invalid vector dimensions for dot product computation")
            raise ValueError("Input vectors must have compatible dimensions") from e
    
    def check_conjugate_symmetry(self, a: Union[np.ndarray, List[float]], b: Union[np.ndarray, List[float]]) -> bool:
        """
        Verifies if the inner product satisfies conjugate symmetry.
        
        For real vectors, this means that compute(a, b) should equal compute(b, a).
        
        Args:
            a: The first vector
            b: The second vector
            
        Returns:
            bool: True if conjugate symmetry holds, False otherwise
        """
        try:
            # Compute both inner products
            inner_product_ab = self.compute(a, b)
            inner_product_ba = self.compute(b, a)
            
            # Check if they are equal
            return np.isclose(inner_product_ab, inner_product_ba)
            
        except Exception as e:
            logger.error("Error checking conjugate symmetry")
            return False
    
    def check_linearity_first_argument(self, a: Union[np.ndarray, List[float]], b: Union[np.ndarray, List[float]], c: Union[np.ndarray, List[float]]) -> bool:
        """
        Checks if the inner product is linear in the first argument.
        
        This means that for vectors a, b, c and scalar k:
        compute(a + c, b) = compute(a, b) + compute(c, b)
        compute(k * a, b) = k * compute(a, b)
        
        Args:
            a: The first vector
            b: The second vector
            c: The third vector for additivity check
            
        Returns:
            bool: True if linearity holds, False otherwise
        """
        try:
            # Check additivity
            ab = self.compute(a, b)
            cb = self.compute(c, b)
            ab_plus_cb = self.compute(np.add(a, c), b)
            
            if not np.isclose(ab + cb, ab_plus_cb):
                return False
            
            # Check homogeneity (k=2 for simplicity)
            k = 2.0
            k_ab = self.compute(k * a, b)
            k_times_ab = k * ab
            
            return np.isclose(k_ab, k_times_ab)
            
        except Exception as e:
            logger.error("Error checking linearity in first argument")
            return False
    
    def check_positivity(self, a: Union[np.ndarray, List[float]]) -> bool:
        """
        Checks if the inner product is positive definite.
        
        For a non-zero vector a, compute(a, a) must be positive.
        
        Args:
            a: The vector to check
            
        Returns:
            bool: True if the inner product is positive definite, False otherwise
        """
        try:
            # Compute the inner product of a with itself
            inner_product = self.compute(a, a)
            
            # Check if the result is positive and that a is not the zero vector
            is_positive = inner_product > 0.0
            a_not_zero = not np.allclose(a, np.zeros_like(a))
            
            return is_positive and a_not_zero
            
        except Exception as e:
            logger.error("Error checking positivity")
            return False