import logging
import numpy as np
from typing import Any, Literal, Union

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(InnerProductBase, "FrobeniusComplex")
class FrobeniusComplex(InnerProductBase):
    """
    Implementation of Frobenius inner product for complex matrices.
    
    This class implements the Frobenius inner product for complex matrices,
    which is defined as the trace of the product of one matrix with the 
    conjugate transpose of the other. For matrices A and B, the inner product
    is calculated as: trace(A @ B.conj().T).
    
    Attributes
    ----------
    type : Literal["FrobeniusComplex"]
        The type identifier for this inner product implementation
    """
    
    type: Literal["FrobeniusComplex"] = "FrobeniusComplex"
    
    def __init__(self) -> None:
        """
        Initialize the Frobenius inner product for complex matrices.
        
        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing FrobeniusComplex inner product")
    
    def compute(self, vec1: Union[np.ndarray, Any], vec2: Union[np.ndarray, Any]) -> float:
        """
        Compute the Frobenius inner product between two complex matrices.
        
        The Frobenius inner product for complex matrices A and B is defined as:
        <A, B> = trace(A @ B.conj().T)
        
        Parameters
        ----------
        vec1 : Union[np.ndarray, Any]
            First matrix in the inner product
        vec2 : Union[np.ndarray, Any]
            Second matrix in the inner product
            
        Returns
        -------
        float
            The resulting inner product value
            
        Raises
        ------
        ValueError
            If the matrices are incompatible for inner product calculation
        TypeError
            If the matrices are of unsupported types or don't support conjugation
        """
        if not self.is_compatible(vec1, vec2):
            self.logger.error("Matrices are not compatible for Frobenius inner product")
            raise ValueError("Matrices must have compatible dimensions for inner product calculation")
        
        try:
            # For complex matrices, we need the conjugate transpose of the second matrix
            # np.trace computes the sum of the diagonal elements
            # The result should be a real number (though it might have a very small imaginary part due to numerical errors)
            result = np.trace(np.matmul(vec1, vec2.conj().T))
            
            # Ensure the result is real (might have a tiny imaginary component due to numerical precision)
            if np.iscomplex(result) and abs(result.imag) < 1e-10:
                result = result.real
                
            return float(result)
        except AttributeError:
            self.logger.error("Input matrices must support conjugation")
            raise TypeError("Input matrices must support conjugation")
        except Exception as e:
            self.logger.error(f"Error computing Frobenius inner product: {str(e)}")
            raise
    
    def is_compatible(self, vec1: Union[np.ndarray, Any], vec2: Union[np.ndarray, Any]) -> bool:
        """
        Check if two matrices are compatible for Frobenius inner product calculation.
        
        For the Frobenius inner product, matrices must have the same shape.
        
        Parameters
        ----------
        vec1 : Union[np.ndarray, Any]
            First matrix to check
        vec2 : Union[np.ndarray, Any]
            Second matrix to check
            
        Returns
        -------
        bool
            True if the matrices are compatible, False otherwise
        """
        try:
            # Check if inputs are array-like
            shape1 = np.shape(vec1)
            shape2 = np.shape(vec2)
            
            # Check if both have the same shape
            if shape1 != shape2:
                self.logger.debug(f"Incompatible shapes: {shape1} vs {shape2}")
                return False
            
            # Check if both support conjugation
            # This is a simple test to see if the object has a conj method or attribute
            if not hasattr(vec1, 'conj') or not hasattr(vec2, 'conj'):
                self.logger.debug("One or both matrices don't support conjugation")
                return False
                
            return True
        except Exception as e:
            self.logger.debug(f"Error checking compatibility: {str(e)}")
            return False