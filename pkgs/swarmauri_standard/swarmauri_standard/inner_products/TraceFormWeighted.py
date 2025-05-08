import logging
import numpy as np
from typing import Literal, Optional, Union, Any

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(InnerProductBase, "TraceFormWeighted")
class TraceFormWeighted(InnerProductBase):
    """
    Inner product implementation using weighted trace of matrix product.
    
    This class implements an inner product where the inner product of two matrices
    is calculated as the trace of their product, modulated by an external weight matrix.
    The formula is: <A, B>_W = trace(A @ W @ B.T)
    
    Attributes
    ----------
    type : Literal["TraceFormWeighted"]
        The type identifier for this inner product implementation
    weight_matrix : Optional[np.ndarray]
        The weight matrix used to modulate the trace calculation
    """
    
    type: Literal["TraceFormWeighted"] = "TraceFormWeighted"
    weight_matrix: Optional[np.ndarray] = None
    
    def __init__(self, weight_matrix: Optional[np.ndarray] = None) -> None:
        """
        Initialize the weighted trace form inner product.
        
        Parameters
        ----------
        weight_matrix : Optional[np.ndarray], default=None
            The weight matrix to use for modulating the trace calculation.
            If None, an identity matrix will be used effectively making this
            equivalent to a standard trace form inner product.
        """
        super().__init__()
        self.weight_matrix = weight_matrix
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing TraceFormWeighted inner product")
    
    def compute(self, vec1: Union[np.ndarray, Any], vec2: Union[np.ndarray, Any]) -> float:
        """
        Compute the weighted trace inner product between two matrices.
        
        Calculates <vec1, vec2>_W = trace(vec1 @ W @ vec2.T) where W is the weight matrix.
        
        Parameters
        ----------
        vec1 : np.ndarray
            First matrix in the inner product
        vec2 : np.ndarray
            Second matrix in the inner product
            
        Returns
        -------
        float
            The resulting weighted trace inner product value
            
        Raises
        ------
        ValueError
            If the matrices are incompatible for inner product calculation
        TypeError
            If the inputs are not numpy arrays
        """
        if not self.is_compatible(vec1, vec2):
            self.logger.error("Incompatible matrices for weighted trace inner product")
            raise ValueError("Matrices must be compatible for weighted trace inner product calculation")
        
        try:
            # If weight_matrix is None, use identity matrix (standard trace inner product)
            if self.weight_matrix is None:
                # For efficiency, we can directly compute trace(vec1 @ vec2.T) without creating identity matrix
                result = np.trace(vec1 @ vec2.T)
            else:
                # Calculate trace(vec1 @ W @ vec2.T)
                result = np.trace(vec1 @ self.weight_matrix @ vec2.T)
            
            self.logger.debug(f"Computed weighted trace inner product: {result}")
            return float(result)
        except Exception as e:
            self.logger.error(f"Error computing weighted trace inner product: {str(e)}")
            raise
    
    def is_compatible(self, vec1: Union[np.ndarray, Any], vec2: Union[np.ndarray, Any]) -> bool:
        """
        Check if two matrices are compatible for weighted trace inner product calculation.
        
        For matrices to be compatible:
        1. Both must be numpy arrays
        2. Both must be 2D matrices
        3. The shapes must be compatible with the weight matrix
        
        Parameters
        ----------
        vec1 : np.ndarray
            First matrix to check
        vec2 : np.ndarray
            Second matrix to check
            
        Returns
        -------
        bool
            True if the matrices are compatible, False otherwise
        """
        # Check if inputs are numpy arrays
        if not isinstance(vec1, np.ndarray) or not isinstance(vec2, np.ndarray):
            self.logger.warning("Inputs must be numpy arrays")
            return False
        
        # Check if inputs are 2D matrices
        if vec1.ndim != 2 or vec2.ndim != 2:
            self.logger.warning("Inputs must be 2D matrices")
            return False
        
        # Check shape compatibility
        if vec1.shape != vec2.shape:
            self.logger.warning(f"Matrix shapes do not match: {vec1.shape} vs {vec2.shape}")
            return False
        
        # Check compatibility with weight matrix if it exists
        if self.weight_matrix is not None:
            if not isinstance(self.weight_matrix, np.ndarray) or self.weight_matrix.ndim != 2:
                self.logger.warning("Weight matrix must be a 2D numpy array")
                return False
            
            # For trace(vec1 @ W @ vec2.T) to work:
            # vec1 shape: (m, n), W shape: (n, p), vec2.T shape: (p, m)
            # So W should be (n, n) if vec1 and vec2 are (m, n)
            if vec1.shape[1] != self.weight_matrix.shape[0] or self.weight_matrix.shape[1] != vec2.shape[1]:
                self.logger.warning(
                    f"Weight matrix shape {self.weight_matrix.shape} is incompatible with "
                    f"input matrices of shape {vec1.shape}"
                )
                return False
        
        return True
    
    def set_weight_matrix(self, weight_matrix: np.ndarray) -> None:
        """
        Set or update the weight matrix used in the inner product calculation.
        
        Parameters
        ----------
        weight_matrix : np.ndarray
            The new weight matrix to use
            
        Raises
        ------
        TypeError
            If weight_matrix is not a numpy array
        ValueError
            If weight_matrix is not a 2D matrix
        """
        if not isinstance(weight_matrix, np.ndarray):
            self.logger.error("Weight matrix must be a numpy array")
            raise TypeError("Weight matrix must be a numpy array")
        
        if weight_matrix.ndim != 2:
            self.logger.error("Weight matrix must be a 2D matrix")
            raise ValueError("Weight matrix must be a 2D matrix")
        
        self.weight_matrix = weight_matrix
        self.logger.info(f"Updated weight matrix to shape {weight_matrix.shape}")
    
    def get_weight_matrix(self) -> Optional[np.ndarray]:
        """
        Get the current weight matrix.
        
        Returns
        -------
        Optional[np.ndarray]
            The current weight matrix or None if not set
        """
        return self.weight_matrix