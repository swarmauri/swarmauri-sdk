from typing import Any, List, Union, Literal, Optional
import logging
import numpy as np
from numpy.typing import NDArray

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """
    Hermitian inner product implementation for complex vectors.
    
    This class provides a concrete implementation of the inner product for complex vectors,
    ensuring Hermitian (conjugate) symmetry. The inner product is defined as <x,y> = y^H * x,
    where y^H is the conjugate transpose of y.
    
    Attributes
    ----------
    type : Literal["HermitianInnerProduct"]
        The type identifier for this component
    """
    
    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"
    
    def __init__(self) -> None:
        """
        Initialize the Hermitian inner product implementation.
        
        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing HermitianInnerProduct")
    
    def compute(self, vec1: Union[List[complex], NDArray[np.complex_], complex], 
                vec2: Union[List[complex], NDArray[np.complex_], complex]) -> complex:
        """
        Compute the Hermitian inner product between two complex vectors.
        
        The Hermitian inner product is defined as <x,y> = y^H * x, where y^H is the 
        conjugate transpose of y. This ensures conjugate symmetry: <x,y> = <y,x>*.
        
        Parameters
        ----------
        vec1 : Union[List[complex], NDArray[np.complex_], complex]
            First complex vector (or scalar) in the inner product
        vec2 : Union[List[complex], NDArray[np.complex_], complex]
            Second complex vector (or scalar) in the inner product
            
        Returns
        -------
        complex
            The resulting inner product value
            
        Raises
        ------
        ValueError
            If the vectors are incompatible for inner product calculation
        TypeError
            If the vectors are not of complex type
        """
        if not self.is_compatible(vec1, vec2):
            self.logger.error("Incompatible vectors for inner product calculation")
            raise ValueError("Vectors must have the same dimensions for inner product calculation")
        
        # Convert inputs to numpy arrays if they aren't already
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1, dtype=complex)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2, dtype=complex)
        
        # Ensure arrays are complex
        if not np.issubdtype(vec1.dtype, np.complexfloating) or not np.issubdtype(vec2.dtype, np.complexfloating):
            vec1 = vec1.astype(complex)
            vec2 = vec2.astype(complex)
        
        # Compute the Hermitian inner product: <x,y> = y^H * x
        # For vectors, this is the conjugate transpose of vec2 multiplied by vec1
        if vec1.ndim == 0 and vec2.ndim == 0:
            # For scalars, just multiply
            result = np.conj(vec2) * vec1
        else:
            # For vectors, use dot product with conjugate
            result = np.vdot(vec2, vec1)  # vdot computes the conjugate dot product
        
        self.logger.debug(f"Computed inner product: {result}")
        return result
    
    def is_compatible(self, vec1: Any, vec2: Any) -> bool:
        """
        Check if two vectors are compatible for Hermitian inner product calculation.
        
        Vectors are compatible if they have the same shape or can be cast to the same shape.
        
        Parameters
        ----------
        vec1 : Any
            First vector to check
        vec2 : Any
            Second vector to check
            
        Returns
        -------
        bool
            True if the vectors are compatible, False otherwise
        """
        try:
            # Try to convert to numpy arrays
            if not isinstance(vec1, np.ndarray):
                vec1 = np.array(vec1, dtype=complex)
            if not isinstance(vec2, np.ndarray):
                vec2 = np.array(vec2, dtype=complex)
            
            # Check if shapes are compatible
            return vec1.shape == vec2.shape
        except (TypeError, ValueError) as e:
            self.logger.error(f"Error checking compatibility: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error checking compatibility: {e}")
            return False