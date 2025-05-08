from typing import Any, List, Optional, Tuple, TypeVar, Union, Generic, Literal, Callable
import numpy as np
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.norms.INorm import T

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "SobolevNorm")
class SobolevNorm(NormBase):
    """
    Sobolev Norm implementation that combines function value norms with derivative norms.
    
    This norm measures both the size of a function and its derivatives, providing
    a measure of smoothness. It is particularly useful in applications where both
    the function values and how rapidly they change are important.
    
    Attributes
    ----------
    type : Literal["SobolevNorm"]
        Type identifier for the Sobolev norm
    weights : List[float]
        Weights for each derivative order, starting with the function itself (order 0)
    max_order : int
        Maximum derivative order to consider
    derivative_fn : Callable
        Function to compute derivatives of the input
    """
    type: Literal["SobolevNorm"] = "SobolevNorm"
    weights: List[float] = Field(default=[1.0, 1.0], description="Weights for each derivative order")
    max_order: int = Field(default=1, description="Maximum derivative order to consider")
    derivative_fn: Optional[Callable] = Field(default=None, 
                                             description="Function to compute derivatives")
    
    def __init__(self, **data: Any):
        """
        Initialize the Sobolev norm with specified parameters.
        
        Parameters
        ----------
        **data : Any
            Keyword arguments for configuring the norm
        """
        super().__init__(**data)
        # Ensure weights list has correct length
        if len(self.weights) != self.max_order + 1:
            logger.warning(f"Weights list length ({len(self.weights)}) doesn't match max_order+1 ({self.max_order+1}). Adjusting weights.")
            # Extend weights list if too short
            if len(self.weights) < self.max_order + 1:
                self.weights.extend([1.0] * (self.max_order + 1 - len(self.weights)))
            # Truncate weights list if too long
            else:
                self.weights = self.weights[:self.max_order + 1]
        
        # Set default derivative function if none provided
        if self.derivative_fn is None:
            self.derivative_fn = self._default_derivative_fn
            
        logger.info(f"Initialized SobolevNorm with max_order={self.max_order}, weights={self.weights}")
    
    def _default_derivative_fn(self, x: np.ndarray, order: int) -> np.ndarray:
        """
        Default function to compute derivatives using finite differences.
        
        Parameters
        ----------
        x : np.ndarray
            Input data
        order : int
            Derivative order to compute
            
        Returns
        -------
        np.ndarray
            Computed derivative of specified order
            
        Notes
        -----
        This is a simple implementation using finite differences.
        For more complex applications, a more sophisticated derivative
        computation may be needed.
        """
        if order == 0:
            return x
        
        # Simple finite difference for first derivative
        if order == 1:
            # Pad with zeros for consistent dimensions
            diff = np.zeros_like(x)
            if len(x) > 1:
                diff[:-1] = np.diff(x)
            return diff
        
        # For higher orders, recursively apply the derivative function
        return self._default_derivative_fn(self._default_derivative_fn(x, 1), order - 1)
    
    def compute(self, x: T) -> float:
        """
        Compute the Sobolev norm of a vector or function.
        
        The Sobolev norm combines the L2 norm of the function and its derivatives,
        weighted according to the specified weights.
        
        Parameters
        ----------
        x : T
            Vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The Sobolev norm value
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        if not isinstance(x, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected vector-like input, got {type(x)}")
        
        # Convert to numpy array for consistent handling
        x_array = np.asarray(x, dtype=float)
        
        if x_array.size == 0:
            logger.warning("Computing norm of empty array, returning 0.0")
            return 0.0
        
        # Compute weighted sum of squared L2 norms of function and its derivatives
        norm_squared = 0.0
        for order in range(self.max_order + 1):
            try:
                derivative = self.derivative_fn(x_array, order)
                # L2 norm squared of the derivative
                derivative_norm_sq = np.sum(np.square(derivative))
                # Add weighted contribution
                norm_squared += self.weights[order] * derivative_norm_sq
                
                logger.debug(f"Order {order} derivative norm contribution: {self.weights[order] * derivative_norm_sq}")
            except Exception as e:
                logger.error(f"Error computing derivative of order {order}: {str(e)}")
                raise ValueError(f"Failed to compute derivative of order {order}: {str(e)}")
        
        # Return square root for final norm value
        return np.sqrt(norm_squared)
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two vectors using the Sobolev norm.
        
        Parameters
        ----------
        x : T
            First vector
        y : T
            Second vector
            
        Returns
        -------
        float
            The Sobolev distance between x and y
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        if not isinstance(x, (list, tuple, np.ndarray)) or not isinstance(y, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected vector-like inputs, got {type(x)} and {type(y)}")
        
        # Convert to numpy arrays
        x_array = np.asarray(x, dtype=float)
        y_array = np.asarray(y, dtype=float)
        
        # Check for compatible dimensions
        if x_array.shape != y_array.shape:
            raise ValueError(f"Incompatible dimensions: {x_array.shape} vs {y_array.shape}")
        
        # Compute the Sobolev norm of the difference
        return self.compute(x_array - y_array)
    
    def normalize(self, x: T) -> T:
        """
        Normalize a vector to have unit Sobolev norm.
        
        Parameters
        ----------
        x : T
            Vector to normalize
            
        Returns
        -------
        T
            Normalized vector with the same direction as x but unit Sobolev norm
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        if not isinstance(x, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected vector-like input, got {type(x)}")
        
        # Convert to numpy array for consistent handling
        x_array = np.asarray(x, dtype=float)
        
        norm_value = self.compute(x_array)
        
        if np.isclose(norm_value, 0.0):
            raise ValueError("Cannot normalize a zero vector")
        
        # Return the normalized vector in the same format as the input
        normalized = x_array / norm_value
        
        # Convert back to original type if needed
        if isinstance(x, list):
            return normalized.tolist()
        elif isinstance(x, tuple):
            return tuple(normalized.tolist())
        
        return normalized
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit Sobolev norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's Sobolev norm is within tolerance of 1.0, False otherwise
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        if not isinstance(x, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected vector-like input, got {type(x)}")
        
        norm_value = self.compute(x)
        return abs(norm_value - 1.0) <= tolerance
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this Sobolev norm
        """
        return f"SobolevNorm(max_order={self.max_order}, weights={self.weights})"
    
    def set_derivative_function(self, func: Callable) -> None:
        """
        Set a custom derivative computation function.
        
        Parameters
        ----------
        func : Callable
            A function that takes an array and an order parameter and returns
            the derivative of that order
            
        Returns
        -------
        None
        """
        self.derivative_fn = func
        logger.info("Custom derivative function set")
    
    def set_weights(self, weights: List[float]) -> None:
        """
        Set new weights for the different derivative orders.
        
        Parameters
        ----------
        weights : List[float]
            List of weights for each derivative order, starting with order 0
            
        Returns
        -------
        None
            
        Raises
        ------
        ValueError
            If weights list length doesn't match max_order+1
        """
        if len(weights) != self.max_order + 1:
            raise ValueError(f"Weights list must have length {self.max_order + 1}")
        
        self.weights = weights
        logger.info(f"Weights updated to {weights}")