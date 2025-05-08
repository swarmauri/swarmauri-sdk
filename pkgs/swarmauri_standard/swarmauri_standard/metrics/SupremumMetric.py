from typing import TypeVar, Generic, Literal, Any, List, Union, Optional
import logging
import numpy as np
from pydantic import Field

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Type variable for generic implementation
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    Supremum (L∞) metric implementation that measures the maximum absolute difference
    between corresponding components of two vectors.
    
    This metric calculates the distance as the maximum absolute difference between
    corresponding elements of two vectors, making it suitable for bounded vector spaces.
    
    Attributes
    ----------
    type : Literal["SupremumMetric"]
        The type identifier for this metric
    """
    type: Literal["SupremumMetric"] = "SupremumMetric"
    
    def distance(self, x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> float:
        """
        Calculate the supremum (L∞) distance between two vectors.
        
        The supremum distance is the maximum absolute difference between 
        corresponding components of the input vectors.
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            First vector
        y : Union[List[float], np.ndarray]
            Second vector
            
        Returns
        -------
        float
            The supremum distance between x and y
            
        Raises
        ------
        ValueError
            If inputs have different dimensions or are not valid vectors
        """
        try:
            # Convert inputs to numpy arrays for efficient computation
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)
            
            # Validate dimensions
            if x_array.shape != y_array.shape:
                error_msg = f"Input vectors must have the same dimensions: x {x_array.shape} vs y {y_array.shape}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Calculate the maximum absolute difference (L∞ norm)
            result = np.max(np.abs(x_array - y_array))
            
            logger.debug(f"Calculated supremum distance between {x} and {y}: {result}")
            return float(result)
            
        except Exception as e:
            if not isinstance(e, ValueError):  # Don't log twice for our own ValueError
                logger.error(f"Error calculating supremum distance: {str(e)}")
            raise
    
    def are_identical(self, x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> bool:
        """
        Check if two vectors are identical according to the supremum metric.
        
        Two vectors are identical under this metric if their supremum distance is zero,
        meaning all corresponding components are equal.
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            First vector
        y : Union[List[float], np.ndarray]
            Second vector
            
        Returns
        -------
        bool
            True if the vectors are identical (supremum distance is zero), False otherwise
        """
        try:
            # Use a small epsilon to account for floating-point precision issues
            epsilon = 1e-10
            distance_value = self.distance(x, y)
            are_same = distance_value < epsilon
            
            logger.debug(f"Checking if {x} and {y} are identical: {are_same} (distance: {distance_value})")
            return are_same
            
        except Exception as e:
            logger.error(f"Error checking vector identity: {str(e)}")
            return False
    
    def validate_inputs(self, x: Any, y: Any) -> bool:
        """
        Validate that the inputs are valid for this metric calculation.
        
        Parameters
        ----------
        x : Any
            First input to validate
        y : Any
            Second input to validate
            
        Returns
        -------
        bool
            True if inputs are valid, False otherwise
        """
        try:
            # Try to convert to numpy arrays
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)
            
            # Check that they have the same shape
            if x_array.shape != y_array.shape:
                logger.warning(f"Input vectors have different shapes: {x_array.shape} vs {y_array.shape}")
                return False
            
            # Check that they are at least 1D arrays
            if x_array.ndim < 1:
                logger.warning(f"Input must be at least a 1D vector, got {x_array.ndim}D")
                return False
                
            return True
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid inputs for supremum metric: {str(e)}")
            return False