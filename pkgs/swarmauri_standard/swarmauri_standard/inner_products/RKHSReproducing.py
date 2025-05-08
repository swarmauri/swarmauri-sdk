from typing import Any, Literal, TypeVar, Callable, Union, Optional
import logging
import numpy as np

from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_base.ComponentBase import ComponentBase

T = TypeVar('T')

@ComponentBase.register_type(InnerProductBase, "RKHSReproducing")
class RKHSReproducing(InnerProductBase):
    """
    Inner product implementation for Reproducing Kernel Hilbert Space (RKHS).
    
    This class induces an inner product in a Reproducing Kernel Hilbert Space
    via kernel evaluation. The kernel must be positive-definite to ensure
    the inner product properties are satisfied.
    
    Attributes
    ----------
    type : Literal["RKHSReproducing"]
        Type identifier for this inner product implementation
    kernel_func : Callable[[T, T], float]
        The kernel function that defines the inner product
    """
    
    type: Literal["RKHSReproducing"] = "RKHSReproducing"
    
    def __init__(self, kernel_func: Optional[Callable[[Any, Any], float]] = None) -> None:
        """
        Initialize the RKHS inner product with a kernel function.
        
        Parameters
        ----------
        kernel_func : Optional[Callable[[Any, Any], float]], optional
            The kernel function that defines the inner product. If None, defaults to
            a radial basis function (RBF) kernel with gamma=1.0.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing RKHSReproducing inner product")
        
        # Default to RBF kernel if none provided
        if kernel_func is None:
            self.kernel_func = self._default_rbf_kernel
            self.logger.info("Using default RBF kernel with gamma=1.0")
        else:
            self.kernel_func = kernel_func
            self.logger.info("Using custom kernel function")
    
    def _default_rbf_kernel(self, x: Any, y: Any, gamma: float = 1.0) -> float:
        """
        Default RBF (Gaussian) kernel implementation.
        
        Parameters
        ----------
        x : Any
            First input, expected to be convertible to numpy array
        y : Any
            Second input, expected to be convertible to numpy array
        gamma : float, optional
            Kernel bandwidth parameter, by default 1.0
            
        Returns
        -------
        float
            Kernel evaluation k(x, y)
        """
        try:
            x_array = np.asarray(x, dtype=np.float64)
            y_array = np.asarray(y, dtype=np.float64)
            return np.exp(-gamma * np.sum((x_array - y_array) ** 2))
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error in RBF kernel calculation: {e}")
            raise ValueError(f"Inputs must be convertible to numpy arrays: {e}")
    
    def compute(self, vec1: T, vec2: T) -> float:
        """
        Compute the inner product between two vectors using the kernel function.
        
        Parameters
        ----------
        vec1 : T
            First vector in the inner product
        vec2 : T
            Second vector in the inner product
            
        Returns
        -------
        float
            The resulting inner product value (kernel evaluation)
            
        Raises
        ------
        ValueError
            If the vectors are incompatible for inner product calculation
        """
        if not self.is_compatible(vec1, vec2):
            error_msg = f"Incompatible vectors for RKHS inner product: {type(vec1)} and {type(vec2)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            result = self.kernel_func(vec1, vec2)
            # Ensure the result is a float
            if not isinstance(result, (int, float)):
                self.logger.warning(f"Kernel function returned non-scalar value: {result}")
                result = float(result)
            return result
        except Exception as e:
            self.logger.error(f"Error computing kernel inner product: {e}")
            raise ValueError(f"Failed to compute kernel inner product: {e}")
    
    def is_compatible(self, vec1: T, vec2: T) -> bool:
        """
        Check if two vectors are compatible for kernel-based inner product calculation.
        
        This method attempts to evaluate the kernel function on the inputs to determine
        if they are compatible.
        
        Parameters
        ----------
        vec1 : T
            First vector to check
        vec2 : T
            Second vector to check
            
        Returns
        -------
        bool
            True if the vectors are compatible with the kernel function, False otherwise
        """
        try:
            # Try to compute the kernel and check if the result is a scalar
            result = self.kernel_func(vec1, vec2)
            return isinstance(result, (int, float)) or (
                hasattr(result, "shape") and result.shape == () or 
                hasattr(result, "__len__") and len(result) == 1
            )
        except Exception as e:
            self.logger.debug(f"Vectors are incompatible for kernel evaluation: {e}")
            return False
    
    def set_kernel(self, kernel_func: Callable[[Any, Any], float]) -> None:
        """
        Set a new kernel function for the inner product.
        
        Parameters
        ----------
        kernel_func : Callable[[Any, Any], float]
            The new kernel function to use
        """
        self.logger.info("Setting new kernel function")
        self.kernel_func = kernel_func
    
    def is_positive_definite(self, data_points: list[Any], tol: float = 1e-10) -> bool:
        """
        Check if the kernel is positive definite on the given data points.
        
        A kernel is positive definite if the Gram matrix is positive definite,
        which means all eigenvalues are positive.
        
        Parameters
        ----------
        data_points : list[Any]
            List of data points to check positive definiteness on
        tol : float, optional
            Tolerance for eigenvalues, by default 1e-10
            
        Returns
        -------
        bool
            True if the kernel is positive definite, False otherwise
        """
        n = len(data_points)
        if n == 0:
            self.logger.warning("No data points provided to check positive definiteness")
            return True
        
        try:
            # Construct the Gram matrix
            gram_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    gram_matrix[i, j] = self.compute(data_points[i], data_points[j])
            
            # Check if the matrix is symmetric
            if not np.allclose(gram_matrix, gram_matrix.T):
                self.logger.warning("Gram matrix is not symmetric")
                return False
            
            # Compute eigenvalues
            eigenvalues = np.linalg.eigvalsh(gram_matrix)
            
            # Check if all eigenvalues are positive (within tolerance)
            is_pd = np.all(eigenvalues > -tol)
            
            if not is_pd:
                self.logger.warning(f"Kernel is not positive definite. Min eigenvalue: {np.min(eigenvalues)}")
            
            return is_pd
            
        except Exception as e:
            self.logger.error(f"Error checking positive definiteness: {e}")
            return False