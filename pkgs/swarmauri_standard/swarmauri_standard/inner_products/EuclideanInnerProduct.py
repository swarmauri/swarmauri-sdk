from typing import Any, List, Tuple, Union, Literal, overload
import logging
import numpy as np
from numpy.typing import ArrayLike, NDArray

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    """
    Euclidean Inner Product implementation for real-valued vectors.
    
    This class provides an implementation of the standard dot product used in
    Euclidean geometry for real vector spaces. It computes the L2 inner product
    between two real-valued, finite-dimensional vectors.
    
    Attributes
    ----------
    type : Literal["EuclideanInnerProduct"]
        Type identifier for this inner product implementation
    """
    
    type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"
    
    def __init__(self) -> None:
        """
        Initialize the Euclidean inner product implementation.
        
        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing EuclideanInnerProduct")
    
    @overload
    def compute(self, vec1: List[float], vec2: List[float]) -> float: ...
    
    @overload
    def compute(self, vec1: Tuple[float, ...], vec2: Tuple[float, ...]) -> float: ...
    
    @overload
    def compute(self, vec1: NDArray[np.float_], vec2: NDArray[np.float_]) -> float: ...
    
    def compute(self, vec1: Union[List[float], Tuple[float, ...], NDArray[np.float_]], 
                vec2: Union[List[float], Tuple[float, ...], NDArray[np.float_]]) -> float:
        """
        Compute the Euclidean inner product (dot product) between two vectors.
        
        This method computes the standard dot product between two real-valued vectors:
        <vec1, vec2> = sum(vec1[i] * vec2[i]) for all i
        
        Parameters
        ----------
        vec1 : Union[List[float], Tuple[float, ...], NDArray[np.float_]]
            First vector in the inner product
        vec2 : Union[List[float], Tuple[float, ...], NDArray[np.float_]]
            Second vector in the inner product
            
        Returns
        -------
        float
            The resulting inner product value
            
        Raises
        ------
        ValueError
            If the vectors have different dimensions or contain non-finite values
        TypeError
            If the vectors are not of supported types
        """
        self.logger.debug(f"Computing Euclidean inner product between vectors of types {type(vec1)} and {type(vec2)}")
        
        # Check if vectors are compatible before computation
        if not self.is_compatible(vec1, vec2):
            error_msg = f"Vectors are not compatible for Euclidean inner product: {vec1}, {vec2}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Convert inputs to numpy arrays for consistent handling
        try:
            vec1_array = np.asarray(vec1, dtype=float)
            vec2_array = np.asarray(vec2, dtype=float)
        except (ValueError, TypeError) as e:
            error_msg = f"Failed to convert vectors to numpy arrays: {e}"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Compute the dot product
        try:
            # Use numpy's dot product for efficient computation
            result = float(np.dot(vec1_array, vec2_array))
            self.logger.debug(f"Computed inner product: {result}")
            return result
        except Exception as e:
            error_msg = f"Error computing Euclidean inner product: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def is_compatible(self, vec1: Any, vec2: Any) -> bool:
        """
        Check if two vectors are compatible for Euclidean inner product calculation.
        
        Vectors are compatible if:
        1. Both are of supported types (lists, tuples, or numpy arrays)
        2. Both have the same dimension
        3. All elements are real numbers (finite floats)
        
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
        self.logger.debug(f"Checking compatibility of vectors for Euclidean inner product")
        
        # Check if vectors are of supported types
        supported_types = (list, tuple, np.ndarray)
        if not (isinstance(vec1, supported_types) and isinstance(vec2, supported_types)):
            self.logger.debug(f"Incompatible types: {type(vec1)} and {type(vec2)}")
            return False
        
        # Try to convert to numpy arrays
        try:
            vec1_array = np.asarray(vec1, dtype=float)
            vec2_array = np.asarray(vec2, dtype=float)
        except (ValueError, TypeError):
            self.logger.debug("Failed to convert vectors to numpy arrays")
            return False
        
        # Check for same dimensions
        if vec1_array.shape != vec2_array.shape:
            self.logger.debug(f"Vectors have different shapes: {vec1_array.shape} vs {vec2_array.shape}")
            return False
        
        # Check if vectors are 1D
        if len(vec1_array.shape) != 1:
            self.logger.debug(f"Vectors must be 1-dimensional, got shape {vec1_array.shape}")
            return False
        
        # Check if all elements are finite
        if not (np.isfinite(vec1_array).all() and np.isfinite(vec2_array).all()):
            self.logger.debug("Vectors contain non-finite values")
            return False
        
        self.logger.debug("Vectors are compatible for Euclidean inner product")
        return True