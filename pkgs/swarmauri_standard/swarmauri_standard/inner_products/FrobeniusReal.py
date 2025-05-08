import numpy as np
import logging
from typing import Any, Literal, Union, cast

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(InnerProductBase, "FrobeniusReal")
class FrobeniusReal(InnerProductBase):
    """
    Frobenius inner product implementation for real-valued matrices.
    
    This class implements the Frobenius inner product, which is defined as the sum
    of element-wise products of two matrices. For real matrices A and B, the
    Frobenius inner product is equivalent to Tr(A^T B), where Tr is the trace.
    
    Attributes
    ----------
    type : Literal["FrobeniusReal"]
        The type identifier for this inner product implementation
    """
    
    type: Literal["FrobeniusReal"] = "FrobeniusReal"
    
    def __init__(self) -> None:
        """
        Initialize the Frobenius inner product implementation for real matrices.
        
        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing FrobeniusReal inner product")
    
    def compute(self, mat1: Union[np.ndarray, list], mat2: Union[np.ndarray, list]) -> float:
        """
        Compute the Frobenius inner product between two real matrices.
        
        The Frobenius inner product is calculated as the sum of element-wise
        products of the two matrices.
        
        Parameters
        ----------
        mat1 : Union[np.ndarray, list]
            First matrix in the inner product
        mat2 : Union[np.ndarray, list]
            Second matrix in the inner product
            
        Returns
        -------
        float
            The resulting Frobenius inner product value
            
        Raises
        ------
        ValueError
            If the matrices are not compatible (different shapes) or contain complex values
        TypeError
            If the inputs are not arrays or lists convertible to arrays
        """
        # Ensure inputs are numpy arrays
        try:
            mat1_array = np.asarray(mat1, dtype=float)
            mat2_array = np.asarray(mat2, dtype=float)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to convert inputs to numpy arrays: {e}")
            raise TypeError("Inputs must be convertible to real-valued numpy arrays") from e
        
        # Check compatibility
        if not self.is_compatible(mat1_array, mat2_array):
            error_msg = f"Matrices are not compatible for Frobenius inner product: {mat1_array.shape} vs {mat2_array.shape}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Compute the Frobenius inner product
        try:
            # Calculate as sum of element-wise products (equivalent to Tr(A^T B))
            result = float(np.sum(mat1_array * mat2_array))
            self.logger.debug(f"Computed Frobenius inner product: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error computing Frobenius inner product: {e}")
            raise
    
    def is_compatible(self, vec1: Any, vec2: Any) -> bool:
        """
        Check if two matrices are compatible for Frobenius inner product calculation.
        
        Matrices are compatible if they:
        1. Are both numpy arrays or convertible to numpy arrays
        2. Have the same shape
        3. Contain only real values
        
        Parameters
        ----------
        vec1 : Any
            First matrix to check
        vec2 : Any
            Second matrix to check
            
        Returns
        -------
        bool
            True if the matrices are compatible, False otherwise
        """
        try:
            # Try to convert to numpy arrays
            mat1 = np.asarray(vec1, dtype=float)
            mat2 = np.asarray(vec2, dtype=float)
            
            # Check if shapes match
            if mat1.shape != mat2.shape:
                self.logger.debug(f"Matrix shapes don't match: {mat1.shape} vs {mat2.shape}")
                return False
            
            # Check if all values are real (not complex)
            if np.iscomplexobj(mat1) or np.iscomplexobj(mat2):
                self.logger.debug("Matrices contain complex values")
                return False
            
            return True
        except (ValueError, TypeError):
            self.logger.debug("Inputs cannot be converted to real-valued numpy arrays")
            return False